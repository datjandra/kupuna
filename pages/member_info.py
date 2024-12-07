import streamlit as st
import pandas as pd
import random
import io
import streamlit_shadcn_ui as ui

from style_helper import apply_header
from database import fetch_patients, bulk_insert_patient

# Define race categories and ethnicity mapping
race_categories = [
    "Caucasian", "Native Hawaiian or Pacific Islander", "Portuguese",
    "Filipino", "Japanese", "Chinese"
]

ethnicity_mapping = {
    "Caucasian": 2,  # Not Hispanic
    "Native Hawaiian or Pacific Islander": 3,  # Unknown
    "Portuguese": 2,  # Not Hispanic
    "Filipino": 1,  # Hispanic
    "Japanese": 3,  # Unknown
    "Chinese": 3    # Unknown
}

# Fill missing MEM_RACE and set MEM_ETHNICITY
def assign_race_ethnicity(row):
    if pd.isna(row["MEM_RACE"]):
        race = random.choice(race_categories)
        ethnicity = ethnicity_mapping[race]
        return pd.Series([race, ethnicity])
    return pd.Series([row["MEM_RACE"], row["MEM_ETHNICITY"]])

import random

# Set NAME based on MEM_GENDER, MEM_RACE, MEM_ETHNICITY
def assign_name(row):
    # Gender-specific names for each race and ethnicity
    race_to_name = {
        "Caucasian": {
            "M": ["Alexander Baldwin", "Henry Perrine", "Ethan Taylor"] if row["MEM_ETHNICITY"] == 2 else ["Juan Garcia", "Carlos Diaz", "Miguel Torres"],
            "F": ["Emily Cooke", "Olivia Brown", "Sophia Harris"] if row["MEM_ETHNICITY"] == 2 else ["Maria Gonzalez", "Isabella Martinez", "Ana Lopez"]
        },
        "Native Hawaiian or Pacific Islander": {
            "M": ["Kai Malu", "Noa Kaipo", "Lani Kealoha"],
            "F": ["Leilani Aloha", "Moana Kea", "Halia Lani"]
        },
        "Portuguese": {
            "M": ["Antonio Silva", "Manuel Sousa", "Joao Mendes"],
            "F": ["Sofia Costa", "Isabel Ferreira", "Ana Oliveira"]
        },
        "Filipino": {
            "M": ["Jose Rizal", "Andres Bonifacio", "Manuel Quezon"],
            "F": ["Maria Clara", "Gabriela Silang", "Corazon Aquino"]
        },
        "Japanese": {
            "M": ["Greg Tanaka", "Hiroshi Yamamoto", "Steve Suzuki"],
            "F": ["Mary Sato", "Akiko Nakamura", "Eunice Takahashi"]
        },
        "Chinese": {
            "M": ["David Zhang", "Li Wei", "John Wang"],
            "F": ["Bill Mei", "Xiao Hong", "Joseph Yi"]
        }
    }

    # Default name if gender or race is unknown
    default_name = "Taylor Morgan"

    # Get race-based names
    race_names = race_to_name.get(row["MEM_RACE"], {})
    # Get gender-specific names, or use default if not available
    gender_names = race_names.get(row["MEM_GENDER"], [default_name])
    
    # Randomly pick a name from the list
    return random.choice(gender_names)

