import streamlit as st
import pandas as pd
import random
import io
import streamlit_shadcn_ui as ui

from style_helper import apply_header, apply_footer
from database import fetch_patients, bulk_insert_patient

# Define race categories and ethnicity mapping
race_categories = [
    "Caucasian", "Black", "Native Hawaiian or Pacific Islander", "Portuguese",
    "Filipino", "Japanese", "Chinese"
]

ethnicity_mapping = {
    "Caucasian": 2,  # Not Hispanic
    "Black": 3,
    "Native Hawaiian or Pacific Islander": 3,  # Unknown
    "Portuguese": 2,  # Not Hispanic
    "Filipino": 1,  # Hispanic
    "Japanese": 3,  # Unknown
    "Chinese": 3    # Unknown
}

# Fill missing MEM_RACE and set MEM_ETHNICITY
def assign_race_ethnicity(row):
    race = random.choice(race_categories)
    ethnicity = ethnicity_mapping[race]
    return pd.Series([race, ethnicity])

# Set NAME based on MEM_GENDER, MEM_RACE, MEM_ETHNICITY
def assign_name(row):
    # Gender-specific names for each race and ethnicity
    race_to_name = {
        "Caucasian": {
            "M": [
                "Alexander Baldwin", "Henry Perrine", "Ethan Taylor", 
                "William Scott", "James Hunter"
            ] if row["MEM_ETHNICITY"] == 2 else [
                "Juan Garcia", "Carlos Diaz", "Miguel Torres", 
                "Luis Ramirez", "Pedro Sanchez"
            ],
            "F": [
                "Emily Cooke", "Olivia Brown", "Sophia Harris", 
                "Emma Thompson", "Charlotte Evans"
            ] if row["MEM_ETHNICITY"] == 2 else [
                "Maria Gonzalez", "Isabella Martinez", "Ana Lopez", 
                "Lucia Morales", "Elena Navarro"
            ]
        },
        "Native Hawaiian or Pacific Islander": {
            "M": [
                "Mike Malu", "Noah Kaipo", "Lani Kealoha", 
                "Kimo Hekili", "Koa Malakai"
            ],
            "F": [
                "Leilani Aloha", "Moana Kea", "Jennifer Lani", 
                "Hina Kaleo", "Debbie Makana"
            ]
        },
        "Portuguese": {
            "M": [
                "Antonio Silva", "Manuel Sousa", "Joao Mendes", 
                "Carlos Almeida", "Francisco Moreira"
            ],
            "F": [
                "Sofia Costa", "Isabel Ferreira", "Ana Oliveira", 
                "Catarina Rocha", "Teresa Pires"
            ]
        },
        "Filipino": {
            "M": [
                "Jose Rizal", "Andres Bonifacio", "Manuel Quezon", 
                "Ramon Magsaysay", "Lapu-Lapu"
            ],
            "F": [
                "Maria Clara", "Gabriela Silang", "Corazon Aquino", 
                "Imelda Santos", "Jocelyn Cruz"
            ]
        },
        "Japanese": {
            "M": [
                "Greg Tanaka", "Hiroshi Yamamoto", "Steve Suzuki", 
                "Kenji Takeda", "Kevin Kobayashi"
            ],
            "F": [
                "Mary Sato", "Akiko Nakamura", "Eunice Takahashi", 
                "Hana Matsumoto", "Yuki Fujimoto"
            ]
        },
        "Chinese": {
            "M": [
                "David Zhang", "Li Wei", "John Wang", 
                "Kevin Chen", "Tony Huang"
            ],
            "F": [
                "Lillian Mei", "Xiao Hong", "Julia Yi", 
                "Angela Lin", "Grace Liu"
            ]
        },
        "Black": {
            "M": [
                "James Brown", "Michael Johnson", "William Robinson", 
                "David Carter", "Joseph Harris"
            ],
            "F": [
                "Ava Jackson", "Emma Washington", "Sophia Jefferson", 
                "Olivia Brooks", "Maya Scott"
            ]
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

    # Add instructions in the sidebar
    st.sidebar.title("Adding Members")
    
    st.sidebar.markdown("### 1. Identify members with cognitive conditions such as dementia using the Claims Enrollment CSV from the [Lokahi dataset](https://lablab.ai/tech/lokahi-hackathon-datasets).")
    st.sidebar.write("Command:")
    st.sidebar.code('''fgrep DEMENTIA Claims_Enrollment_truncated.csv''', language='text')
    st.sidebar.write("Output:")
    st.sidebar.code('''
    7A406DA9B06D5E514D328418F,7A406DA9B06D5E514D328418F,2023-07-01,202307,76,SUBSCRIBER,"WARREN-TROY-FARMINGTON HILLS, MI",MEDICARE,MP,DENTAL,0.0,0.0,1.0,0.0,,102.0,102 - SEVERE DEMENTIA
    222C720211EE79B712933E434,222C720211EE79B712933E434,2023-07-01,202307,83,SUBSCRIBER,"FLINT, MI",MEDICARE,MP,VISION,0.0,0.0,0.0,1.0,,102.0,102 - SEVERE DEMENTIA
    F2F1E2D2A72DC946BAF56240B,F2F1E2D2A72DC946BAF56240B,2023-01-01,202301,64,,"SAN DIEGO-CHULA VISTA-CARLSBAD, CA",MEDICAID,ME,DENTAL,0.0,0.0,1.0,0.0,ACTIVE,102.0,102 - SEVERE DEMENTIA
    ''', language='text')
    
    st.sidebar.markdown("### 2. Now find members by MEMBER_ID from combined Claims Member CSV dataset.")
    st.sidebar.write("Command:")
    st.sidebar.code('''grep -E "7A406DA9B06D5E514D328418F|F2F1E2D2A72DC946BAF56240B|222C720211EE79B712933E434" combined_data_member.csv''', language='text')
    st.sidebar.write("Output:")
    st.sidebar.code('''
    7A406DA9B06D5E514D328418F,7A406DA9B06D5E514D328418F,F,,,968,"URBAN HONOLULU, HI",HI
    222C720211EE79B712933E434,222C720211EE79B712933E434,M,,,968,"URBAN HONOLULU, HI",HI
    7A406DA9B06D5E514D328418F,7A406DA9B06D5E514D328418F,F,,,480,"WARREN-TROY-FARMINGTON HILLS, MI",MI
    222C720211EE79B712933E434,222C720211EE79B712933E434,M,,,484,"FLINT, MI",MI
    F2F1E2D2A72DC946BAF56240B,F2F1E2D2A72DC946BAF56240B,F,4,3,920,"SAN DIEGO-CHULA VISTA-CARLSBAD, CA",CA
    F2F1E2D2A72DC946BAF56240B,F2F1E2D2A72DC946BAF56240B,F,4,3,920,"SAN DIEGO-CHULA VISTA-CARLSBAD, CA",CA
    ''', language='text')
    
    st.sidebar.markdown("### 3. Copy the output of #1 in Enrollment text box below the headers. Do not overwrite the headers. If headers are deleted then refresh the page and copy the data below the headers.")

    st.sidebar.markdown("### 4. Copy the output of #2 in Members text box below the headers. Do not overwrite the headers. If headers are deleted then refresh the page and copy the data below the headers.")

    st.sidebar.markdown("### 5. Click \"Insert Members\" button to insert the members. Race will be randomly assigned, and name will be randomly assigned from race and gender.")

    st.sidebar.markdown("### 6. To create a new exercise routine click the \"Create Routine\" button.")

    st.sidebar.markdown("### 7. To assign a routine to a member, first create a routine then click the \"Assign Routine\" button.")
    
    st.header('Kūpunas')
    patients_df = fetch_patients()
    ui.table(data=patients_df)
    
    members = """
    PRIMARY_PERSON_KEY,MEMBER_ID,MEMBER_MONTH_START_DATE,YEARMO,MEM_AGE,RELATION,MEM_MSA_NAME,PAYER_LOB,PAYER_TYPE,PROD_TYPE,QTY_MM_MD,QTY_MM_RX,QTY_MM_DN,QTY_MM_VS,MEM_STAT,PRIMARY_CHRONIC_CONDITION_ROLLUP_ID,PRIMARY_CHRONIC_CONDITION_ROLLUP_DESC
    7A406DA9B06D5E514D328418F,7A406DA9B06D5E514D328418F,2023-07-01,202307,76,SUBSCRIBER,"WARREN-TROY-FARMINGTON HILLS, MI",MEDICARE,MP,DENTAL,0.0,0.0,1.0,0.0,,102.0,102 - SEVERE DEMENTIA
    111C5B708D4F5DA70CAC42607,111C5B708D4F5DA70CAC42607,2023-05-01,202305,75,SUBSCRIBER,"FLINT, MI",MEDICARE SUPPLEMENT,MS,VISION,0.0,0.0,0.0,1.0,,102.0,102 - SEVERE DEMENTIA
    222C720211EE79B712933E434,222C720211EE79B712933E434,2023-07-01,202307,83,SUBSCRIBER,"FLINT, MI",MEDICARE,MP,VISION,0.0,0.0,0.0,1.0,,102.0,102 - SEVERE DEMENTIA
    B6D25593757653ED083F7E816,B6D25593757653ED083F7E816,2023-09-01,202309,80,SUBSCRIBER,"WARREN-TROY-FARMINGTON HILLS, MI",MEDICARE,MP,RX,0.0,1.0,0.0,0.0,,102.0,102 - SEVERE DEMENTIA
    F760929731123ECC986CE311B,F760929731123ECC986CE311B,2022-10-01,202210,85,SUBSCRIBER,"NON-MSA AREA, MI",MEDICARE SUPPLEMENT,MS,MEDICAL,1.0,0.0,0.0,0.0,,102.0,102 - SEVERE DEMENTIA
    D7E42CD09E0574D1F2E069F9D,D7E42CD09E0574D1F2E069F9D,2024-06-01,202406,66,SPOUSE,"FLINT, MI",MEDICARE SUPPLEMENT,MS,DENTAL,0.0,0.0,1.0,0.0,,102.0,102 - SEVERE DEMENTIA
    AE9AE972B8FA17112AAFD96C4,AE9AE972B8FA17112AAFD96C4,2023-11-01,202311,58,SUBSCRIBER,"DETROIT-DEARBORN-LIVONIA, MI",MEDICARE,MR,MEDICAL,1.0,0.0,0.0,0.0,ACTIVE,102.0,102 - SEVERE DEMENTIA
    F2F1E2D2A72DC946BAF56240B,F2F1E2D2A72DC946BAF56240B,2023-01-01,202301,64,,"SAN DIEGO-CHULA VISTA-CARLSBAD, CA",MEDICAID,ME,DENTAL,0.0,0.0,1.0,0.0,ACTIVE,102.0,102 - SEVERE DEMENTIA
    """
    members_csv = st.text_area("Members", value=members.strip(), height=300)

    enrollment = """
    PRIMARY_PERSON_KEY,MEMBER_ID,MEM_GENDER,MEM_RACE,MEM_ETHNICITY,MEM_ZIP3,MEM_MSA_NAME,MEM_STATE
    7A406DA9B06D5E514D328418F,7A406DA9B06D5E514D328418F,F,,,968,"URBAN HONOLULU, HI",HI
    222C720211EE79B712933E434,222C720211EE79B712933E434,M,,,968,"URBAN HONOLULU, HI",HI
    111C5B708D4F5DA70CAC42607,111C5B708D4F5DA70CAC42607,F,,,968,"URBAN HONOLULU, HI",HI
    7A406DA9B06D5E514D328418F,7A406DA9B06D5E514D328418F,F,,,480,"WARREN-TROY-FARMINGTON HILLS, MI",MI
    222C720211EE79B712933E434,222C720211EE79B712933E434,M,,,484,"FLINT, MI",MI
    111C5B708D4F5DA70CAC42607,111C5B708D4F5DA70CAC42607,F,,,485,"FLINT, MI",MI
    F760929731123ECC986CE311B,F760929731123ECC986CE311B,F,,,968,"URBAN HONOLULU, HI",HI
    B6D25593757653ED083F7E816,B6D25593757653ED083F7E816,M,,,968,"URBAN HONOLULU, HI",HI
    F760929731123ECC986CE311B,F760929731123ECC986CE311B,F,,,487,"NON-MSA AREA, MI",MI
    B6D25593757653ED083F7E816,B6D25593757653ED083F7E816,M,,,483,"WARREN-TROY-FARMINGTON HILLS, MI",MI
    AE9AE972B8FA17112AAFD96C4,AE9AE972B8FA17112AAFD96C4,F,,,968,"URBAN HONOLULU, HI",HI
    F2F1E2D2A72DC946BAF56240B,F2F1E2D2A72DC946BAF56240B,F,4,3,920,"SAN DIEGO-CHULA VISTA-CARLSBAD, CA",CA
    D7E42CD09E0574D1F2E069F9D,D7E42CD09E0574D1F2E069F9D,F,,,968,"URBAN HONOLULU, HI",HI
    AE9AE972B8FA17112AAFD96C4,AE9AE972B8FA17112AAFD96C4,F,,,482,"DETROIT-DEARBORN-LIVONIA, MI",MI
    F2F1E2D2A72DC946BAF56240B,F2F1E2D2A72DC946BAF56240B,F,4,3,920,"SAN DIEGO-CHULA VISTA-CARLSBAD, CA",CA
    D7E42CD09E0574D1F2E069F9D,D7E42CD09E0574D1F2E069F9D,F,,,485,"FLINT, MI",MI
    """
    enrollment_csv = st.text_area("Enrollment", value=enrollment.strip(), height=300)

    insert_members = st.button("Insert Members")
    
    apply_footer()
    
    if insert_members:
        members_df = pd.read_csv(io.StringIO(members_csv))
        enrollment_df = pd.read_csv(io.StringIO(enrollment_csv))

        # Perform the filtering
        filtered_members_df = members_df.merge(
            enrollment_df,
            on=["PRIMARY_PERSON_KEY", "MEM_MSA_NAME"],
            how="inner"
        )
    
        # Merge datasets on PRIMARY_PERSON_KEY
        merged_data = pd.merge(filtered_members_df, enrollment_df, on="PRIMARY_PERSON_KEY", how="inner")
    
        merged_data[["MEM_RACE", "MEM_ETHNICITY"]] = merged_data.apply(assign_race_ethnicity, axis=1)

        if "MEM_GENDER_x" in merged_data.columns and merged_data["MEM_GENDER_x"].notna().any():
            merged_data.rename(columns={"MEM_GENDER_x": "MEM_GENDER"}, inplace=True)
        elif "MEM_GENDER_y" in merged_data.columns and merged_data["MEM_GENDER_y"].notna().any:
            merged_data.rename(columns={"MEM_GENDER_y": "MEM_GENDER"}, inplace=True)
        
        merged_data["NAME"] = merged_data.apply(assign_name, axis=1)

        if "MEM_AGE_x" in merged_data.columns:
            merged_data.rename(columns={"MEM_AGE_x": "MEM_AGE"}, inplace=True)
        elif "MEM_AGE_y" in merged_data.columns:
            merged_data.rename(columns={"MEM_AGE_y": "MEM_AGE"}, inplace=True)

        # Select only the required columns
        final_data = merged_data[["PRIMARY_PERSON_KEY", "NAME", "MEM_AGE", "MEM_GENDER", "MEM_RACE", "MEM_ETHNICITY"]]

        bulk_insert_patient(final_data)
        st.rerun()

if __name__ == "__main__":
    main()
