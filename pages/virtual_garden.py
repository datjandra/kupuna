import streamlit as st
import streamlit_shadcn_ui as ui

from style_helper import apply_header
from database import get_exercise_stats, fetch_patient_routines

def main():    
    apply_header()
    st.title("Virtual Garden")

    st.markdown(
      """
      <div class="button-grid">
          <a href="exercise_routines" target="_self" class="button-card">
            <p>View Routines</p>
            <div class="icon">&#129488;</div>
          </a>
          <a href="exercise_log" target="_self" class="button-card">
            <p>Exercise Log</p>
            <div class="icon">&#128200;</div>
          </a>
      </div>
      """, unsafe_allow_html=True)

    st.sidebar.image("https://raw.githubusercontent.com/datjandra/kupuna/refs/heads/main/images/logo.png")

    patient_routines_df = fetch_patient_routines()
    
    # Display patient and routine data in the main area
    st.header('Kūpunas Assigned to Routines')
    ui.table(data=patient_routines_df)

    # Move the patient-routine selection to the sidebar
    selected_patient_routine = st.sidebar.selectbox(
        'Select a kūpuna and assigned routine',
        patient_routines_df['patient_name'] + ' - ' + patient_routines_df['routine_name'],
        index=None  # Set default to no selection
    )

    # Check if a selection has been made
    if selected_patient_routine:
        # Extract selected patient and routine IDs
        selected_patient_name, selected_routine_name = selected_patient_routine.split(' - ')
        selected_patient_id = patient_routines_df.loc[patient_routines_df['patient_name'] == selected_patient_name, 'patient_id'].values[0]
        selected_routine_id = patient_routines_df.loc[patient_routines_df['routine_name'] == selected_routine_name, 'routine_id'].values[0]

    if selected_patient_id and selected_routine_id:
        total_sessions, longest_streak = get_exercise_stats(selected_patient_id, selected_routine_id)
        cols = st.columns(2)
        with cols[0]:
          ui.metric_card(title="Total Sessions", content=total_sessions, key="total-sessions")
        with cols[1]:
          ui.metric_card(title="Longest Streak", content=longest_streak, key="longest-streak")
   
if __name__ == "__main__":
    main()