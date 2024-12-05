import streamlit as st

from style_helper import apply_header

from database import get_all_exercises, insert_routine

def main():
    apply_header()
    st.title("Create Exercise Routine")

    st.markdown(
      """
      <div class="button-grid">
          <a href="assign_routine" class="button-card">
            <p>Assign Routine</p>
            <div class="icon">&#128116;</div>
          </a>
          <a href="exercise_routines" class="button-card">
            <p>View Routines</p>
            <div class="icon">&#128221;</div>
          </a>
      </div>
      """, unsafe_allow_html=True)

    # Load exercise routines
    exercise_data = get_all_exercises()

if __name__ == "__main__":
    main()
