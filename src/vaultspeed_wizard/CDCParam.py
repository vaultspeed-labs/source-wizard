import streamlit as st
from vaultspeed_sdk.models.metadata.cdc_type import CdcTypes
from .utils import question_with_docs_and_radio, question_with_docs_and_selectbox, question_with_docs_and_text_input, question_with_docs_and_multiselect, set_parameter_if_exists

def get_options(data_type, dataset_type):
    options = {
        "Full": {
            "question": "Are there any indications of change available in the full dataset?",
            "choices": ["Modification Date", "Modification Sequence", "No Indication"],
        },
        "Incremental": {
            "question": "Are there any indications of change available in the incremental dataset?",
            "choices": ["Modification Flag & Date", "Modification Date", "Modification Sequence", "No Indication"],
        },
    }
    return options.get(dataset_type, None)

def get_column_question(change_type):
    column_questions = {
        "Modification Date": "What column are you using for the Modification Date?",
        "Modification Sequence": "What column are you using for the Modification Sequence?",
        "Modification Flag & Date": "What columns are you using for the Modification Flag & Date?",
    }
    return column_questions.get(change_type, None)

def get_cdc_type_mapping(dataset_type, change_type):
    cdc_type_mapping = {
        ("Incremental", "Modification Flag & Date"): CdcTypes.CDC,
        ("Incremental", "Modification Date"): CdcTypes.MOD_DATE_INCR,
        ("Incremental", "Modification Sequence"): CdcTypes.MOD_SEQUENCE_INCR,
        ("Incremental", "No Indication"): CdcTypes.INCR,
        ("Full", "Modification Date"): CdcTypes.MOD_DATE,
        ("Full", "Modification Sequence"): CdcTypes.MOD_SEQUENCE,
        ("Full", "No Indication"): CdcTypes.FULL,
    }
    return cdc_type_mapping.get((dataset_type, change_type), None)

def check_cdc_timestamp():
    has_microseconds = question_with_docs_and_radio(
        "Does the CDC_TIMESTAMP value contain microseconds to ensure the correct order of loading?",
        "https://docs.vaultspeed.com/space/VPD/3012755470/Parameter+Descriptions#CDC_TIMESTAMP-[-CHAR-]",
        ["Yes", "No"],
        index=None,
        key="has_microseconds"
    )
    if has_microseconds == "No":
        st.warning("Potential issues in loading: The CDC_TIMESTAMP value may not be detailed enough.")
    return has_microseconds

def ask_logposition(source):
    logposition_available = question_with_docs_and_radio(
        "Does the source database system have log position data available?",
        "https://docs.vaultspeed.com/space/VPD/3012755470/Parameter+Descriptions#CDC_LOGPOSITION_AVAILABLE-[-Y-or-N-]",
        ["Yes", "No"],
        index=None,
        key="logposition_available"
    )
    if logposition_available == "Yes":
        set_parameter_if_exists(source.parameters, "CDC_LOGPOSITION_AVAILABLE", "Y")
        logposition = question_with_docs_and_text_input("What is the name of the attribute that contains this logposition?",
                                                                           "https://docs.vaultspeed.com/space/VPD/3012755470/Parameter+Descriptions#CDC_LOGPOSITION-[-CHAR-]",
                                                                           "Value", key="logposition")
        if logposition != "":
            set_parameter_if_exists(source.parameters, "CDC_LOGPOSITION", logposition)
    return logposition_available, st.session_state.get("logposition", "")

