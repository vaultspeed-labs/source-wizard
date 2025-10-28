import streamlit as st
from .utils import question_with_docs_and_radio, question_with_docs_and_number_input, question_with_docs_and_text_input, set_parameter_if_exists

def get_system_params(system):
    st.header("System parameters")
    # 1. OBJECT_NAMES_CASE_SENSITIVE
    object_names_case_sensitive = question_with_docs_and_radio(
        "Does the source contain specific capital casing you want to maintain?",
        "https://docs.vaultspeed.com/space/VPD/3012755470/Parameter+Descriptions#OBJECT_NAMES_CASE_SENSITIVE-[-LOWER,-UPPER-or-EXACT-]",
        ["LOWER", "UPPER", "EXACT"]
    )
    if object_names_case_sensitive:
        if object_names_case_sensitive == "LOWER":
            try:
                st.warning("Recommended for Databricks, Google BigQuery, PostgreSQL and Greenplum")
                set_parameter_if_exists(system.parameters, "OBJECT_NAMES_CASE_SENSITIVE", "LOWER")
            except:
                redirect_already_source()
        elif object_names_case_sensitive == "UPPER":
            st.warning("Recommended for Oracle and Snowflake.")
            set_parameter_if_exists(system.parameters, "OBJECT_NAMES_CASE_SENSITIVE", "UPPER")
        elif object_names_case_sensitive == "EXACT":
            st.warning("Object names in the Raw Data Vault will match the exact casing defined in the source or application.")
            set_parameter_if_exists(system.parameters, "OBJECT_NAMES_CASE_SENSITIVE", "EXACT")

        # 2. BK_CASE_INSENSITIVE_COMPARISON
        bk_case_insensitive_comparison = question_with_docs_and_radio(
            "Does your data allow you to state that the BK values can be uppercased for the HKEY calculation?",
            "https://docs.vaultspeed.com/space/VPD/3012755470/Parameter+Descriptions#BK_CASE_INSENSITIVE_COMPARISON-[-Y-or-N-]",
            ["Yes", "No"]
        )
        if bk_case_insensitive_comparison:
            if bk_case_insensitive_comparison == "Yes":
                set_parameter_if_exists(system.parameters, "BK_CASE_INSENSITIVE_COMPARISON", "Y")
            elif bk_case_insensitive_comparison == "No":
                set_parameter_if_exists(system.parameters, "BK_CASE_INSENSITIVE_COMPARISON", "N")

            # 3. HASH_ALGORITHM
            hash_algorithm = question_with_docs_and_radio(
                "Which Hashing algorithm do you want to use?",
                "https://docs.vaultspeed.com/space/VPD/3012755470/Parameter+Descriptions#HASH_ALGORITHM-[-MD5-or-SHA-1%C2%A0or-SHA-256-or-HASH-or-NO_HASH]",
                ["SHA-256", "HASH", "NO_HASH"]
            )
            if hash_algorithm:
                set_parameter_if_exists(system.parameters, "HASH_ALGORITHM", hash_algorithm)

                # 4. HASH_STORE_IN_BINARY
                hash_store_in_binary = question_with_docs_and_radio(
                    "Do you want to store your HASH KEYS as binary?",
                    "https://docs.vaultspeed.com/space/VPD/3012755470/Parameter+Descriptions#HASH_STORE_IN_BINARY--[-Y-or-N-]",
                    ["Yes", "No"]
                )
                if hash_store_in_binary:
                    if hash_store_in_binary == "Yes":
                        set_parameter_if_exists(system.parameters, "HASH_STORE_IN_BINARY", "Y")
                    elif hash_store_in_binary == "No":
                        set_parameter_if_exists(system.parameters, "HASH_STORE_IN_BINARY", "N")
                    # Only show Next button at the end
                    if st.button("Next"):
                        st.session_state.step = "system_params_continue"
                        st.rerun()

