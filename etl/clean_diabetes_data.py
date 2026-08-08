"""
ETL script: loads the cleaned diabetic encounters dataset into MySQL.

Reads data/processed/diabetic_data_cleaned.csv (output of
01_diabetic_data_wrangling.ipynb), splits it into schema-matching tables,
and loads them into the six-table MySQL schema defined in sql/schema.sql.

Safe to re-run: checks each table's row count before inserting, and skips
tables that already have data rather than attempting a duplicate load.
"""

import os
import sys
import pandas as pd
from sqlalchemy import create_engine, inspect, text
from dotenv import load_dotenv


MEDICATION_COLUMNS = [
    'metformin', 'repaglinide', 'nateglinide', 'chlorpropamide', 'glimepiride',
    'acetohexamide', 'glipizide', 'glyburide', 'tolbutamide', 'pioglitazone',
    'rosiglitazone', 'acarbose', 'miglitol', 'troglitazone', 'tolazamide',
    'examide', 'citoglipton', 'insulin', 'glyburide_metformin',
    'glipizide_metformin', 'glimepiride_pioglitazone',
    'metformin_rosiglitazone', 'metformin_pioglitazone'
]

RENAME_MAP = {
    'change': 'change_flag',
    'A1Cresult': 'a1c_result',
    'diabetesMed': 'diabetes_med',
    'glyburide-metformin': 'glyburide_metformin',
    'glipizide-metformin': 'glipizide_metformin',
    'glimepiride-pioglitazone': 'glimepiride_pioglitazone',
    'metformin-rosiglitazone': 'metformin_rosiglitazone',
    'metformin-pioglitazone': 'metformin_pioglitazone'
}

DESC_COLUMNS_TO_DROP = [
    'admission_type_desc', 'discharge_disposition_desc', 'admission_source_desc'
]


def get_engine():
    """Build a SQLAlchemy engine from credentials in .env."""
    load_dotenv()
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_name = os.getenv('DB_NAME')

    if not all([db_user, db_password, db_host, db_name]):
        sys.exit("ERROR: missing one or more DB_* variables in .env")

    return create_engine(
        f'mysql+mysqlconnector://{db_user}:{db_password}@{db_host}/{db_name}'
    )


def load_and_prepare(csv_path):
    """Load the cleaned CSV, rename columns to MySQL-safe names."""
    diabetic = pd.read_csv(csv_path)
    diabetic = diabetic.rename(columns=RENAME_MAP)

    missing = [v for v in RENAME_MAP.values() if v not in diabetic.columns]
    if missing:
        sys.exit(f"ERROR: expected renamed columns not found: {missing}")

    return diabetic


def split_tables(diabetic):
    """Split the cleaned dataframe into schema-matching tables."""
    patients_df = diabetic[['patient_nbr']].drop_duplicates().reset_index(drop=True)

    encounters_df = diabetic.drop(columns=MEDICATION_COLUMNS)
    encounters_df = encounters_df.drop(columns=DESC_COLUMNS_TO_DROP)

    medications_df = diabetic[['encounter_id'] + MEDICATION_COLUMNS]

    assert patients_df.shape[0] == diabetic['patient_nbr'].nunique()
    assert encounters_df.shape[0] == diabetic.shape[0]
    assert medications_df.shape[0] == diabetic.shape[0]

    return patients_df, encounters_df, medications_df


def verify_columns_match(engine, df, table_name):
    """Compare a dataframe's columns against the live table's columns."""
    inspector = inspect(engine)
    table_cols = set(col['name'] for col in inspector.get_columns(table_name))
    df_cols = set(df.columns)

    extra = df_cols - table_cols
    missing = table_cols - df_cols

    if extra or missing:
        sys.exit(
            f"ERROR: column mismatch for '{table_name}'. "
            f"Extra in dataframe: {extra}. Missing from dataframe: {missing}."
        )
    print(f"  {table_name}: columns verified")


def table_is_empty(engine, table_name):
    """Check whether a table currently has zero rows."""
    with engine.connect() as conn:
        count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
    return count == 0


def load_table(engine, df, table_name):
    """Load a dataframe into a table, skipping if it already has data."""
    if not table_is_empty(engine, table_name):
        print(f"  {table_name}: already has data — skipping")
        return
    df.to_sql(table_name, engine, if_exists='append', index=False)
    print(f"  {table_name}: loaded {len(df):,} rows")


def main():
    print("Connecting to database...")
    engine = get_engine()

    print("Loading cleaned data...")
    diabetic = load_and_prepare('data/processed/diabetic_data_cleaned.csv')

    print("Loading lookup tables...")
    admission_type = pd.read_csv('data/raw/admission_type.csv', keep_default_na=False, na_values=[''])
    discharge_disposition = pd.read_csv('data/raw/discharge_disposition.csv', keep_default_na=False, na_values=[''])
    admission_source = pd.read_csv('data/raw/admission_source.csv', keep_default_na=False, na_values=[''])

    print("Splitting into schema-matching tables...")
    patients_df, encounters_df, medications_df = split_tables(diabetic)

    print("Verifying column alignment...")
    verify_columns_match(engine, patients_df, 'patients')
    verify_columns_match(engine, encounters_df, 'encounters')
    verify_columns_match(engine, medications_df, 'encounter_medications')

    print("Loading tables (in dependency order)...")
    load_table(engine, admission_type, 'admission_type')
    load_table(engine, discharge_disposition, 'discharge_disposition')
    load_table(engine, admission_source, 'admission_source')
    load_table(engine, patients_df, 'patients')
    load_table(engine, encounters_df, 'encounters')
    load_table(engine, medications_df, 'encounter_medications')

    print("Done.")


if __name__ == '__main__':
    main()