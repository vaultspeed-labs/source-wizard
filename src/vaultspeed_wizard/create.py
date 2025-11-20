import streamlit as st
from vaultspeed_sdk.models.metadata.database_type import DatabaseTypes
from vaultspeed_sdk.models.metadata.cdc_type import CdcTypes
from vaultspeed_sdk.models.metadata.source_type import SourceTypes
from vaultspeed_sdk.exceptions.internal_server_error import InternalServerError
from .sessionState import show_session_state_selector, load_session_state


def create_source(system, project):
    name = st.text_input("Source Name")
    short_name = st.text_input("Source Short Name")
    record_name = st.text_input("Source Record Name")
    bk_name = st.text_input("Source System Business Key")
    # cdc_type_str = st.selectbox("Source CDC", [
    #     "Incremental Load using Modification Flag & Date", 
    #     "Incremental Load using Modification Date",
    #     "Incremental Load using Modification Sequence", 
    #     "Incremental Load", 
    #     "Full Load using Modification Date with Delete Management", 
    #     "Full Load using Modification Sequence with Delete Management", 
    #     "Full Load with Delete Management"
    # ])
    
    # cdc_type_mapping = {
    #     "Incremental Load using Modification Flag & Date": CdcTypes.CDC,
    #     "Incremental Load using Modification Date": CdcTypes.MOD_DATE_INCR,
    #     "Incremental Load using Modification Sequence": CdcTypes.MOD_SEQUENCE_INCR,
    #     "Incremental Load": CdcTypes.INCR,
    #     "Full Load using Modification Date with Delete Management": CdcTypes.MOD_DATE,
    #     "Full Load using Modification Sequence with Delete Management": CdcTypes.MOD_SEQUENCE,
    #     "Full Load with Delete Management": CdcTypes.FULL
    # }
    
    cdc_type = CdcTypes.CDC
    src_type_str = "AGENT" 
    src_type = SourceTypes.AGENT
    database_links = [link.name for link in system.database_links]
    selected_link = st.selectbox("Database Link", database_links)
    database_link = system.get_database_link(selected_link)
    database_type = database_link.database_type
    physical_schema = st.text_input("Physical Schema")
    show_session_state_selector()

    if st.button("Create Source"):
        try:
            st.session_state.source = project.create_source(
                name=name, 
                short_name=short_name, 
                bk_name=bk_name, 
                cdc_type=cdc_type, 
                src_type=src_type, 
                database_type=database_type, 
                database_link=database_link, 
                physical_schema=physical_schema, 
                record_name=record_name
            )
            st.session_state.step = "important_params"
            st.rerun()
        except InternalServerError as e:
            error_message = str(e)
            if "same name already exists" in error_message.lower():
                st.error(f"A source with the name '{name}' already exists. Please choose a different name.")
            else:
                st.error(f"Error creating source: {error_message}")
        except Exception as e:
            st.error(f"An unexpected error occurred while creating the source: {str(e)}")
    
    if st.button("Previous"):
        st.session_state.step = "projects"
        st.rerun()

def create_project(system):
    project_name = st.text_input("Project Name")
    project_description = st.text_input("Project Description")
    if st.button("Create Project"):
        try:
            st.session_state.selected_project = system.create_project(project_name, project_description)
            st.session_state.step = "new_source"
            st.rerun()
        except InternalServerError as e:
            error_message = str(e)
            if "same name already exists" in error_message.lower():
                st.error(f"A project with the name '{project_name}' already exists. Please choose a different name.")
            else:
                st.error(f"Error creating project: {error_message}")
        except Exception as e:
            st.error(f"An unexpected error occurred while creating the project: {str(e)}")
    
    if st.button("Previous"):
        st.session_state.step = "projects"
        st.rerun()