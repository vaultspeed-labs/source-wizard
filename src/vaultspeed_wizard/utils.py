import os
import ast
import streamlit as st
from streamlit import expander, markdown
from vaultspeed_sdk.exceptions.parameter_value_conflict import ParameterValueConflictException

def set_parameter_if_exists(parameters, param_name, value):
    """
    Sets the value of a parameter if it exists on the parameters object.
    Handles parameter value conflicts gracefully by showing user-friendly error messages.
    """
    if hasattr(parameters, param_name):
        try:
            setattr(getattr(parameters, param_name), 'value', value)
            parameters.save()
        except ParameterValueConflictException as e:
            error_message = str(e)
            st.error(f"Parameter conflict: {error_message}")

def question_with_docs_and_radio(
    question: str,
    docs_url: str,
    options: list,
    index=None,
    key=None
):
    """
    Render a question with an inline docs link and a radio button.

    Args:
        question (str): The question text.
        docs_url (str): The URL to the documentation.
        options (list): The radio options.
        index (int, optional): The default selected index.
        key (str, optional): Streamlit key for the radio.

    Returns:
        The selected option.
    """
    col1, col2 = st.columns([8, 1])

    with col1:
        st.write(f"**{question}**")

    with col2:
        st.page_link(docs_url, label="📖 Docs")

    return st.radio(
        label=question,
        options=options,
        index=index,
        key=key,
        label_visibility="collapsed"
    )

def question_with_docs_and_number_input(
    question: str,
    docs_url: str,
    min_value=None,
    max_value=None,
    value=None,
    step=None,
    format=None,
    key=None
):
    col1, col2 = st.columns([8, 1])
    with col1:
        st.write(f"**{question}**")
    with col2:
        st.page_link(docs_url, label="📖 Docs")
    return st.number_input(
        label=question,
        min_value=min_value,
        max_value=max_value,
        value=value,
        step=step,
        format=format,
        key=key,
        label_visibility="collapsed"
    )


def question_with_docs_and_text_input(
    question: str,
    docs_url: str,
    placeholder="",
    value="",
    key=None
):
    col1, col2 = st.columns([8, 1])
    with col1:
        st.write(f"**{question}**")
    with col2:
        st.page_link(docs_url, label="📖 Docs")
    return st.text_input(
        label=question,
        value=value,
        placeholder=placeholder,
        key=key,
        label_visibility="collapsed"
    )

def question_with_docs_and_multiselect(
    question: str,
    docs_url: str,
    options: list,
    value: list = [],
    key=None
):
    col1, col2 = st.columns([8, 1])
    with col1:
        st.write(f"**{question}**")
    with col2:
        st.page_link(docs_url, label="📖 Docs")
    return st.multiselect(
        label=question,
        options=options,
        default=value,
        key=key,
        label_visibility="collapsed"
    )

def question_with_docs_and_selectbox(
    question: str,
    docs_url: str,
    options: list,
    value: str,
    key=None
):
    col1, col2 = st.columns([8, 1])
    with col1:
        st.write(f"**{question}**")
    with col2:
        st.page_link(docs_url, label="📖 Docs")
    return st.selectbox(
        label=question,
        options=options,
        index=options.index(value) if value in options else 0,
        key=key,
        label_visibility="collapsed"
    )

# RAG functionality removed - not needed for core functionality

def set_param_safe(source, key, value):
    if key in source.parameters:
        source.parameters[key].value = value
        source.parameters.save()
    else:
        st.warning(f"This parameter setting is outdated and parameter {key} is no longer in VaultSpeed.")

