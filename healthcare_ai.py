import json
import re

import _snowflake
import pandas as pd
import streamlit as st
from snowflake.snowpark.context import get_active_session


# ============================================================
# CONFIGURATION
# ============================================================

DATABASE = "HEALTHCARE_CLAIMS_DB"
SCHEMA = "GOLD"
STAGE = "CORTEX_SEMANTIC_STAGE"
FILE = "healthcare_claims_semantic_model.yaml"

SEMANTIC_MODEL_FILE = f"@{DATABASE}.{SCHEMA}.{STAGE}/{FILE}"

ANALYST_ENDPOINT = "/api/v2/cortex/analyst/message"
API_TIMEOUT_MS = 50000


# ============================================================
# EXAMPLE QUESTIONS
# ============================================================

EXAMPLE_QUESTIONS = [
    "How many claims are there?",
    "Show claim count for each provider type.",
    "Show claim count for each year.",
    "What is the denial percentage?",
    "Show total claim amount for each year.",
    "Show claim count by gender.",
    "Show claim count for each denial reason.",
    "What is the total insurance payment?",
]


# ============================================================
# SNOWFLAKE SESSION
# ============================================================

session = get_active_session()


# ============================================================
# STREAMLIT PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Healthcare Claims Analyst",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 950px;
    }

    .app-subtitle {
        color: #6b7280;
        font-size: 0.95rem;
        margin-top: -0.6rem;
        margin-bottom: 1.2rem;
    }

    .stButton button {
        border-radius: 8px;
    }

    div[data-testid="stChatMessage"] {
        padding: 0.5rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# PAGE HEADER
# ============================================================

st.title("🏥 Healthcare Claims Analyst")

st.markdown(
    "Ask questions about claims, payments, denials, providers, "
    "beneficiaries, diagnoses, and dates — in plain English."
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "suggestions" not in st.session_state:
    st.session_state.suggestions = []

if "pending_question" not in st.session_state:
    st.session_state.pending_question = None


# ============================================================
# RESET CONVERSATION
# ============================================================

def reset_conversation():
    st.session_state.messages = []
    st.session_state.suggestions = []
    st.session_state.pending_question = None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("🏥 Healthcare Claims")

    st.caption("Semantic model")

    st.code(FILE, language=None)

    st.divider()

    st.button(
        "🗑️ New Conversation",
        use_container_width=True,
        on_click=reset_conversation,
    )

    st.divider()

    st.subheader("💡 Example questions")

    for i, question in enumerate(EXAMPLE_QUESTIONS):

        if st.button(
            question,
            key=f"example_{i}",
            use_container_width=True,
        ):
            st.session_state.pending_question = question
            st.rerun()

    st.divider()

    st.caption("Powered by Snowflake Cortex Analyst")

    with st.expander("🐛 Debug: session context"):

        try:

            ctx = session.sql(
                """
                SELECT
                    CURRENT_ROLE() AS ROLE,
                    CURRENT_WAREHOUSE() AS WAREHOUSE,
                    CURRENT_DATABASE() AS DATABASE,
                    CURRENT_SCHEMA() AS SCHEMA
                """
            ).collect()[0]

            st.write(dict(ctx.as_dict()))

        except Exception as e:

            st.write(f"Could not fetch context: {e}")


# ============================================================
# SEND MESSAGE TO CORTEX ANALYST
# ============================================================

def send_message(history):

    if not history:
        raise RuntimeError(
            "Conversation history cannot be empty."
        )

    if history[-1]["role"] != "user":
        raise RuntimeError(
            "Invalid conversation state: last message must be from the user."
        )

    request_body = {
        "messages": history,
        "semantic_model_file": SEMANTIC_MODEL_FILE,
    }

    response = _snowflake.send_snow_api_request(
        "POST",
        ANALYST_ENDPOINT,
        {},
        {},
        request_body,
        {},
        API_TIMEOUT_MS,
    )

    if response["status"] >= 400:

        raise RuntimeError(
            f"Cortex Analyst request failed "
            f"(HTTP {response['status']}): "
            f"{response.get('content')}"
        )

    return json.loads(response["content"])


# ============================================================
# EXTRACT ANALYST CONTENT
# ============================================================

def extract_content(response_json):

    return response_json.get(
        "message",
        {}
    ).get(
        "content",
        []
    )


# ============================================================
# EXTRACT SUGGESTIONS
# ============================================================

def extract_suggestions(content):

    suggestions = []

    for item in content:

        item_type = item.get("type")

        if item_type == "suggestions":

            suggestions.extend(
                item.get("suggestions", [])
            )

        elif item_type == "suggestion":

            text = item.get("text")

            if text:
                suggestions.append(text)

    seen = set()
    unique = []

    for suggestion in suggestions:

        if suggestion not in seen:

            seen.add(suggestion)
            unique.append(suggestion)

    return unique


# ============================================================
# REPAIR GENERATED CLAIM ID SQL
# ============================================================

def repair_claim_id_sql(sql):
    """
    Repairs a known Cortex Analyst SQL alias issue.

    Example generated SQL:

        WITH claims AS (
            SELECT
                CLM_ID AS CLAIM_ID
            FROM FACT_CLAIMS
        )
        SELECT
            COUNT(DISTINCT CLM_ID)
        FROM claims;

    CLM_ID is not available outside the CTE because the CTE
    exposes the column as CLAIM_ID.

    This function changes the outer reference to CLAIM_ID.
    """

    if not sql:
        return sql

    repaired = sql

    # --------------------------------------------------------
    # Pattern 1:
    #
    # COUNT(DISTINCT fc.clm_id)
    #
    # becomes
    #
    # COUNT(DISTINCT fc.claim_id)
    # --------------------------------------------------------

    repaired = re.sub(
        r"COUNT\s*\(\s*DISTINCT\s+fc\.clm_id\s*\)",
        "COUNT(DISTINCT fc.claim_id)",
        repaired,
        flags=re.IGNORECASE,
    )

    # --------------------------------------------------------
    # Pattern 2:
    #
    # COUNT(DISTINCT clm_id)
    #
    # becomes
    #
    # COUNT(DISTINCT claim_id)
    # --------------------------------------------------------

    repaired = re.sub(
        r"COUNT\s*\(\s*DISTINCT\s+clm_id\s*\)",
        "COUNT(DISTINCT claim_id)",
        repaired,
        flags=re.IGNORECASE,
    )

    # --------------------------------------------------------
    # Pattern 3:
    #
    # fc.clm_id
    #
    # becomes
    #
    # fc.claim_id
    #
    # Only replace when it is used in a COUNT DISTINCT
    # expression to avoid unnecessarily changing valid SQL.
    # --------------------------------------------------------

    repaired = re.sub(
        r"(COUNT\s*\(\s*DISTINCT\s+)fc\.clm_id",
        r"\1fc.claim_id",
        repaired,
        flags=re.IGNORECASE,
    )

    return repaired


# ============================================================
# EXECUTE SQL
# ============================================================

def execute_sql(sql):

    if not sql:
        return pd.DataFrame()

    try:

        rows = session.sql(sql).collect()

        if rows:

            return pd.DataFrame(
                [row.as_dict() for row in rows]
            )

        return pd.DataFrame()

    except Exception as first_error:

        error_text = str(first_error)

        # ----------------------------------------------------
        # Retry only for known CLM_ID / CLAIM_ID issue
        # ----------------------------------------------------

        if (
            "invalid identifier" in error_text.lower()
            and "clm_id" in error_text.lower()
        ):

            repaired_sql = repair_claim_id_sql(sql)

            if repaired_sql != sql:

                try:

                    rows = session.sql(
                        repaired_sql
                    ).collect()

                    st.info(
                        "ℹ️ Cortex Analyst generated a "
                        "CLM_ID/CLAIM_ID alias mismatch. "
                        "The generated SQL was repaired before execution."
                    )

                    if rows:

                        return pd.DataFrame(
                            [row.as_dict() for row in rows]
                        )

                    return pd.DataFrame()

                except Exception as repaired_error:

                    st.error(
                        "Unable to execute the repaired SQL."
                    )

                    st.exception(
                        repaired_error
                    )

                    return None

        st.error(
            "Unable to execute the generated SQL."
        )

        st.exception(
            first_error
        )

        return None


# ============================================================
# FORMAT DATAFRAME
# ============================================================

def format_dataframe(df):

    if df is None:
        return df

    output = df.copy()

    new_columns = []
    seen = {}

    for column in output.columns:

        column = str(column)

        if column not in seen:

            seen[column] = 0
            new_columns.append(column)

        else:

            seen[column] += 1

            new_columns.append(
                f"{column}_{seen[column]}"
            )

    output.columns = [
        str(column)
        .replace("_", " ")
        .title()
        for column in new_columns
    ]

    return output


# ============================================================
# DISPLAY CHART
# ============================================================

def display_chart(df):

    if df is None:
        return

    if df.empty:
        return

    if len(df.columns) < 2:
        return

    numeric_positions = []

    for position in range(
        len(df.columns)
    ):

        series = df.iloc[:, position]

        if pd.api.types.is_numeric_dtype(series):

            numeric_positions.append(
                position
            )

    if not numeric_positions:

        st.info(
            "No numeric measure available for charting."
        )

        return

    # First column becomes category
    x_series = df.iloc[:, 0]

    # First numeric column becomes value
    y_series = df.iloc[
        :,
        numeric_positions[0]
    ]

    chart_df = pd.DataFrame(
        {
            "category": x_series,
            "value": pd.to_numeric(
                y_series,
                errors="coerce",
            ),
        }
    )

    chart_df = chart_df.dropna(
        subset=[
            "category",
            "value",
        ]
    )

    if chart_df.empty:

        st.info(
            "No valid data available for charting."
        )

        return

    if len(chart_df) > 30:

        st.info(
            "Chart is hidden because the result "
            "contains more than 30 rows."
        )

        return

    chart_df = chart_df.set_index(
        "category"
    )

    st.bar_chart(
        chart_df["value"],
        use_container_width=True,
    )


# ============================================================
# DISPLAY ANALYST CONTENT
# ============================================================

def display_content(content):

    sql_statement = None

    # --------------------------------------------------------
    # Extract text and SQL from Cortex response
    # --------------------------------------------------------

    for item in content:

        item_type = item.get("type")

        if (
            item_type == "text"
            and item.get("text")
        ):

            st.markdown(
                item["text"]
            )

        elif item_type == "sql":

            sql_statement = item.get(
                "statement"
            )

    # --------------------------------------------------------
    # No SQL returned
    # --------------------------------------------------------

    if not sql_statement:
        return

    # --------------------------------------------------------
    # Repair generated SQL before execution
    # --------------------------------------------------------

    executed_sql = repair_claim_id_sql(
        sql_statement
    )

    if executed_sql != sql_statement:

        st.info(
            "ℹ️ The generated SQL contained a "
            "CLM_ID/CLAIM_ID alias mismatch. "
            "The SQL was corrected before execution."
        )

    # --------------------------------------------------------
    # Execute SQL
    # --------------------------------------------------------

    df = execute_sql(
        executed_sql
    )

    # --------------------------------------------------------
    # SQL execution failed
    # --------------------------------------------------------

    if df is None:

        with st.expander(
            "🔍 View generated SQL (failed)",
            expanded=True,
        ):

            st.caption(
                f"Length: {len(sql_statement)} chars · "
                f"{sql_statement.count(chr(10)) + 1} lines"
            )

            numbered_sql = "\n".join(
                f"{i + 1:>3}: {line}"
                for i, line in enumerate(
                    sql_statement.split("\n")
                )
            )

            st.code(
                numbered_sql,
                language="sql",
            )

        return

    # --------------------------------------------------------
    # Empty result
    # --------------------------------------------------------

    if df.empty:

        st.info(
            "The query returned no rows."
        )

        with st.expander(
            "🔍 View generated SQL"
        ):

            st.code(
                executed_sql,
                language="sql",
            )

        return

    # --------------------------------------------------------
    # Format dataframe
    # --------------------------------------------------------

    display_df = format_dataframe(
        df
    )

    # --------------------------------------------------------
    # Multiple rows
    # --------------------------------------------------------

    if len(df) > 1:

        tab_data, tab_chart, tab_sql = st.tabs(
            [
                "📋 Data",
                "📊 Chart",
                "🔍 SQL",
            ]
        )

        with tab_data:

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
            )

        with tab_chart:

            try:

                display_chart(
                    df
                )

            except Exception as chart_error:

                st.warning(
                    "Unable to render the chart "
                    "for this result."
                )

                st.caption(
                    str(chart_error)
                )

        with tab_sql:

            st.code(
                executed_sql,
                language="sql",
            )

    # --------------------------------------------------------
    # Single row
    # --------------------------------------------------------

    else:

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
        )

        with st.expander(
            "🔍 View generated SQL"
        ):

            st.code(
                executed_sql,
                language="sql",
            )