def cdc_type(source):
    existing_cdc_load = st.session_state.get("cdc_load")

    options = ["Full", "Incremental"]
    if existing_cdc_load in options:
        index = options.index(existing_cdc_load)
    else:
        index = None
    
    cdc_load = question_with_docs_and_radio(
        "The dataset that is available in my landing zone is Incrementally loaded or does it contain a Full dataset from the source?",
        "https://docs.vaultspeed.com/space/VPD/3012755470/Parameter+Descriptions#CDC_LOAD-[-CHAR-]",
        options,
        index=index,
        key="cdc_load"
    )

    if cdc_load is None and existing_cdc_load is not None:
        cdc_load = existing_cdc_load
    
    # Save a backup of the value when it's valid (for recovery in landing_schema)
    if cdc_load is not None:
        st.session_state["_cdc_load_backup"] = cdc_load
    
    dataset_options = get_options("cdc", cdc_load)
    if cdc_load and dataset_options:
        cdc_type_val = question_with_docs_and_radio(
            dataset_options["question"],
            "https://docs.vaultspeed.com/space/VPD/3012755470/Parameter+Descriptions#CDC_TYPE-[-CHAR-]",
            dataset_options["choices"],
            index=None,
            key="cdc_type"
        )
        if cdc_type_val is not None:
            column_question = get_column_question(cdc_type_val)
            if column_question:
                cdc_column = question_with_docs_and_text_input(column_question,
                                                                                 "https://docs.vaultspeed.com/space/VPD/3012755470/Parameter+Descriptions#CDC_COLUMN-[-CHAR-]",
                                                                                 "Value", key="cdc_column")
                if cdc_column != "":
                    set_parameter_if_exists(source.parameters, "CDC_COLUMN", cdc_column)
                if cdc_type_val in ["Modification Date", "Modification Sequence", "Modification Flag & Date"]:
                    has_microseconds = check_cdc_timestamp()
                    logposition_available, logposition = ask_logposition(source)
                    
                    missing_fields = []
                    if has_microseconds is None:
                        missing_fields.append("CDC timestamp microseconds")
                    if logposition_available is None:
                        missing_fields.append("log position availability")
                    elif logposition_available == "Yes" and logposition == "":
                        missing_fields.append("log position attribute name")
                    
                    if st.button("Next"):
                        if missing_fields:
                            st.error(f"Please fill in the required fields")
                        else:
                            st.session_state.step = "cdc_params"
                            st.rerun()
            cdc_mapping = get_cdc_type_mapping(cdc_load, cdc_type_val)
            if cdc_mapping is not None:
                source.cdc_type = cdc_mapping
                if cdc_type_val == "No Indication":
                    if st.button("Next"):
                        st.session_state.step = "cdc_params"
                        st.rerun()

# Step 8
def landing_schema(source):
    cdc_load = st.session_state.get("cdc_load")
    
    # If cdc_load is None, try to restore it from backup
    if cdc_load is None:
        backup_cdc_load = st.session_state.get("_cdc_load_backup")
        if backup_cdc_load is not None:
            cdc_load = backup_cdc_load
    
    if cdc_load == "Incremental":
        # Get current values before rendering
        current_incremental = st.session_state.get("landing_schema_incremental", "")
        current_initial = st.session_state.get("landing_schema_initial", "")
        
        st.session_state.landing_schema_incremental = question_with_docs_and_text_input(
            "In what schema is the data landed for incremental loading?",
            "https://docs.vaultspeed.com/space/VPD/3012755470/Parameter+Descriptions#SCHEMA_INI-[-CHAR-]",
            placeholder="Schema",
            value=current_incremental,
            key="landing_schema_incremental_input"
        )
        
        st.session_state.landing_schema_initial = question_with_docs_and_text_input(
            "In what schema is the data landed for initial loading?",
            "https://docs.vaultspeed.com/space/VPD/3012755470/Parameter+Descriptions#SCHEMA_CDC-[-CHAR-]",
            placeholder="Schema",
            value=current_initial,
            key="landing_schema_initial_input"
        )
        
        # Only set parameters when values are provided (don't process empty strings)
        landing_schema_incremental = st.session_state.get("landing_schema_incremental", "")
        if landing_schema_incremental != "":
            set_parameter_if_exists(source.parameters, "SCHEMA_INI", str(landing_schema_incremental))
        
        landing_schema_initial = st.session_state.get("landing_schema_initial", "")
        if landing_schema_initial != "":
            set_parameter_if_exists(source.parameters, "SCHEMA_CDC", str(landing_schema_initial))
            
    elif cdc_load == "Full":
        current_schema = st.session_state.get("landing_schema", "")
        
        st.session_state.landing_schema = question_with_docs_and_text_input(
            "In what schema is the data landed?",
            "https://docs.vaultspeed.com/space/VPD/3012755470/Parameter+Descriptions#SCHEMA_INI-[-CHAR-]",
            placeholder="Schema",
            value=current_schema,
            key="landing_schema_input"
        )
        
        if st.session_state.get("landing_schema", "") != "":
            set_parameter_if_exists(source.parameters, "SCHEMA_INI", st.session_state.landing_schema)
            set_parameter_if_exists(source.parameters, "SCHEMA_CDC", st.session_state.landing_schema)

    
    st.session_state.create_table_option = question_with_docs_and_multiselect(
        "Does VaultSpeed have to create the tables in the landing zone?",
        "https://docs.vaultspeed.com/space/VPD/3012755470/Parameter+Descriptions#CREATE_INI_TABLES-[-Y-or-N-]",
        ["Create CDC Table", "Create Initial Table"],
        value=st.session_state.get("create_table_option", ["Create CDC Table", "Create Initial Table"]),
        key="create_table_option_select"
    )
    
    if st.session_state.create_table_option == ["Create CDC Table", "Create Initial Table"]:
        set_parameter_if_exists(source.parameters, "CREATE_INI_TABLES", "Y")
        set_parameter_if_exists(source.parameters, "CREATE_CDC_TABLES", "Y")
    elif st.session_state.create_table_option == "Don't Create Tables":
        set_parameter_if_exists(source.parameters, "CREATE_INI_TABLES", "N")
        set_parameter_if_exists(source.parameters, "CREATE_CDC_TABLES", "N")

