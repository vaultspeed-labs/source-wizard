import streamlit as st
from .utils import question_with_docs_and_radio, question_with_docs_and_number_input, question_with_docs_and_text_input, set_parameter_if_exists

def get_important_params(source):
    # 1. INSERT_ONLY_LOGIC
    preserve_historical_accuracy = question_with_docs_and_radio(
        question="Do you want to preserve historical accuracy by capturing data changes as new record?",
        docs_url="https://docs.vaultspeed.com/space/VPD/3012755470/Parameter+Descriptions#INSERT_ONLY_LOGIC-[-Y-or-N-]-(Recommended:-Y)",
        options=["Yes", "No"],
        index=None,
        key="preserve_historical_accuracy"
    )
    if preserve_historical_accuracy:
        if preserve_historical_accuracy == "No":
            set_parameter_if_exists(source.parameters, "INSERT_ONLY_LOGIC", "N")
        elif preserve_historical_accuracy == "Yes":
            set_parameter_if_exists(source.parameters, "INSERT_ONLY_LOGIC", "Y")
        # 2. EARLY_ARRIVING_FACTS
        early_arriving = question_with_docs_and_radio(
            question="Should business keys be loaded from parent and child objects to prevent loading issues?",
            docs_url="https://docs.vaultspeed.com/space/VPD/3012755470/Parameter+Descriptions#EARLY_ARRIVING_FACTS-[-Y-or-N-]",
            options=["Yes", "No"],
            index=None,
            key="early_arriving_facts"
        )
        if early_arriving:
            if early_arriving == "No":
                set_parameter_if_exists(source.parameters, "EARLY_ARRIVING_FACTS", "N")
            elif early_arriving == "Yes":
                set_parameter_if_exists(source.parameters, "EARLY_ARRIVING_FACTS", "Y")
            # 3. STREAMING_SOURCE
            streaming_source = st.radio("What is the expected frequency of data loads from this source?", ["Real-Time", "Batch"], index=None, key="streaming_source")
            if streaming_source:
                if streaming_source == "Real-Time":
                    set_parameter_if_exists(source.parameters, "STREAMING_SOURCE", "Y")
                    water_mark_size = question_with_docs_and_number_input("Watermark Size", r"https://docs.vaultspeed.com/space/VPD/3012755470/Parameter+Descriptions#WATERMARK_SIZE-%3Cinteger%3E",min_value=1, value=120, key="water_mark_size")
                    error_record_retention_time = question_with_docs_and_number_input("Error record retention time", r"https://docs.vaultspeed.com/space/VPD/3012755470/Parameter+Descriptions#ERROR_RECORD_RETENTION_TIME-%3Cinteger%3E", min_value=1, value=120, key="error_record_retention_time")
                    set_parameter_if_exists(source.parameters, "WATERMARK_SIZE", water_mark_size)
                    set_parameter_if_exists(source.parameters, "ERROR_RECORD_RETENTION_TIME", error_record_retention_time)
                    if water_mark_size and error_record_retention_time:
                        if st.button("Next"):
                            st.session_state.step = "contact_sales"
                            st.rerun()
                elif streaming_source == "Batch":
                    set_parameter_if_exists(source.parameters, "STREAMING_SOURCE", "N")
                    if st.button("Next"):
                        st.session_state.step = "cdc_type"
                        st.rerun()
    #TODO FMC flow integration