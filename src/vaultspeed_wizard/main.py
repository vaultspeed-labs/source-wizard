import streamlit as st
from vaultspeed_sdk.client import Client, TaskConfig
from vaultspeed_sdk.client import UserPasswordAuthentication
from vaultspeed_sdk.system import System

from .prerequisites import check_prerequisites
from .impParam import get_important_params
from .create import create_source, create_project
from .CDCParam import cdc_type, cdc_params
from .systemParam import get_system_params, get_system_params_continue
from .contact_sales import contact_sales
# from .dataProfiling import data_profiling

def authenticate(username, password):
    """Authenticate with VaultSpeed API."""
    auth = UserPasswordAuthentication(
        api_url="https://training-eu.vaultspeed.com/api", 
        username=username, 
        password=password
    )
    client = Client(
        base_url="https://training-eu.vaultspeed.com/api", 
        auth=auth, 
        retries=2, 
        timeout=120, 
        caller="docs", 
        task_config=TaskConfig(
            polling_interval=10, 
            timeout=0, 
            queue_timeout=600, 
            show_progress=True
        )
    )
    system = System(client=client)  
    st.session_state.system = system


def main():
    """Main application function."""
    # Initialize session state
    if 'step' not in st.session_state:
        st.session_state.step = "login"

    # Set page config
    st.set_page_config(
        page_title="VaultSpeed Source Wizard",
        page_icon="🔧",
        layout="wide"
    )

    # Main UI
    st.title("VaultSpeed Source Creation Wizard")
    st.write("This wizard will guide you through the process of creating a new source in VaultSpeed.")
    
    # Step routing
    if st.session_state.step == "login":
        _render_login_step()
    elif st.session_state.step == "prerequisites":
        check_prerequisites(st.session_state.system)
    elif st.session_state.step == "system_params":
        get_system_params(st.session_state.system)
    elif st.session_state.step == "system_params_continue":
        get_system_params_continue(st.session_state.system)
    elif st.session_state.step == "projects":
        _render_projects_step()
    elif st.session_state.step == "new_project":
        create_project(st.session_state.system)
    elif st.session_state.step == "new_source":
        create_source(st.session_state.system, st.session_state.selected_project)
    elif st.session_state.step == "important_params":
        get_important_params(st.session_state.source) 
    elif st.session_state.step == "cdc_type":
        cdc_type(st.session_state.source)
    elif st.session_state.step == "cdc_params":
        cdc_params(st.session_state.source)
    elif st.session_state.step == "data_profiling":
        _render_data_profiling_step()
    elif st.session_state.step == "contact_sales":
        contact_sales()


def _render_login_step():
    """Render the login step."""
    st.header("Log in to VaultSpeed")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Next"):
        authenticate(username, password)
        st.session_state.step = "prerequisites"
        st.rerun()


def _render_projects_step():
    """Render the projects selection step."""
    projects = [project.name for project in st.session_state.system.projects]
    selected_project = st.selectbox("Select a project", projects)
    if st.button("New Project"):
        st.session_state.step = "new_project"
    st.session_state.selected_project = st.session_state.system.get_project(selected_project)
    if st.button("Next"):
        st.session_state.step = "new_source"
    st.rerun()


def _render_data_profiling_step():
    """Render the data profiling step."""
    st.header("Data Profiling")
    st.write("Data profiling is not yet implemented")


if __name__ == "__main__":
    main()