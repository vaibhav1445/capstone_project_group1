# capstone_project_group1
🏥 Healthcare Claims Analytics
End-to-End Data Engineering • Data Quality • Data Warehousing • Business Intelligence • Conversational Analytics

An end-to-end Healthcare Claims Analytics platform that transforms raw healthcare claims data into governed, business-ready analytical information.

The solution implements a complete data lifecycle:

AWS S3 → Databricks → Bronze → Silver → Gold → Snowflake → Power BI / Cortex Analyst / Streamlit

The platform combines scalable data engineering, data-quality governance, dimensional modeling, business intelligence, and natural-language analytics on a common analytical foundation.

📌 Project Overview

Healthcare claims data contains information about beneficiaries, providers, claims, payments, diagnoses, procedures, and healthcare transactions. Raw source data requires significant processing before it can be reliably used for business reporting and analysis.

This project establishes a governed path from raw source files to analytical consumption by:

Preserving incoming source data
Cleaning and standardizing datasets
Applying data-quality and validation rules
Building reusable fact and dimension models
Serving governed analytical data through Snowflake
Providing interactive analytics through Power BI
Enabling natural-language-to-SQL analysis using Snowflake Cortex Analyst
Providing a conversational analytics interface using Streamlit

The core principle is:

Preserve → Clean → Validate → Model → Serve → Analyze

🏗️ Solution Architecture
                    ┌─────────────────────────┐
                    │   Healthcare Datasets   │
                    │ Beneficiary / Inpatient │
                    │ Outpatient / Carrier    │
                    │ Prescription Events     │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │       AWS S3             │
                    │     Raw Landing Zone     │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │       Databricks        │
                    │   Distributed Processing │
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
                  │ Dashboards  │ │ Natural Lang. │ │ Conversational│
                  └─────────────┘ └───────────────┘ └─────────────┘
🔄 Data Pipeline
1. Source → AWS S3

Healthcare source datasets are initially placed in Amazon S3, which acts as the centralized raw landing zone.

Core datasets include:

DatasetBusiness Area
Beneficiary	Beneficiary demographics and attributes
Inpatient	Hospital admission and inpatient claims
Outpatient	Outpatient claims and service activity
Carrier	Carrier / insurance claim and payment information
Prescription Drug Events	Pharmacy and prescription information

The S3 landing layer preserves the source representation and provides a clear starting point for data lineage.

2. AWS S3 → Databricks

Databricks serves as the primary distributed processing environment.

Responsibilities include:

Reading source datasets from S3
Creating controlled Bronze representations
Data profiling
Initial validation
Silver transformations
Gold dimensional and fact modeling
Deterministic data-quality checks
🥉 Bronze Layer

The Bronze layer preserves the incoming data in a controlled processing environment.

Key Responsibilities
Source preservation
Schema awareness
Ingestion traceability
Basic validation
Record-load verification
Stable input for Silver processing

Heavy business cleaning is intentionally not performed in Bronze.

🥈 Silver Layer

Silver is the primary cleaning, standardization, and validation layer.

Transformations
Missing-value handling
Deduplication
Data-type standardization
Categorical-value normalization
Date validation
Financial validation
Referential integrity checks
Invalid-record quarantine

Examples of business validations include checking that inpatient admission dates do not occur after discharge dates and that claim from-dates do not occur after through-dates.

The output of Silver is a reliable and standardized dataset that becomes the foundation for Gold modeling.

🥇 Gold Layer

Gold is the business-facing analytical layer.

Instead of exposing raw source structures directly to business users, the Gold layer organizes data into reusable fact and dimension tables.

Dimension Tables
Table	Purpose
DIM_BENEFICIARY	Beneficiary demographics and segmentation
DIM_PROVIDER	Provider identification and classification
DIM_DATE	Time-based analysis
DIM_DIAGNOSIS	Diagnosis classification
DIM_CLAIM_STATUS	Claim lifecycle and status analysis
Fact Tables
Table	Purpose
FACT_CLAIMS	General claim-level analytical measures
FACT_INPATIENT	Inpatient claim measures
FACT_PHARMACY	Prescription drug-event measures

