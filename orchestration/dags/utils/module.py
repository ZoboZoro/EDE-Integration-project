import logging

import awswrangler as wr
import boto3
import pandas as pd
from datetime import datetime
from airflow.models import Variable
from dotenv import load_dotenv
from faker import Faker
from faker.providers import DynamicProvider

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
        "COV    I19",
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
        "Obsessi    vCompulsive Disorder (OCD)",
        "Schizophrenia",

        # Musculoskeletal Conditions
        "Osteoarthritis",
        "Rheumatoid Arthritis",
        "Gout",
        "Tendinitis",
        "Fibromyalgia",

        # ENT / Head & Neck,
        "Pleomorphic Adenoma",
        "Warthin Tumor",
        "Monomorphic Adenoma",
        "Oncocytoma",
        "Basal Cell Adenoma",
        "Canalicular Adenoma",
        "Lymphoepithelial Lesion",
        "Cysts (e.g., mucoceles, ranulas)",
        "Mucoepidermoid Carcinoma",
        "Adenoid Cystic Carcinoma",
        "Acinic Cell Carcinoma",
        "Salivary Duct Carcinoma",
        "Carcinoma ex Pleomorphic Adenoma",
        "Polymorphous Adenocarcinoma",
        "Adenocarcinoma, NOS",
        "Lymphoma (salivary involvement)",
        "Metastatic Tumors to Salivary Glands",

        # Other Common Diagnoses
        "Chronic Kidney Disease",
        "Anemia (e.g., Iron Deficiency)",
        "Allergic Rhinitis (Hay Fever)",
        "Psoriasis",
        "Eczema (Atopic Dermatitis)"
        "Gallbladder hydrops"
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
        seed_value: int | None = None
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
        datetime.strptime(str(fake.profile()["birthdate"]), "%Y-%m-%d")
        #  fake.profile()["birthdate"].strftime("%Y-%m-%d")
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
        "jobs": job,
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

#  def count


def faker_to_s3(
        range_value: int,
        bucket: str,
        key: str,
        **kwargs
        ):

    """Function to write health records to s3"""

    s3_path = "{}{}".format(bucket, key)
    wr.s3.to_parquet(
        df=generate_fake_healthinformatics(
            range_value=range_value
            ),
        index=False,
        path=s3_path,
        dataset=False,
        boto3_session=airflow_boto_session()
    )
    logging.info("{} load to s3 successful!".format(key))
    kwargs["ti"].xcom_push("key", key)


def replace_with_underscore(x: str):
    """
    Function to strip and replace whitespaces between words with _score
    :param x: a string (required)
    :returns: formatted string with underscore(s) in lowercase
    """
    x = x.strip()
    return x.replace(" ", "_").lower()


def to_snakecase(data_list: list):
    """
    Function to transform list items to snake_case
    :param data_list: takes a list (required)
    :returns: list of items in snake_case
    """
    col = [replace_with_underscore(i) for i in data_list]
    return col


def googlesheet_to_s3(
        client,
        spreadsheet_name,
        file_path,
        **kwargs
        ):

    """
    Function to connect to google drive API and extract data
    :params client: instance of connection to googlesheet API
    :params spreadsheet_name: the target spreadsheet.
    :params file_path:
        Amazon s3 path to write file
        e.g("s3://bucket_name/directory/filename.extension")
    :returns: success message when ingestion is complete
    """
    try:
        spreadsheet = client.open(spreadsheet_name)
        if spreadsheet:
            logging.info("spreadsheet found...")
            worksheet = spreadsheet.sheet1.get_all_records()
            data = pd.DataFrame(worksheet)
            logging.info("ingested successfully!:")
            columns_list = data.columns.to_list()

            # used to_snakecase to transform columns
            columns_list = to_snakecase(columns_list)
            data.columns = columns_list
            logging.info("Column names updated successfully!")
            wr.s3.to_parquet(
                df=data,
                index=False,
                path=file_path,
                dataset=False,
                boto3_session=airflow_boto_session()
            )
            logging.info("upload to s3 complete!")
            kwargs["ti"].xcom_push("key", file_path)
        else:
            logging.info("spreadsheet does not exist!")
    except Exception as e:
        logging.info(e)
