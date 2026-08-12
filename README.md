# 🏥 Healthcare Claims Analytics

### End-to-End Data Engineering • Data Quality • Data Warehousing • Business Intelligence • Conversational Analytics

An end-to-end **Healthcare Claims Analytics platform** that transforms raw healthcare claims data into governed, business-ready analytical information.

**AWS S3 → Databricks → Bronze → Silver → Gold → Snowflake → Power BI / Cortex Analyst / Streamlit**

---

## 📌 Project Overview

Healthcare claims data contains information about beneficiaries, providers, claims, payments, diagnoses, procedures, and healthcare transactions. Raw source data requires significant processing before it can be reliably used for business reporting and analysis.

This project establishes a governed path from raw source files to analytical consumption by:

- 📥 Preserving incoming source data
- 🧹 Cleaning and standardizing datasets
- ✅ Applying data-quality and validation rules
- ⭐ Building reusable fact and dimension models
- ❄️ Serving governed analytical data through Snowflake
- 📊 Providing interactive analytics through Power BI
- 🤖 Enabling natural-language-to-SQL analysis using Snowflake Cortex Analyst
- 💬 Providing a conversational analytics interface using Streamlit

### Core Principle

> **Preserve → Clean → Validate → Model → Serve → Analyze**

---

# 🏗️ Solution Architecture