# ============================================================
# DISPLAY FOLLOW-UP SUGGESTIONS
# ============================================================

def display_suggestions():

    suggestions = st.session_state.suggestions

    if not suggestions:
        return

    st.markdown(
        "**💡 Suggested follow-up questions**"
    )

    number_of_suggestions = min(
        len(suggestions),
        3,
    )

    columns = st.columns(
        number_of_suggestions
    )

    for i, suggestion in enumerate(
        suggestions
    ):

        with columns[i % number_of_suggestions]:

            if st.button(
                suggestion,
                key=(
                    f"followup_"
                    f"{len(st.session_state.messages)}_"
                    f"{i}"
                ),
                use_container_width=True,
            ):

                st.session_state.pending_question = (
                    suggestion
                )

                st.rerun()


# ============================================================
# PROCESS QUESTION
# ============================================================

def process_question(question):

    question = question.strip()

    if not question:
        return

    # --------------------------------------------------------
    # Clear previous suggestions
    # --------------------------------------------------------

    st.session_state.suggestions = []

    # --------------------------------------------------------
    # Add user message
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": question,
                }
            ],
        }
    )

    try:

        with st.spinner(
            "🔎 Analyzing your question..."
        ):

            response = send_message(
                st.session_state.messages
            )

        # ----------------------------------------------------
        # Extract analyst response
        # ----------------------------------------------------

        analyst_content = extract_content(
            response
        )

        if not analyst_content:

            raise RuntimeError(
                "Cortex Analyst returned "
                "an empty response."
            )

        # ----------------------------------------------------
        # Save analyst response
        # ----------------------------------------------------

        st.session_state.messages.append(
            {
                "role": "analyst",
                "content": analyst_content,
            }
        )

        # ----------------------------------------------------
        # Extract suggestions
        # ----------------------------------------------------

        st.session_state.suggestions = (
            extract_suggestions(
                analyst_content
            )
        )

        # ----------------------------------------------------
        # Display response
        # ----------------------------------------------------

        display_content(
            analyst_content
        )

        display_suggestions()

    except Exception as error:

        # Remove failed user message
        if (
            st.session_state.messages
            and st.session_state.messages[-1]["role"]
            == "user"
        ):

            st.session_state.messages.pop()

        st.error(
            "❌ Something went wrong."
        )

        st.exception(
            error
        )


