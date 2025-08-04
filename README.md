# 4WD HEALTH PROJECT


# Multisource Health Records ETL Pipeline 🚑

This project is a robust and scalable **ETL pipeline** for consolidating patient health records from multiple data sources into a centralized data warehouse (Amazon Redshift). It demonstrates data engineering best practices including orchestration with **Apache Airflow**, integration via **Airbyte**, infrastructure provisioning with **Terraform**, and the use of **AWS** cloud services.

## 📌 Project Overview

The pipeline extracts health data from two primary sources:
1. **Google Sheets** – Live health records from a shared spreadsheet (via Google Sheets API).
2. **SimuHealth** *(synthetic source)* – Programmatically generated fake health data using the `Faker` library to simulate electronic health record systems for testing and development purposes.

Each dataset is processed and routed through different transformation and loading strategies, then unified in Redshift for analytics and reporting.

---

## 🛠️ Tech Stack

| Layer | Tools & Services |
|------|------------------|
| Orchestration | Apache Airflow |
| Infrastructure | Terraform |
| Data Sources | Google Sheets API, SimuHealth (Faker-generated) |
| Cloud | AWS (S3, RDS, Redshift) |
| Integration | Airbyte |
| Programming | Python |

---
![alt text](dag.png)
![vpc](assets/vpc.png)
![alt text](assets/cluster_queryeditor.png)
## 🔄 Data Flow Summary

### 🔹 Google Sheets Source
- Extracted via **Google Sheets API**
- Transformed and saved as `.parquet`
- Loaded to **Amazon S3**
- Ingested into **Redshift** via **Airflow**

### 🔹 SimuHealth (Faker) Source
- Generated using `Faker` to simulate structured health records
- Loaded directly into **AWS RDS (PostgreSQL)** using **Airflow**
- Synchronized to **Redshift** using **Airbyte**

---

## 🏗️ Infrastructure

The entire infrastructure is fully managed via **Terraform**, ensuring reproducibility and scalability. Key provisioned components include:
- **Amazon Redshift** (with IAM Role, Pause, Resume, and Resize scheduling)
- **S3 buckets**
- **RDS PostgreSQL**
- **Airflow & Airbyte deployment scaffolds**
- **IAM roles and policies**

### ⏱️ Redshift Lifecycle Features
- **Pause** at `16:30 UTC`
- **Resume** at `10:30 UTC`
- **Resize** to match performance demand at `15:30 UTC`

<!-- ## 👤 Author
#### Taofeecoh Adesanu
##### Data Engineer | Cloud & Data Infrastructure Enthusiast -->
---