def landing_table(source):
    st.session_state.same_name_source = question_with_docs_and_radio(
        "Do the tables in the landing zone have the same name as the original source tables or do they have some sort of pre- or suffix?",
        "https://docs.vaultspeed.com/space/VPD/3012755470/Parameter+Descriptions#LANDING_TABLE_SUFFIX-[-CHAR-]",
        ["Same", "Different"],
        index=None,
    )
    if st.session_state.same_name_source == "No":
        st.session_state.landing_table_suffix = question_with_docs_and_text_input("What is the suffix of the landing zone tables?",
                                                                                     "https://docs.vaultspeed.com/space/VPD/3012755470/Parameter+Descriptions#LANDING_TABLE_SUFFIX-[-CHAR-]",
                                                                                     "Value")
        if st.session_state.landing_table_suffix != "":
            set_parameter_if_exists(source.parameters, "LANDING_TABLE_SUFFIX", st.session_state.landing_table_suffix)
        st.session_state.landing_table_prefix = question_with_docs_and_text_input("What is the prefix of the landing zone tables?",
                                                                                     "https://docs.vaultspeed.com/space/VPD/3012755470/Parameter+Descriptions#LANDING_TABLE_PREFIX-[-CHAR-]",
                                                                                     "Value")
        if st.session_state.landing_table_prefix != "":
            set_parameter_if_exists(source.parameters, "LANDING_TABLE_PREFIX", st.session_state.landing_table_prefix)

# TODO: clean up this function, it is a bit messy
def oracle_DWH(source):
    st.session_state.oracle_dwh = question_with_docs_and_radio(
        "Is the source database an Oracle DWH?",
        "https://docs.vaultspeed.com/space/VPD/3012755470/Parameter+Descriptions#ORACLE_DWH-[-Y-or-N-]",
        ["Yes", "No"],
        index=None,
    )
    if st.session_state.oracle_dwh == "Yes":
        st.session_state.cdc_tables_inside_dwh = question_with_docs_and_radio(
            "Are the CDC tables stored inside the DWH?",
            "https://docs.vaultspeed.com/space/VPD/3012755470/Parameter+Descriptions#CDC_TABLES_INSIDE_DWH-[-Y-or-N-]",
            ["Yes", "No"],
            index=None,
        )
        if st.session_state.cdc_tables_inside_dwh == "Yes":
            pass
        else:
            st.session_state.remote_dblink_name = question_with_docs_and_text_input("What is the name of the DBLink to the source database?",
                                                                                     "https://docs.vaultspeed.com/space/VPD/3012755470/Parameter+Descriptions#REMOTE_CDC_DBLINK_NAME-[-CHAR-]",
                                                                                     "Value")
        st.session_state.remote_delta_view = question_with_docs_and_radio(
            "Is a loading window table in the source and views on the source CDC tables needed to filter records within the current loading window?",
            "https://docs.vaultspeed.com/space/VPD/3012755470/Parameter+Descriptions#REMOTE_DELTA_VIEW-[-Y-or-N-]",
            ["Yes", "No"],
            index=None,
        )
    elif st.session_state.oracle_dwh == "No":
        if st.button("Next"):
            st.session_state.step = "data_profiling"
            st.rerun()