# ============================================================
# DISPLAY EXISTING CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    role = message["role"]

    if role == "user":

        with st.chat_message(
            "user",
            avatar="👤",
        ):

            for item in message["content"]:

                if item.get("type") == "text":

                    st.markdown(
                        item.get(
                            "text",
                            "",
                        )
                    )

    elif role == "analyst":

        with st.chat_message(
            "assistant",
            avatar="🤖",
        ):

            display_content(
                message["content"]
            )


# ============================================================
# WELCOME SCREEN
# ============================================================

if not st.session_state.messages:

    st.markdown(
        "##### Try asking:"
    )

    columns = st.columns(2)

    for i, question in enumerate(
        EXAMPLE_QUESTIONS[:6]
    ):

        with columns[i % 2]:

            if st.button(
                question,
                key=f"welcome_{i}",
                use_container_width=True,
            ):

                st.session_state.pending_question = (
                    question
                )

                st.rerun()


# ============================================================
# FOLLOW-UP SUGGESTIONS
# ============================================================

if st.session_state.suggestions:

    st.divider()

    display_suggestions()


# ============================================================
# CHAT INPUT
# ============================================================

typed_question = st.chat_input(
    "Ask a question or ask a follow-up..."
)


# ============================================================
# PROCESS PENDING QUESTION
# ============================================================

if st.session_state.pending_question:

    question = (
        st.session_state.pending_question
    )

    st.session_state.pending_question = None

    with st.chat_message(
        "user",
        avatar="👤",
    ):

        st.markdown(
            question
        )

    with st.chat_message(
        "assistant",
        avatar="🤖",
    ):

        process_question(
            question
        )


# ============================================================
# PROCESS TYPED QUESTION
# ============================================================

elif typed_question:

    with st.chat_message(
        "user",
        avatar="👤",
    ):

        st.markdown(
            typed_question
        )

    with st.chat_message(
        "assistant",
        avatar="🤖",
    ):

        process_question(
            typed_question
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Healthcare Claims Analytics • Snowflake Cortex Analyst"
)