The model follows a star-schema approach, allowing facts to reference reusable dimensions for consistent filtering and aggregation.

❄️ Snowflake Analytical Serving Layer

The curated Gold datasets are loaded into Snowflake, which serves as the governed analytical layer.

Snowflake is responsible for:

Storing Gold fact and dimension datasets
SQL-based analytical access
Power BI workloads
Cortex Analyst SQL execution
Data-quality audit telemetry
Governed access through roles and permissions
Analytical Flow
Databricks Gold
      ↓
Snowflake Gold
      ↓
Power BI
Cortex Analyst
SQL Consumers

Power BI and natural-language analytics use the same governed analytical foundation to maintain consistent business definitions across applications.

✅ Enterprise Data Quality Control Tower

A dedicated Data Quality Control Tower operates alongside the Medallion pipeline.

It provides measurable and auditable data-quality governance.

Quality Dimensions
Dimension	Measurement
Completeness	Presence of required data
Uniqueness	Distinct-value density
Yield	Records passing schema/format checks
Accuracy	Conformance with business rules
Composite Quality Score
Composite Score =
(Completeness + Uniqueness + Yield + Accuracy) / 4
Quality Bands
Score	Status
0.00% – 77.76%	🔴 Critical
77.77% – 85.00%	🟡 Acceptable
85.01% – 100.00%	🟢 Analytics-Ready

Quality telemetry is persisted in Snowflake and can be used for operational monitoring and review.

📊 Power BI Dashboard

Power BI provides the primary visual analytics experience.

Dashboard Capabilities
Executive KPI cards
Claim volume analysis
Financial analysis
Claim status analysis
Trend analysis
Provider analysis
Beneficiary analysis
Time-based analysis
Interactive slicers
Detailed tables and charts

The dashboard consumes governed Gold data through Snowflake rather than directly querying raw source datasets.

🤖 Natural Language Analytics

The project extends traditional BI with natural-language-to-SQL analytics using Snowflake Cortex Analyst.

Flow
Business Question
       ↓
Streamlit
       ↓
Cortex Analyst
       ↓
Semantic Model
       ↓
Generated SQL
       ↓
Snowflake
       ↓
Analytical Result
       ↓
Streamlit

The semantic model provides business terminology, relationships, measures, and column context so that natural-language questions can be translated into appropriate analytical SQL.

Example

User:

How many claims were there in 2010?

Follow-up:

How many of them were denied?

Follow-up:

What were the main denial reasons?

The conversational workflow maintains context to support multi-turn analytical questions.

💬 Streamlit Conversational Application

A Streamlit application provides the user-facing conversational analytics interface.

Components
💬 Chat interface
🧠 Conversation state
🤖 Cortex Analyst integration
🗄️ Snowflake query execution
📋 Result tables
📈 Automatic chart presentation where appropriate
🔍 Generated SQL visibility
💡 Suggested questions
🔄 New conversation functionality
⚠️ Error handling

The application provides transparency by exposing generated SQL along with analytical results.

🧪 Testing & Validation

Validation is performed throughout the pipeline rather than only at the end.

Data Engineering Validation
Source-file readability
Schema validation
Data-type validation
Record-count reconciliation
Mandatory identifier validation
Duplicate detection
Date relationship validation
Financial-field validation
Key relationship validation
Gold Validation
Fact-count reconciliation
Dimension-key validation
Business-key duplication checks
Derived-measure validation
Aggregation validation
BI & AI Validation
Power BI measure validation
Filter/slicer behavior
Visual-to-SQL reconciliation
Semantic-model validation
Generated SQL validation
Empty-result handling
API-error handling
Conversation-state validation




🔐 Security & Governance

The architecture separates source storage, transformation, analytical serving, and business consumption.

Key principles include:

Least-privilege access
Controlled write permissions
Governed analytical repositories
Protected application and semantic-model configurations
End-to-end lineage
Data-quality monitoring
Centralized business definitions
Controlled natural-language analytics

