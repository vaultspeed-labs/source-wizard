from vaultspeed_sdk.source.release import ReleaseParts
from vaultspeed_sdk.client import Client, TaskConfig
from vaultspeed_sdk.client import UserPasswordAuthentication
from vaultspeed_sdk.system import System
from vaultspeed_sdk.source.attribute import AttributeTypes
import streamlit as st

# Initialize session state for data profiling
if 'dp_step' not in st.session_state:
    st.session_state.dp_step = "login"
if 'dp_client' not in st.session_state:
    st.session_state.dp_client = None
if 'dp_system' not in st.session_state:
    st.session_state.dp_system = None
if 'dp_source' not in st.session_state:
    st.session_state.dp_source = None

def data_profiling_login():
    """Login page for data profiling functionality"""
    st.title("Data Profiling - VaultSpeed")
    st.header("Step 1: Log in to VaultSpeed")
    
    username = st.text_input("Username", key="dp_username")
    password = st.text_input("Password", type="password", key="dp_password")
    
    if st.button("Login", key="dp_login_btn"):
        if username and password:
            try:
                with st.spinner("Authenticating..."):
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
                    
                    st.session_state.dp_client = client
                    st.session_state.dp_system = system
                    st.session_state.dp_step = "source_selection"
                    st.success("Login successful!")
                    st.rerun()
            except Exception as e:
                st.error(f"Login failed: {str(e)}")
        else:
            st.warning("Please enter both username and password")

def data_profiling_source_selection():
    """Source selection page for data profiling"""
    st.title("Data Profiling - VaultSpeed")
    st.header("Step 2: Select Source to Profile")
    
    system = st.session_state.dp_system
    
    try:
        # Get all projects
        projects = [project.name for project in system.projects]
        
        if not projects:
            st.warning("No projects found in your VaultSpeed instance")
            if st.button("Back to Login"):
                st.session_state.dp_step = "login"
                st.rerun()
            return
        
        # Project selection
        selected_project_name = st.selectbox(
            "Select a Project",
            projects,
            key="dp_project_select"
        )
        
        # Get the selected project
        project = system.get_project(selected_project_name)
        
        # Get all sources in the project
        sources = [source.name for source in project.sources]
        
        if not sources:
            st.warning(f"No sources found in project '{selected_project_name}'")
            if st.button("Back to Login"):
                st.session_state.dp_step = "login"
                st.rerun()
            return
        
        # Source selection
        selected_source_name = st.selectbox(
            "Select a Source to Profile",
            sources,
            key="dp_source_select"
        )
        
        # Display source information
        st.info(f"📊 Selected: {selected_project_name} → {selected_source_name}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Back to Login", key="dp_back_to_login"):
                st.session_state.dp_step = "login"
                st.session_state.dp_client = None
                st.session_state.dp_system = None
                st.rerun()
        
        with col2:
            if st.button("Start Profiling", key="dp_start_profiling", type="primary"):
                with st.spinner("Fetching source objects..."):
                    source = project.get_source(selected_source_name)
                    source_objects = source.get_source_objects(refresh=True)
                    source.select_source_objects(source_objects, selected=True)
                    
                    st.session_state.dp_source = source
                    st.session_state.dp_step = "profiling_results"
                    st.rerun()
                    
    except Exception as e:
        st.error(f"Error loading projects/sources: {str(e)}")
        if st.button("Back to Login"):
            st.session_state.dp_step = "login"
            st.rerun()

def get_primary_keys(src_rel_obj):
    primary_keys = []
    for obj in src_rel_obj:
        if hasattr(obj, 'attributes'):
            for attr in obj.attributes:
                if hasattr(attr, 'primary_key') and attr.primary_key:
                    primary_keys.append((obj.name, attr.name))
        else:
            print(f"Object {obj} has no attribute 'attributes'")
    return primary_keys

def generate_primary_key_sql_script(primary_keys):
    sql_scripts = ["-- SQL script to check primary keys for all tables"]

    for idx, (table_name, column_name) in enumerate(primary_keys):
        sql_script = f"""
        -- Check primary key for table {table_name}
        SELECT 
            '{table_name}' AS table_name,
            '{column_name}' AS column_name,
            COUNT(*) AS total_count,
            COUNT(DISTINCT {column_name}) AS distinct_count
        FROM {table_name}
        """
        if idx < len(primary_keys) - 1:
            sql_script += "\nUNION ALL"
        
        sql_scripts.append(sql_script.strip())

    return "\n\n".join(sql_scripts) + ";"


def get_foreign_keys(src_rel_obj):
    foreign_keys = []
    for obj in src_rel_obj:
        if hasattr(obj, 'attributes'):
            for attr in obj.attributes:                
                if hasattr(attr, 'attribute_types'):
                    for attr_type in attr.attribute_types:
                        if attr_type in [AttributeTypes.FOREIGN_KEY, AttributeTypes.PRIMARY_KEY]:
                            foreign_keys.append((obj.name, attr.name))    
    return foreign_keys