def get_system_params_continue(system):
    # This step continues the question flow for system params
    # 1. FMC
    fmc = question_with_docs_and_radio(
        "Do you want to use the VaultSpeed FMC?",
        "https://docs.vaultspeed.com/space/VPD/3012755470/Parameter+Descriptions#USE_FMC%C2%A0[-Y-or-N-]",
        ["Yes", "No"]
    )
    if fmc:
        if fmc == "Yes":
            set_parameter_if_exists(system.parameters, "USE_FMC", "Y")
            fmc_type = question_with_docs_and_radio(
                "Which FMC type do you want to use?",
                "https://docs.vaultspeed.com/space/VPD/3012755470/Parameter+Descriptions#FMC_TYPE--[-Airflow,-ADF-or-generic-]",
                ["Airflow", "ADF", "Generic"]
            )
            if fmc_type:
                set_parameter_if_exists(system.parameters, "FMC_TYPE", fmc_type)
                show_important_system_params(system)
        elif fmc == "No":
            set_parameter_if_exists(system.parameters, "USE_FMC", "N")
            show_important_system_params(system)

def show_important_system_params(system):
    # 1. STORE_TEMP_IN_STAGING
    store_temp_in_staging = question_with_docs_and_radio(
        "Do you want to store the TMP table for DV loading in the STAGING schema?",
        "https://docs.vaultspeed.com/space/VPD/3012755470/Parameter+Descriptions#STORE_TEMP_IN_STAGING-[-Y-or-N-]",
        ["Yes", "No"]
    )
    if store_temp_in_staging:
        if store_temp_in_staging == "Yes":
            set_parameter_if_exists(system.parameters, "STORE_TEMP_IN_STAGING", "Y")
        elif store_temp_in_staging == "No":
            set_parameter_if_exists(system.parameters, "STORE_TEMP_IN_STAGING", "N")
        # 2. INSERT_ONLY_LOGIC
        insert_only_logic = question_with_docs_and_radio(
            "Do you want your raw data vault to contain end dating in the satellite objects?",
            "https://docs.vaultspeed.com/space/VPD/3012755470/Parameter+Descriptions#INSERT_ONLY_LOGIC-[-Y-or-N-]",
            ["Yes", "No"]
        )
        if insert_only_logic:
            if insert_only_logic == "Yes":
                set_parameter_if_exists(system.parameters, "INSERT_ONLY_LOGIC", "N")
            elif insert_only_logic == "No":
                set_parameter_if_exists(system.parameters, "INSERT_ONLY_LOGIC", "Y")
            show_delete_handling(system)

def show_delete_handling(system):
    # 1. CLOSE_DELETED_RECORDS
    close_deleted_records = question_with_docs_and_radio(
        "When a delete occurs on the source, do you want the end date of the latest version be updated?",
        "https://docs.vaultspeed.com/space/VPD/3012755470/Parameter+Descriptions#CLOSE_DELETED_RECORDS-[-Y-or-N-]",
        ["Yes", "No"]
    )
    if close_deleted_records:
        if close_deleted_records == "Yes":
            set_parameter_if_exists(system.parameters, "CLOSE_DELETED_RECORDS", "Y")
        elif close_deleted_records == "No":
            set_parameter_if_exists(system.parameters, "CLOSE_DELETED_RECORDS", "N")
        # 2. INSERT_ON_DELETE
        inser_on_delete = question_with_docs_and_radio(
            "When a delete occurs on the source, do you want a new version to be inserted?",
            "https://docs.vaultspeed.com/space/VPD/3012755470/Parameter+Descriptions#INSERT_ON_DELETE-[-Y-or-N-]",
            ["Yes", "No"]
        )
        if inser_on_delete:
            if inser_on_delete == "Yes":
                set_parameter_if_exists(system.parameters, "INSERT_ON_DELETE", "Y")
            elif inser_on_delete == "No":
                set_parameter_if_exists(system.parameters, "INSERT_ON_DELETE", "N")
            # Only show Next button at the end
            if st.button("Next"):
                st.session_state.step = "projects"
                st.rerun()

@st.dialog("You already have a source created, setting these parameters is no longer possible!")
def redirect_already_source():
    if st.button("Next"):
        st.session_state.step = "projects"
        st.rerun()