def apply_oracle_DWH_parameters(source):
    """Apply Oracle DWH parameters based on user selections. Called when Next is pressed."""
    if st.session_state.get("oracle_dwh") == "Yes":
        if st.session_state.get("cdc_tables_inside_dwh") == "Yes":
            if source.parameters.CREATE_REMOTE_DELTA_VIEW.value == "N":
                set_parameter_if_exists(source.parameters, "REMOTE_JOURNALING_TABLES", "Y")
                set_parameter_if_exists(source.parameters, "CREATE_REMOTE_DELTA_VIEW", "Y")
            set_parameter_if_exists(source.parameters, "USE_REMOTE_CDC_DBLINK", "N")
            set_parameter_if_exists(source.parameters, "REMOTE_JOURNALING_TABLES", "N")
        else:
            set_parameter_if_exists(source.parameters, "REMOTE_JOURNALING_TABLES", "Y")
            if st.session_state.get("remote_dblink_name", "") != "":
                set_parameter_if_exists(source.parameters, "REMOTE_CDC_DBLINK_NAME", st.session_state.remote_dblink_name)
                if st.session_state.get("use_remote_cdc_dblink") == "Y":
                    set_parameter_if_exists(source.parameters, "USE_REMOTE_CDC_DBLINK", "N")
                set_parameter_if_exists(source.parameters, "CREATE_REMOTE_DELTA_VIEW", "Y")
                set_parameter_if_exists(source.parameters, "USE_REMOTE_CDC_DBLINK", "Y")
        
        if st.session_state.get("remote_delta_view") == "Yes":
            set_parameter_if_exists(source.parameters, "REMOTE_JOURNALING_TABLES", "Y")
            set_parameter_if_exists(source.parameters, "CREATE_REMOTE_DELTA_VIEW", "Y")
        else:
            set_parameter_if_exists(source.parameters, "CREATE_REMOTE_DELTA_VIEW", "N")
            set_parameter_if_exists(source.parameters, "REMOTE_JOURNALING_TABLES", "N")

def cdc_update_record_all_attributes(source):
    st.session_state.update_record_all_attributes = question_with_docs_and_radio(
        "Are all attributes of an updated record delivered by the CDC system?",
        "https://docs.vaultspeed.com/space/VPD/3012755470/Parameter+Descriptions#CDC_UPDATE_RECORD_ALL_ATTRIBUTES-[-Y-or-N-]",
        ["Yes", "No"],
        index=None,
    )
    if st.session_state.update_record_all_attributes == "Yes":
        types = ["CHAR", "NUMBER", "DATE", "TIME", "TIMESTAMP", "OTHER"]
        st.session_state.no_change_indication = question_with_docs_and_selectbox("What special value should be used to mask unchanged values within each attribute?", 
                                                                                 "https://docs.vaultspeed.com/space/VPD/3012755470/Parameter+Descriptions#NO_CHANGE_INDICATION-[-CHAR-]", 
                                                                                  types, value="")
    else:
        st.session_state.preimage_records = question_with_docs_and_radio(
            "Does the CDC system provide pre-image records?",
            "https://docs.vaultspeed.com/space/VPD/3012755470/Parameter+Descriptions#CDC_PRE_IMAGE_AVAILABLE-[-Y-or-N-]",
            ["Yes", "No"],
            index=None,
        )
        if st.session_state.preimage_records == "Yes":
            st.session_state.preimage_column = question_with_docs_and_text_input("In what column is this stored?",
                                                                                       "https://docs.vaultspeed.com/space/VPD/3012755470/Parameter+Descriptions#CDC_PRE_POST_IMAGE_FLAG-[-CHAR-]",
                                                                                       "Value")
            st.session_state.preimage_unique_key = question_with_docs_and_text_input("What is the unique indicator that links the pre- and post-image together?",
                                                                                       "https://docs.vaultspeed.com/space/VPD/3012755470/Parameter+Descriptions#CDC_PRE_IMAGE_UNIQUE_KEY-[-CHAR-]",
                                                                                       "Value")
            st.session_state.preimage_flag_value = question_with_docs_and_text_input("What is the value of the pre-image flag?",
                                                                                       "https://docs.vaultspeed.com/space/VPD/3012755470/Parameter+Descriptions#CDC_PRE_IMAGE_FLAG_VALUE-[-CHAR-]",
                                                                                       "Value")
            st.session_state.postimage_flag_value = question_with_docs_and_text_input("What is the value of the post-image flag?",
                                                                                       "https://docs.vaultspeed.com/space/VPD/3012755470/Parameter+Descriptions#CDC_POST_IMAGE_FLAG_VALUE-[-CHAR-]",
                                                                                       "Value")
    st.session_state.lcl_timestamp_for_initial_load = question_with_docs_and_radio(
        "Will the Load Cycle Info timestamp be used for the initial load or the timestamp from the source?",
        "https://docs.vaultspeed.com/space/VPD/3012755470/Parameter+Descriptions#USE_LCI_TIMESTAMP_FOR_INITIAL_LOAD-[-Y-or-N-]",
        ["Load Cycle", "Source Timestamp"],
        index=None,
    )