def generate_foreign_key_sql_script(foreign_keys):
    foreign_key_sql_scripts = ["-- SQL script to check foreign keys for all tables"]
    for idx, (table_name, column_name) in enumerate(foreign_keys):
        sql_script = f"""
        -- Check foreign key for table {table_name}
        SELECT 
            '{table_name}' AS table_name,
            '{column_name}' AS column_name,
            COUNT(*) AS total_count,
            COUNT(DISTINCT {column_name}) AS distinct_count
        FROM {table_name}
        """
        if idx < len(foreign_keys) - 1:
            sql_script += "\nUNION ALL"
        
        foreign_key_sql_scripts.append(sql_script.strip())
    return "\n\n".join(foreign_key_sql_scripts) + ";"

def get_business_keys(src_rel_obj):
    business_keys = []
    for obj in src_rel_obj:
        if hasattr(obj, 'attributes'):
            for attr in obj.attributes:
                if hasattr(attr, 'business_key') and attr.business_key:
                    business_keys.append((obj.name, attr.name))
        else:
            print(f"Object {obj} has no attribute 'attributes'")
    return business_keys

def generate_business_key_sql_script(business_keys):
    business_key_sql_scripts = ["-- SQL script to check business keys for all tables"]
    for idx, (table_name, column_name) in enumerate(business_keys):
        sql_script = f"""
        -- Check business key for table {table_name}
        SELECT 
            '{table_name}' AS table_name,
            '{column_name}' AS column_name,
            COUNT(*) AS total_count,
            COUNT(DISTINCT {column_name}) AS distinct_count
        FROM {table_name}
        """
        if idx < len(business_keys) - 1:
            sql_script += "\nUNION ALL"
        business_key_sql_scripts.append(sql_script)
    return "\n\n".join(business_key_sql_scripts) + ";"

def display_profiling_results(source):
    """Generate and display data profiling results"""
    st.title("Data Profiling - VaultSpeed")
    st.header("Step 3: Profiling Results")
    
    try:
        with st.spinner("Creating release and analyzing source objects..."):
            source_objects = source.get_source_objects(refresh=True)
            src_rel = source.create_release(
                number=1,
                comment="Data Profiling Release",
                keep=ReleaseParts.ALL,
                import_src_mtd=True
            )
            src_rel_obj = src_rel.objects
            
            # Get all keys
            primary_keys = get_primary_keys(src_rel_obj)
            foreign_keys = get_foreign_keys(src_rel_obj)
            business_keys = get_business_keys(src_rel_obj)
            
            # Generate SQL scripts
            primary_key_sql_script = generate_primary_key_sql_script(primary_keys)
            foreign_key_sql_script = generate_foreign_key_sql_script(foreign_keys)
            business_key_sql_script = generate_business_key_sql_script(business_keys)
        
        st.success("✅ Data profiling completed successfully!")
        
        # Display statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Primary Keys Found", len(primary_keys))
        with col2:
            st.metric("Foreign Keys Found", len(foreign_keys))
        with col3:
            st.metric("Business Keys Found", len(business_keys))
        
        st.divider()
        
        # Display SQL scripts in tabs
        tab1, tab2, tab3 = st.tabs(["Primary Keys", "Foreign Keys", "Business Keys"])
        
        with tab1:
            st.subheader("Primary Key SQL Script")
            st.code(primary_key_sql_script, language="sql")
        
        with tab2:
            st.subheader("Foreign Key SQL Script")
            st.code(foreign_key_sql_script, language="sql")
        
        with tab3:
            st.subheader("Business Key SQL Script")
            st.code(business_key_sql_script, language="sql")
        
        st.divider()
        
        # Download button
        combined_sql = f"""-- Data Profiling SQL Scripts
-- Generated by VaultSpeed Data Profiling Tool

{primary_key_sql_script}

{foreign_key_sql_script}

{business_key_sql_script}
"""
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 Download All SQL Scripts",
                data=combined_sql,
                file_name="data_profiling.sql",
                mime="text/plain",
                type="primary"
            )
        
        with col2:
            if st.button("🔄 Profile Another Source", key="profile_another"):
                st.session_state.dp_step = "source_selection"
                st.session_state.dp_source = None
                st.rerun()
                
    except Exception as e:
        st.error(f"Error during profiling: {str(e)}")
        if st.button("Back to Source Selection"):
            st.session_state.dp_step = "source_selection"
            st.rerun()

# Main application flow
if st.session_state.dp_step == "login":
    data_profiling_login()
elif st.session_state.dp_step == "source_selection":
    data_profiling_source_selection()
elif st.session_state.dp_step == "profiling_results":
    display_profiling_results(st.session_state.dp_source)