\# Hospital Readmission Dashboard



\## Overview

This project analyzes diabetic patient readmission patterns using a retrospective

clinical dataset (Strack et al., 2014) and explores how patient-level clinical

factors relate to 30-day hospital readmission.



A separate, facility-level CMS Care Compare dataset is used for national hospital

benchmarking on readmission-related quality measures. These two datasets are

deliberately NOT merged — they operate at different units of analysis (patient

encounter vs. hospital facility) and have no shared key. Each will support its

own dashboard.



\## Status

🚧 In progress — environment setup complete, raw data inspection underway.



\## Data Sources

\- `data/docs/` — Strack et al. (2014) paper and UCI data dictionary (reference material)

\- Raw data (not committed — see `.gitignore`): UCI Diabetes 130-US hospitals dataset,

&#x20; CMS Hospital Readmissions Reduction Program CSV



\## Tech Stack

\- Python (pandas, SQLAlchemy) for ETL and inspection

\- MySQL for relational storage

\- Jupyter notebooks for exploratory analysis



\## Project Structure



\## How to Run

1\. `python -m venv venv` / `venv\\Scripts\\activate`

2\. `pip install -r requirements.txt`

3\. Place raw CSVs in `data/raw/`

4\. Run notebooks in `notebooks/` for inspection, then ETL scripts in `etl/`