def apply_cdc_update_record_all_attributes_parameters(source):
    """Apply CDC update record parameters based on user selections. Called when Next is pressed."""
    if st.session_state.get("update_record_all_attributes") == "Yes":
        set_parameter_if_exists(source.parameters, "CDC_UPDATE_RECORD_ALL_ATTRIBUTES", "Y")
        types = ["CHAR", "NUMBER", "DATE", "TIME", "TIMESTAMP", "OTHER"]
        if st.session_state.get("no_change_indication") is not None:
            for t in types:
                attr_name = f"NO_CHANGE_INDICATION_{t}"
                set_parameter_if_exists(source.parameters, attr_name, "Y" if st.session_state.no_change_indication == t else "N")
    else:
        set_parameter_if_exists(source.parameters, "CDC_UPDATE_RECORD_ALL_ATTRIBUTES", "N")
        if st.session_state.get("preimage_records") == "Yes":
            set_parameter_if_exists(source.parameters, "CDC_PRE_IMAGE_AVAILABLE", "Y")
            if st.session_state.get("preimage_column", "") != "":
                set_parameter_if_exists(source.parameters, "CDC_PRE_POST_IMAGE_FLAG", st.session_state.preimage_column)
            if st.session_state.get("preimage_unique_key", "") != "":
                set_parameter_if_exists(source.parameters, "CDC_PRE_IMAGE_UNIQUE_KEY", st.session_state.preimage_unique_key)
            if st.session_state.get("preimage_flag_value", "") != "":
                set_parameter_if_exists(source.parameters, "CDC_PRE_IMAGE_FLAG_VALUE", st.session_state.preimage_flag_value)
            if st.session_state.get("postimage_flag_value", "") != "":
                set_parameter_if_exists(source.parameters, "CDC_POST_IMAGE_FLAG_VALUE", st.session_state.postimage_flag_value)
        else:
            set_parameter_if_exists(source.parameters, "CDC_PRE_IMAGE_AVAILABLE", "N")
    
    if st.session_state.get("lcl_timestamp_for_initial_load") == "Load Cycle":
        set_parameter_if_exists(source.parameters, "USE_LCI_TIMESTAMP_FOR_INITIAL_LOAD", "Y")
    else:
        set_parameter_if_exists(source.parameters, "USE_LCI_TIMESTAMP_FOR_INITIAL_LOAD", "N")

def cdc_params(source):
    landing_schema(source)
    if 'create_table_option' in st.session_state and st.session_state.create_table_option != None:
        landing_table(source)    
        if 'same_name_source' in st.session_state and st.session_state.same_name_source != None:
            oracle_DWH(source)
            if 'remote_delta_view' in st.session_state and st.session_state.remote_delta_view != None:
                cdc_update_record_all_attributes(source)
                if 'lcl_timestamp_for_initial_load' in st.session_state and st.session_state.lcl_timestamp_for_initial_load != None:
                    if st.button("Next"):
                        apply_oracle_DWH_parameters(source)
                        apply_cdc_update_record_all_attributes_parameters(source)
                        st.session_state.step = "data_profiling"
                        st.rerun()

    if st.button("Previous"):
        st.session_state.step = "cdc_type"
        st.rerun()