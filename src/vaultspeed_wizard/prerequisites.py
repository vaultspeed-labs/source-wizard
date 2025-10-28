import streamlit as st

st.session_state.setdefault("prereq_reset_id", 0)

def check_all_projects_for_source(system):
    try:
        for project in system.projects:
            for source in project.sources:
                return True
    except:    
        return False

@st.dialog("You already got a source created, if you want to set the system parameters delete all sources!")
def dialog_window(system):
    if st.button("Retry"):
            check_all_projects_for_source(system)
            st.rerun()
    if st.button("Close"):
        st.session_state.pop("prerequisite_conf", None)
        st.session_state["prereq_reset_id"] += 1
        st.rerun()


def check_prerequisites(system):
    st.header("Step 0: Prerequisites")
    radio_key = f"prerequisite_conf_{st.session_state['prereq_reset_id']}"
    st.session_state.prerequisite_confirmed = st.radio(
        "Have system parameters been set?",
        ["Yes", "No"],
        index=None,
        key=radio_key,
    )
    if st.session_state.prerequisite_confirmed == "No":
        check = check_all_projects_for_source(system)
        if check == True:
            dialog_window(system)
        else:
            if st.button("Next"):
                st.session_state.step = "system_params"
                st.rerun()
    elif st.session_state.prerequisite_confirmed == "Yes":
        if st.button("Next"):
            st.session_state.step = "projects"
            st.rerun()

# def check_first_source():
#     if 'first_source' not in st.session_state:
#         st.session_state.first_source = None
#     st.session_state.first_source = st.radio("Is this your first source?", ["Yes", "No"], index=None)
    
#     if st.session_state.first_source == "Yes":
#         if st.button("Next"):
#             st.session_state.step = "system_params"
#             st.rerun()
#     elif st.session_state.first_source == "No":
#         if st.button("Next"):
#             st.session_state.step = "important_params"
#             st.rerun()

# def check_common_source():
#     if 'common_source' not in st.session_state:
#         st.session_state.common_source = None
#     st.session_state.common_source = st.radio("Will most sources have the same configuration as the one being defined now?", ["Yes", "No"], index=None)
    
#     if st.session_state.common_source == "Yes":
#         # create variable to track if system or source parameters should be used
#         recommend_setting_parameters()
#     elif st.session_state.common_source == "No":
#         recommend_setting_parameters()

def recommend_setting_parameters():
    st.session_state.recommend_setting_parameters = "on"
    st.write("It is recommended to set system parameters before creating a source. This will ensure that the source is created with the correct configuration, some project and system parameters can't be changed anymore after the creation of a source.")