def main():    
    apply_header()
    st.title("Member Info")

    st.markdown(
      """
      <div class="button-grid">
          <a href="create_routine" target="_self" class="button-card">
            <p>Create Routine</p>
            <div class="icon">&#x1F57A;</div>
          </a>
          <a href="assign_routine" target="_self" class="button-card">
            <p>Assign Routine</p>
            <div class="icon">&#128116;</div>
          </a>
      </div>
      """, unsafe_allow_html=True)

    st.sidebar.image("https://raw.githubusercontent.com/datjandra/kupuna/refs/heads/main/images/logo.png")

    st.header('Kūpunas')
    patients_df = fetch_patients()
    ui.table(data=patients_df)
    
    members = """
    PRIMARY_PERSON_KEY,MEMBER_ID,MEM_GENDER,MEM_RACE,MEM_ETHNICITY,MEM_ZIP3,MEM_MSA_NAME,MEM_STATE
    1E9F89247B2EA224292BDA829,1E9F89247B2EA224292BDA829,M,,,967,"NON-MSA AREA, HI",HI
    F760929731123ECC986CE311B,F760929731123ECC986CE311B,F,,,968,"URBAN HONOLULU, HI",HI
    B6D25593757653ED083F7E816,B6D25593757653ED083F7E816,M,,,968,"URBAN HONOLULU, HI",HI
    222C720211EE79B712933E434,222C720211EE79B712933E434,M,,,968,"URBAN HONOLULU, HI",HI
    111C5B708D4F5DA70CAC42607,111C5B708D4F5DA70CAC42607,F,,,968,"URBAN HONOLULU, HI",HI
    1E9F89247B2EA224292BDA829,1E9F89247B2EA224292BDA829,M,,,967,"NON-MSA AREA, HI",HI
    F760929731123ECC986CE311B,F760929731123ECC986CE311B,F,,,487,"NON-MSA AREA, MI",MI
    B6D25593757653ED083F7E816,B6D25593757653ED083F7E816,M,,,483,"WARREN-TROY-FARMINGTON HILLS, MI",MI
    222C720211EE79B712933E434,222C720211EE79B712933E434,M,,,484,"FLINT, MI",MI
    111C5B708D4F5DA70CAC42607,111C5B708D4F5DA70CAC42607,F,,,485,"FLINT, MI",MI
    """
    members_csv = st.text_area("Members", value=members.strip(), height=300)

    enrollment = """
    PRIMARY_PERSON_KEY,MEMBER_ID,MEMBER_MONTH_START_DATE,YEARMO,MEM_AGE,RELATION,MEM_MSA_NAME,PAYER_LOB,PAYER_TYPE,PROD_TYPE,QTY_MM_MD,QTY_MM_RX,QTY_MM_DN,QTY_MM_VS,MEM_STAT,PRIMARY_CHRONIC_CONDITION_ROLLUP_ID,PRIMARY_CHRONIC_CONDITION_ROLLUP_DESC
    7A406DA9B06D5E514D328418F,7A406DA9B06D5E514D328418F,2023-07-01,202307,76,SUBSCRIBER,"WARREN-TROY-FARMINGTON HILLS, MI",MEDICARE,MP,DENTAL,0.0,0.0,1.0,0.0,,102.0,102 - SEVERE DEMENTIA
    111C5B708D4F5DA70CAC42607,111C5B708D4F5DA70CAC42607,2023-05-01,202305,75,SUBSCRIBER,"FLINT, MI",MEDICARE SUPPLEMENT,MS,VISION,0.0,0.0,0.0,1.0,,102.0,102 - SEVERE DEMENTIA
    222C720211EE79B712933E434,222C720211EE79B712933E434,2023-07-01,202307,83,SUBSCRIBER,"FLINT, MI",MEDICARE,MP,VISION,0.0,0.0,0.0,1.0,,102.0,102 - SEVERE DEMENTIA
    B6D25593757653ED083F7E816,B6D25593757653ED083F7E816,2023-09-01,202309,80,SUBSCRIBER,"WARREN-TROY-FARMINGTON HILLS, MI",MEDICARE,MP,RX,0.0,1.0,0.0,0.0,,102.0,102 - SEVERE DEMENTIA
    F760929731123ECC986CE311B,F760929731123ECC986CE311B,2022-10-01,202210,85,SUBSCRIBER,"NON-MSA AREA, MI",MEDICARE SUPPLEMENT,MS,MEDICAL,1.0,0.0,0.0,0.0,,102.0,102 - SEVERE DEMENTIA
    """
    enrollment_csv = st.text_area("Enrollment", value=enrollment.strip(), height=300)

    if st.button("Insert Data"):
        members_df = pd.read_csv(io.StringIO(members_csv))
        enrollment_df = pd.read_csv(io.StringIO(enrollment_csv))
    
        # Remove duplicates from data2 based on PRIMARY_PERSON_KEY and MEM_MSA_NAME
        members_df = members_df.drop_duplicates(subset=["PRIMARY_PERSON_KEY", "MEM_MSA_NAME"])
    
        # Merge datasets on PRIMARY_PERSON_KEY
        merged_data = pd.merge(members_df, enrollment_df, on="PRIMARY_PERSON_KEY", how="inner")
    
        merged_data[["MEM_RACE", "MEM_ETHNICITY"]] = merged_data.apply(assign_race_ethnicity, axis=1)
    
        merged_data["NAME"] = merged_data.apply(assign_name, axis=1)
    
        # Select only the required columns
        final_data = merged_data[["PRIMARY_PERSON_KEY", "NAME", "MEM_AGE", "MEM_GENDER", "MEM_RACE", "MEM_ETHNICITY"]]
    
        bulk_insert_patient(final_data)

        patients_df = fetch_patients()
        st.dataframe(patients_df)

if __name__ == "__main__":
    main()