-- ============================================
-- Lookup tables (from IDS_mapping.csv, split)
-- ============================================
CREATE TABLE admission_type (
    admission_type_id  INT PRIMARY KEY,
    description         VARCHAR(50) NOT NULL
);

CREATE TABLE discharge_disposition (
    discharge_disposition_id  INT PRIMARY KEY,
    description                VARCHAR(150) NOT NULL
);

CREATE TABLE admission_source (
    admission_source_id  INT PRIMARY KEY,
    description            VARCHAR(100) NOT NULL
);

-- ============================================
-- Patients — deliberately minimal.
-- race/gender excluded: investigation found 126
-- patients with genuinely conflicting values across
-- encounters, so these are NOT stable patient-level
-- facts in this dataset (see notebook 01).
-- ============================================
CREATE TABLE patients (
    patient_nbr  BIGINT PRIMARY KEY
);

-- ============================================
-- Encounters — the core fact table.
-- One row per hospital admission. patient_nbr
-- repeats for the 46% of encounters belonging to
-- returning patients (confirmed and intentionally
-- retained — see repeat-patient investigation).
-- ============================================
CREATE TABLE encounters (
    encounter_id                BIGINT PRIMARY KEY,
    patient_nbr                  BIGINT NOT NULL,
    race                          VARCHAR(30),
    gender                        VARCHAR(20),
    age                          VARCHAR(10),
    admission_type_id            INT,
    discharge_disposition_id     INT,
    admission_source_id          INT,
    time_in_hospital               INT,
    payer_code                    VARCHAR(20),
    medical_specialty            VARCHAR(50),
    num_lab_procedures             INT,
    num_procedures                  INT,
    num_medications                 INT,
    number_outpatient                INT,
    number_emergency                  INT,
    number_inpatient                   INT,
    number_diagnoses                    INT,
    max_glu_serum                    VARCHAR(10),
    a1c_result                      VARCHAR(10),
    diag_1                            VARCHAR(10),
    diag_1_group                     VARCHAR(30),
    diag_2                            VARCHAR(10),
    diag_3                            VARCHAR(10),
    change_flag                      VARCHAR(10),
    diabetes_med                    VARCHAR(5),
    readmitted                      VARCHAR(5),
    readmitted_30d                   TINYINT,
    is_repeat_patient                BOOLEAN,
    patient_identity_uncertain        BOOLEAN,

    FOREIGN KEY (patient_nbr) REFERENCES patients(patient_nbr),
    FOREIGN KEY (admission_type_id) REFERENCES admission_type(admission_type_id),
    FOREIGN KEY (discharge_disposition_id) REFERENCES discharge_disposition(discharge_disposition_id),
    FOREIGN KEY (admission_source_id) REFERENCES admission_source(admission_source_id),

    INDEX idx_patient_nbr (patient_nbr),
    INDEX idx_diag_1_group (diag_1_group),
    INDEX idx_readmitted_30d (readmitted_30d)
);

-- ============================================
-- Medications — kept physically separate from
-- encounters per the documented tidiness deferral.
-- Still wide, one row per encounter, not reshaped
-- to long format until a drug-specific question is
-- actually scoped.
-- ============================================
CREATE TABLE encounter_medications (
    encounter_id            BIGINT PRIMARY KEY,
    metformin                 VARCHAR(10),
    repaglinide               VARCHAR(10),
    nateglinide               VARCHAR(10),
    chlorpropamide            VARCHAR(10),
    glimepiride               VARCHAR(10),
    acetohexamide             VARCHAR(10),
    glipizide  	              VARCHAR(10),
    glyburide                 VARCHAR(10),
    tolbutamide  	      VARCHAR(10),
    pioglitazone 	      VARCHAR(10), 
    rosiglitazone  	      VARCHAR(10),
    acarbose  	 	      VARCHAR(10),
    miglitol  		      VARCHAR(10),
    troglitazone  	      VARCHAR(10),
    tolazamide   	      VARCHAR(10),
    examide  		      VARCHAR(10),
    citoglipton  	      VARCHAR(10),
    insulin                   VARCHAR(10),
    glyburide_metformin       VARCHAR(10), 
    glipizide_metformin       VARCHAR(10),
    glimepiride_pioglitazone  VARCHAR(10), 
    metformin_rosiglitazone   VARCHAR(10),
    metformin_pioglitazone    VARCHAR(10),
    

    FOREIGN KEY (encounter_id) REFERENCES encounters(encounter_id)
); 