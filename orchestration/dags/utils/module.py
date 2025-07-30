from faker import Faker
from faker.providers import DynamicProvider
import pandas as pd
# From datetime import date
import awswrangler as wr
import os
import boto3
from dotenv import load_dotenv
import logging
from airflow.models import Variable


logging.basicConfig(
    filename="logfile.log",
    level=logging.INFO,
    format='%(levelname)s:%(message)s:%(asctime)s'
)


load_dotenv()


def diagnoses():
    gender_neutral_diagnoses = [
        # Infectious Diseases
        "Influenza (Flu)",
        "COVID-19",
        "Tuberculosis",
        "Hepatitis A",
        "Hepatitis B",
        "Hepatitis C",
        "Malaria",
        "Dengue Fever",
        "Pneumonia",
        "Giardiasis",

        # Cardiovascular Conditions
        "Hypertension (High Blood Pressure)",
        "Hyperlipidemia (High Cholesterol)",
        "Atrial Fibrillation",
        "Congestive Heart Failure",
        "Peripheral Artery Disease",

        # Endocrine & Metabolic Disorders
        "Type 1 Diabetes",
        "Type 2 Diabetes",
        "Hypothyroidism",
        "Hyperthyroidism",
        "Metabolic Syndrome",

        # Respiratory Conditions
        "Asthma",
        "Chronic Obstructive Pulmonary Disease (COPD)",
        "Bronchitis",
        "Sleep Apnea",
        "Sarcoidosis",

        # Digestive & Liver Disorders
        "Irritable Bowel Syndrome (IBS)",
        "Gastroesophageal Reflux Disease (GERD)",
        "Celiac Disease",
        "Crohn’s Disease",
        "Ulcerative Colitis",

        # Neurological Disorders
        "Epilepsy",
        "Migraine",
        "Multiple Sclerosis",
        "Parkinson’s Disease",
        "Stroke",

        # Mental & Behavioral Health
        "Major Depressive Disorder",
        "Generalized Anxiety Disorder",
        "Bipolar Disorder",
        "Obsessive-Compulsive Disorder (OCD)",
        "Schizophrenia",

        # Musculoskeletal Conditions
        "Osteoarthritis",
        "Rheumatoid Arthritis",
        "Gout",
        "Tendinitis",
        "Fibromyalgia",

        # Other Common Diagnoses
        "Chronic Kidney Disease",
        "Anemia (e.g., Iron Deficiency)",
        "Allergic Rhinitis (Hay Fever)",
        "Psoriasis",
        "Eczema (Atopic Dermatitis)"
    ]
    return gender_neutral_diagnoses


def diagnoses_provider():
    clinical_diagnoses_provider = DynamicProvider(
        provider_name="clinical_diagnoses",
        elements=diagnoses()
    )
    return clinical_diagnoses_provider


def generate_fake_healthinformatics(
        range_value: int,
        seed_value: int = 1
        ):
    """
    Function to generate fake records of patients and their diagnosis
    :params range_value: int, required. Count of iterations
    :params seed_value: int
    """

    fake = Faker()
    fake.add_provider(diagnoses_provider())
    Faker.seed(seed=seed_value)
    names = [fake.profile()["name"] for _ in range((range_value))]
    names_split = [name.lower().split(sep=" ") for name in names]
    mail = ["{}{}@gmail.com".format(item[0], item[1]) for item in names_split]
    sex = [fake.profile()["sex"] for _ in range((range_value))]

    birthdate = [
        fake.profile()["birthdate"].strftime("%Y-%m-%d")
        for _ in range((range_value))
        ]
    blood_group = [fake.profile()["blood_group"] for _ in range((range_value))]
    ssn = [fake.profile()["ssn"] for _ in range((range_value))]
    job = [fake.profile()["job"] for _ in range((range_value))]
    residence = [fake.profile()["residence"] for _ in range((range_value))]

    address = [
        fake.address().replace("\n", ", ")
        for _ in range((range_value))
        ]
    diagnosis = [fake.clinical_diagnoses() for _ in range((range_value))]

    records = {
        "names": names,
        "sex": sex,
        "birthdate": birthdate,
        "blood_group": blood_group,
        "ssn": ssn,
        "mail": mail,
        "job": job,
        "address": address,
        "residence": residence,
        "diagnosis": diagnosis
    }
    records_df = pd.DataFrame(data=records)
    return records_df


def airflow_boto_session():
    """
    Function to create a boto3 session.
    :return: A boto3 session object.
    """

    session = boto3.Session(
        aws_access_key_id=Variable.get("AWS_KEY_ID"),
        aws_secret_access_key=Variable.get("AWS_SECRET_KEY"),
        region_name="eu-central-1"
    )
    return session


def extract_to_s3(
        file_path: str,
        range_value: int,
        seed_value: int = 1
        ):
    
    """Function to write health records to s3"""

    wr.s3.to_csv(
        data=generate_fake_healthinformatics(
            range_value=range_value, seed_value=seed_value
            ),
        path=file_path,
        dataset=False,
        boto3_session=airflow_boto_session()
    )
logging.info("Extraction to s3 successful!")
