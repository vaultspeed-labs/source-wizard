from vaultspeed_sdk.source.release import ReleaseParts
from vaultspeed_sdk.client import Client, TaskConfig
from vaultspeed_sdk.client import UserPasswordAuthentication
from vaultspeed_sdk.system import System
from vaultspeed_sdk.source.attribute import AttributeTypes
import streamlit as st

if 'step' not in st.session_state:
    st.session_state.step = "login"

def login():
    st.header("Log in to VaultSpeed")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Next"):
        auth = UserPasswordAuthentication(api_url="https://training-eu.vaultspeed.com/api", username=username, password=password)
        client = Client(base_url="https://training-eu.vaultspeed.com/api", auth=auth, retries=2, timeout=120, caller="docs", task_config=TaskConfig(polling_interval=10, timeout=0, queue_timeout=600, show_progress=True))
        system = System(client=client)
        st.session_state.system = system
        st.session_state.step = "selection"
        st.rerun()

def get_sources(system):
    projects = [project.name for project in system.projects]
    project = st.selectbox("Select a project", projects)
    project = system.get_project(project)
    sources = [source.name for source in project.sources]
    source = st.selectbox("Select a source", sources)
    source = project.get_source(source)
    if st.button("Next"):
        st.write("Currently fetching source objects...")
        source_objects = source.get_source_objects(refresh=True)
        source.select_source_objects(source_objects, selected=True)
        st.session_state.source = source
        st.session_state.step = "data_profiling"
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
            sql_script += "nUNION ALL"
        business_key_sql_scripts.append(sql_script)
    return "\n\n".join(business_key_sql_scripts) + ";"

def create_release(source):
    source_objects = source.get_source_objects(refresh=True)
    src_rel = source.create_release(number=1, comment="1", keep=ReleaseParts.ALL, import_src_mtd=True)
    src_rel_obj = src_rel.objects
    primary_keys = get_primary_keys(src_rel_obj)
    primary_key_sql_script = generate_primary_key_sql_script(primary_keys)
    foreign_keys = get_foreign_keys(src_rel_obj)
    foreign_key_sql_script = generate_foreign_key_sql_script(foreign_keys)
    business_keys = get_business_keys(src_rel_obj)
    business_key_sql_script = generate_business_key_sql_script(business_keys)
    
    
    st.header("Generated SQL Scripts")
    st.text_area("Primary key SQL Script", primary_key_sql_script, height=300)
    st.text_area("Foreign key SQL Script", foreign_key_sql_script, height=300)
    st.text_area("Business key SQL Script", business_key_sql_script, height=300)
    
    st.download_button(
        label="Download SQL Scripts",
        data=primary_key_sql_script + "\n\n" + foreign_key_sql_script + "\n\n" + business_key_sql_script,
        file_name="data_profiling.sql",
        mime="text/plain"
    )

def data_profiling(source):
    st.header("Data Profiling")
    create_release(source)

if st.session_state.step == "login":
    login()
elif st.session_state.step == "selection":
    get_sources(st.session_state.system)
elif st.session_state.step == "data_profiling":
    create_release(st.session_state.source)