The AI layer is constrained by the semantic model and governed Gold layer rather than allowing unrestricted access to raw source structures.

🔗 End-to-End Data Lineage
Healthcare Source Data
        ↓
      AWS S3
        ↓
    Databricks
        ↓
      Bronze
        ↓
      Silver
        ↓
       Gold
        ↓
    Snowflake
        ↓
 ┌──────┼───────────┐
 ↓      ↓           ↓
Power BI Cortex   SQL
        Analyst
          ↓
      Streamlit
          ↓
    Business Users

The complete lineage ensures that analytical outputs can be traced from business consumption back through Gold, Silver, Bronze, Databricks, and the original S3 landing zone.

🛠️ Technology Stack
Technology	Purpose
☁️ AWS S3	Raw data landing and source preservation
🔥 Databricks	Distributed processing and Medallion architecture
🐍 Python	Data processing and application logic
⚡ PySpark	Large-scale data transformation
❄️ Snowflake	Analytical serving and SQL
📊 Power BI	Business intelligence and dashboards
🤖 Snowflake Cortex Analyst	Natural-language-to-SQL
💬 Streamlit	Conversational analytics UI
🧠 Semantic Model YAML	Business context for Cortex Analyst
🐼 Pandas	Result handling and presentation




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

Note: Large Power BI files such as Architecture_BI.pbix are intentionally excluded from the repository.

📈 Business Questions Supported
Claims
How many claims are there?
Claim count by status
Claim count by claim type
Which claims were approved?
Payments
What is the total claim amount?
What is the total insurance payment?
What is the total patient payment?
Denials
How many claims were denied?
What are the main denial reasons?
What is the denial percentage?
What was the denial percentage for a selected year?
Providers & Beneficiaries
Claim count by provider type
Provider type with the highest claim volume
Claim count by age group
Claim count by gender
Time Analysis
Claim count by year
Total claim amount for a selected year
Claim-volume trends over time




🎯 Key Project Outcomes
Data Engineering
AWS S3 raw landing architecture
Databricks integration
Bronze → Silver → Gold Medallion pipeline
Data cleaning and standardization
Gold fact and dimension modeling
Snowflake analytical serving
Data Quality
Layer-level quality monitoring
Column-level profiling
Completeness scoring
Uniqueness scoring
Yield scoring
Accuracy scoring
Composite health score
Snowflake audit repository
Analytics
Power BI dashboard
Interactive KPI analysis
Healthcare claims analytical model
Cortex Analyst semantic model
Natural-language-to-SQL analytics
Streamlit conversational interface

The combined platform provides a single governed analytical foundation for recurring reporting and exploratory analysis.

🚀 Future Enhancements

Potential production enhancements include:

⚙️ Scheduled/event-driven pipeline execution
🔄 Incremental processing
🚨 Automated data-quality alerts
🧠 Expanded semantic model
👥 Role-based business views
📡 Enhanced pipeline observability
🏥 Additional healthcare domains
🔁 Production-grade CI/CD
🧪 Automated regression testing




👥 Team

Project: Healthcare Claims Analytics

Team Members

Devendra Prasad Madala — Intern
Vaibhav Srivastava — Intern

Mentors

Harsha Panchagnula — Engineer III
Ganesh Kancharla — Engineer II

Date: August 2026




⭐ Project Positioning

This project demonstrates an integrated approach to:

DATA ENGINEERING + DATA QUALITY + DATA WAREHOUSING + BUSINESS INTELLIGENCE + NATURAL LANGUAGE TO SQL + CONVERSATIONAL ANALYTICS

The architecture is designed around a governed analytical foundation where the same curated data supports engineering workflows, quality monitoring, BI dashboards, SQL analytics, and AI-assisted business analysis.

📄 Documentation

For detailed technical documentation covering the architecture, transformations, data-quality framework, dimensional model, Snowflake serving layer, Power BI, Cortex Analyst, Streamlit application, testing, governance, and future enhancements, refer to:

Healthcare Claims Analytics — End-to-End Technical Project Documentation