```text
                    ┌─────────────────────────┐
                    │   Healthcare Datasets   │
                    │                         │
                    │ Beneficiary             │
                    │ Inpatient               │
                    │ Outpatient              │
                    │ Carrier                 │
                    │ Prescription Events     │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │        AWS S3           │
                    │    Raw Landing Zone      │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │       Databricks        │
                    │ Distributed Processing  │
                    └────────────┬────────────┘
                                 │
                   ┌────────────┼────────────┐
                   ▼            ▼            ▼
              ┌────────┐  ┌────────┐  ┌────────┐
              │ Bronze │  │ Silver │  │  Gold  │
              │  Raw   │→ │ Clean  │→ │ Model  │
              └────────┘  └────────┘  └────┬───┘
                                            │
                                            ▼
                                  ┌─────────────────┐
                                  │    Snowflake    │
                                  │ Analytical Layer│
                                  └───────┬─────────┘
                                          │
                         ┌────────────────┼────────────────┐
                         ▼                ▼                ▼
                  ┌─────────────┐ ┌───────────────┐ ┌─────────────┐
                  │   Power BI  │ │ Cortex Analyst│ │  Streamlit  │
                  │  Dashboards │ │ Natural Lang. │ │ Conversational│
                  └─────────────┘ └───────────────┘ └─────────────┘
🔄 End-to-End Data Flow
Raw Healthcare Data
        │
        ▼
      AWS S3
        │
        ▼
   ┌───────────┐
   │ Databricks│
   └─────┬─────┘
         │
         ▼
     🥉 Bronze
         │
         │ Ingestion
         │ Validation
         ▼
     🥈 Silver
         │
         │ Cleaning
         │ Standardization
         │ Data Quality
         ▼
      🥇 Gold
         │
         │ Dimensional Modeling
         ▼
     Snowflake
         │
    ┌────┼────────────┐
    │    │            │
    ▼    ▼            ▼
 Power BI  Cortex    Streamlit
           Analyst
☁️ 1. AWS S3 — Raw Landing Zone

AWS S3 acts as the centralized raw landing zone for healthcare datasets.

Source Datasets
Dataset	Business Area
Beneficiary	Beneficiary demographics and attributes
Inpatient	Hospital admission and inpatient claims
Outpatient	Outpatient claims and service activity
Carrier	Carrier / insurance claims
Prescription Drug Events	Pharmacy and prescription activity
Responsibilities
Store source files
Preserve source representation
Provide centralized raw storage
Maintain source-level lineage
Act as the entry point for Databricks processing
🔥 2. Databricks — Data Processing

Databricks is used as the primary data engineering and distributed processing platform.

Responsibilities
Read source data from S3
Create Bronze datasets
Profile source data
Apply validation rules
Perform Silver transformations
Build Gold fact and dimension tables
Execute data-quality checks
🥉 3. Bronze Layer

The Bronze layer maintains a controlled representation of the incoming source data.

Key Activities
Source data ingestion
Schema validation
Record-count validation
Basic structural checks
Ingestion traceability
Source preservation

Bronze should preserve the source rather than aggressively transform it.

🥈 4. Silver Layer

The Silver layer performs the primary cleaning, standardization, and validation.

Transformations
🧹 Missing-value handling
🔄 Deduplication
🔤 Categorical standardization
🔢 Data-type standardization
📅 Date validation
💰 Financial validation
🔗 Referential integrity checks
🚨 Invalid-record identification
🗑️ Duplicate-record removal
Example Business Rules
Admission Date <= Discharge Date

Claim From Date <= Claim Through Date

Required Business Keys != NULL

Financial Amounts >= 0

Reference Keys must exist in corresponding dimensions
🥇 5. Gold Layer

The Gold layer is the business-facing analytical layer.

The data is modeled using reusable fact and dimension tables.

📐 Dimension Tables
Table	Purpose
DIM_BENEFICIARY	Beneficiary demographics and segmentation
DIM_PROVIDER	Provider identification and classification
DIM_DATE	Time-based analysis
DIM_DIAGNOSIS	Diagnosis classification
DIM_CLAIM_STATUS	Claim lifecycle and status
📊 Fact Tables
Table	Purpose
FACT_CLAIMS	General claim-level analytical measures
FACT_INPATIENT	Inpatient claim measures
FACT_PHARMACY	Prescription drug-event measures
Modeling Approach
                    DIM_DATE
                       │
                       │
DIM_BENEFICIARY ─── FACT_CLAIMS ─── DIM_PROVIDER
                       │
                       │
                DIM_CLAIM_STATUS
                       │
                       │
                 DIM_DIAGNOSIS

The model follows a star-schema approach, allowing facts to reference reusable dimensions for consistent filtering and aggregation.

❄️ 6. Snowflake — Analytical Serving Layer

Snowflake serves as the centralized analytical layer for curated Gold data.

Responsibilities
Store Gold fact tables
Store Gold dimension tables
Provide SQL-based analytics
Serve Power BI workloads
Execute Cortex Analyst-generated SQL
Store data-quality telemetry
Provide governed analytical access
Analytical Flow
Databricks Gold
      │
      ▼
  Snowflake
      │
      ├──────────► Power BI
      │
      ├──────────► Cortex Analyst
      │
      └──────────► SQL Analytics
✅ 7. Data Quality Control Tower

A dedicated Data Quality framework monitors the reliability of the data throughout the pipeline.

Quality Dimensions
Dimension	Description
Completeness	Required values are present
Uniqueness	Duplicate records/values are identified
Yield	Records passing validation checks
Accuracy	Data conforms to business rules
Composite Quality Score
Composite Score =
(Completeness + Uniqueness + Yield + Accuracy) / 4
Quality Bands
Score	Status
0% – 77.76%	🔴 Critical
77.77% – 85%	🟡 Acceptable
85.01% – 100%	🟢 Analytics Ready
Data Quality Flow
Source Data
     │
     ▼
Profiling
     │
     ▼
Validation Rules
     │
     ▼
Quality Metrics
     │
     ▼
Composite Score
     │
     ▼
Snowflake Audit Tables
📊 8. Power BI Dashboard

Power BI provides the primary business intelligence experience.

Dashboard Capabilities
📌 Executive KPIs
📈 Claim volume trends
💰 Financial analysis
🚫 Claim denial analysis
🏥 Provider analysis
👥 Beneficiary analysis
📅 Time-based analysis
🔎 Interactive filtering
📋 Detailed claim analysis
Example KPIs
Total Claims
Total Claim Amount
Total Paid Amount
Denied Claims
Approved Claims
Denial Rate
Average Claim Amount
🤖 9. Snowflake Cortex Analyst

Snowflake Cortex Analyst enables natural-language-to-SQL analytics.

Architecture
Business Question
       │
       ▼
   Streamlit
       │
       ▼
Cortex Analyst
       │
       ▼
Semantic Model
       │
       ▼
Generated SQL
       │
       ▼
  Snowflake
       │
       ▼
Analytical Result
Example

Question:

How many claims were there in 2010?

Follow-up:

How many of them were denied?

Follow-up:

What were the main denial reasons?

The conversational workflow allows users to perform analytical exploration without manually writing SQL.

💬 10. Streamlit Conversational Analytics

A Streamlit application provides the user-facing conversational analytics interface.

Features
💬 Chat-based interface
🧠 Conversation state
🤖 Cortex Analyst integration
❄️ Snowflake query execution
📊 Result visualization
📋 Tabular results
🔍 Generated SQL visibility
💡 Suggested questions
🔄 New conversation
⚠️ Error handling
User Flow
User
 │
 │ Natural Language Question
 ▼
Streamlit
 │
 ▼
Cortex Analyst
 │
 ▼
Semantic Model
 │
 ▼
SQL Generation
 │
 ▼
Snowflake
 │
 ▼
Result
 │
 ▼
Streamlit
🧠 Semantic Model

The semantic model provides business context to Cortex Analyst.

It defines:

Business entities
Fact tables
Dimension tables
Relationships
Measures
Business terminology
Column descriptions
Analytical intent

Example:

tables:
  - name: FACT_CLAIMS

    description: >
      Contains claim-level healthcare transaction data.

    dimensions:
      - CLAIM_STATUS
      - PROVIDER_TYPE
      - YEAR

    measures:
      - TOTAL_CLAIMS
      - TOTAL_CLAIM_AMOUNT
      - TOTAL_PAID_AMOUNT
      - DENIAL_RATE

This helps convert business questions into reliable analytical SQL.

🧪 Testing & Validation

Validation is performed across multiple layers.

Data Engineering Validation
Schema validation
Data-type validation
Record-count reconciliation
Duplicate detection
Mandatory-field validation
Date validation
Financial validation
Referential integrity
Gold Validation
Fact-count validation
Dimension-key validation
Business-key uniqueness
Derived-measure validation
Aggregation validation
BI Validation
KPI validation
Slicer/filter validation
Visual validation
Source-to-dashboard reconciliation
AI Validation
Semantic-model validation
Generated SQL validation
Query-result validation
Empty-result handling
Error handling
Conversation-state validation
🔐 Security & Governance

The architecture follows a governed data-consumption model.

Key Principles
🔒 Least-privilege access
🔐 Controlled data access
🏛️ Governed analytical layer
📋 Centralized business definitions
🔍 Data lineage
✅ Data-quality monitoring
🤖 Controlled AI-generated SQL
📊 Consistent KPI definitions

The AI layer operates against governed analytical data rather than unrestricted raw source data.

🔗 End-to-End Data Lineage
Healthcare Source Data
        │
        ▼
      AWS S3
        │
        ▼
    Databricks
        │
        ▼
      Bronze
        │
        ▼
      Silver
        │
        ▼
       Gold
        │
        ▼
    Snowflake
        │
   ┌────┼──────────────┐
   │    │              │
   ▼    ▼              ▼
Power BI Cortex     Streamlit
         Analyst
            │
            ▼
      Business Users
🛠️ Technology Stack
Technology	Purpose
☁️ AWS S3	Raw data landing and source storage
🔥 Databricks	Data processing and Medallion architecture
🐍 Python	Data processing and application logic
⚡ PySpark	Distributed data transformation
❄️ Snowflake	Analytical warehouse
📊 Power BI	Business intelligence
🤖 Cortex Analyst	Natural-language-to-SQL
💬 Streamlit	Conversational analytics
🧠 YAML	Semantic model definition
🐼 Pandas	Data handling and result processing
🔧 Git / GitHub	Version control
📁 Repository Structure
Healthcare-Claims-Analytics/
│
├── README.md
│
├── Bronze_loading.ipynb
├── DataQuality_Landing.ipynb
│
├── Silver_beneficiary.ipynb
├── Silver_carrier.ipynb
├── Silver_inpatient.ipynb
├── Silver_outpatient.ipynb
├── Silver_pde.ipynb
│
├── gold_dim_beneficiary.ipynb
├── gold_dim_claim_status.ipynb
├── gold_dim_date.ipynb
├── gold_dim_diagnosis.ipynb
├── gold_dim_provider.ipynb
│
├── gold_fact_claims.ipynb
├── gold_fact_inpatient.ipynb
├── gold_fact_pharmacy.ipynb
│
├── databricks_snowflake.ipynb
├── load_gold_to_snowflake.ipynb
│
├── healthcare_ai.py
├── healthcare_claims_semantic_model.yaml
│
├── Data_model_diagram.png
├── architecture_diagram.png
│
└── Healthcare_Claims_Analytics_End_to_End_Journal_Documentation.docx

⚠️ Note: Large Power BI files such as Architecture_BI.pbix are intentionally excluded from this repository.

📈 Business Questions Supported
Claims
How many claims are there?
What is the claim count by status?
What is the claim count by claim type?
How many claims were approved?
Payments
What is the total claim amount?
What is the total insurance payment?
What is the total patient payment?
What is the average claim amount?
Denials
How many claims were denied?
What is the denial rate?
What are the main denial reasons?
What was the denial percentage for a selected year?
Providers
Which provider type has the highest claim volume?
What is the claim volume by provider type?
What is the average claim amount by provider?
Beneficiaries
What is the claim count by age group?
What is the claim count by gender?
Which beneficiary segments generate the highest claim volume?
Time Analysis
How many claims occurred in a particular year?
How does claim volume change over time?
What is the total claim amount by year?
🎯 Key Project Outcomes
Data Engineering
✅ AWS S3 raw landing architecture
✅ Databricks integration
✅ Bronze → Silver → Gold pipeline
✅ Data cleaning and standardization
✅ Data-quality validation
✅ Fact and dimension modeling
✅ Snowflake analytical serving
Data Quality
✅ Completeness scoring
✅ Uniqueness scoring
✅ Yield scoring
✅ Accuracy scoring
✅ Composite quality score
✅ Data-quality audit framework
Analytics
✅ Power BI dashboard
✅ Interactive KPI analysis
✅ Healthcare claims analytical model
✅ Cortex Analyst semantic model
✅ Natural-language-to-SQL analytics
✅ Streamlit conversational interface
🚀 Future Enhancements
⚙️ Automated pipeline orchestration
🔄 Incremental data processing
🚨 Automated data-quality alerts
📡 Pipeline monitoring and observability
🧠 Expanded semantic model
👥 Role-based business views
🔁 CI/CD integration
🧪 Automated regression testing
📊 Additional healthcare analytics
🤖 Advanced AI-powered insights
👥 Team
Project

Healthcare Claims Analytics

Team Members
Vaibhav Srivastava — Intern
Devendra Prasad Madala — Intern
Mentors
Harsha Panchagnula — Engineer III
Ganesh Kancharla — Engineer II
Date

August 2026

⭐ Project Highlights

This project demonstrates an integrated approach to:

Data Engineering + Data Quality + Data Warehousing + Business Intelligence + Natural Language to SQL + Conversational Analytics

The platform establishes a single governed analytical foundation that supports engineering workflows, data-quality monitoring, BI dashboards, SQL analytics, and AI-assisted business analysis.

📄 Documentation

For detailed technical documentation covering:

Architecture
Data ingestion
Bronze/Silver/Gold transformations
Data-quality framework
Dimensional modeling
Snowflake integration
Power BI
Cortex Analyst
Streamlit application
Testing
Governance
Future enhancements

refer to:

Healthcare_Claims_Analytics_End_to_End_Journal_Documentation.docx