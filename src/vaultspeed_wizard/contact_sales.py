import streamlit as st
def contact_sales():
    """
    This function creates a Streamlit page for contacting VaultSpeed sales.
    It includes a title, a description, and a button that redirects to the contact sales page.
    """
    st.title("Get in Touch with VaultSpeed Sales")

    st.markdown(
        """
        If you’re interested in using VaultSpeed Streaming,  
        please contact our sales team directly.
        """
    )

    if st.button("Contact Sales"):
        st.markdown(
            """
            <meta http-equiv="refresh" content="0; url=https://vaultspeed.com/contact-sales">
            """,
            unsafe_allow_html=True
        )
    
    if st.button("Back"):
        st.session_state.step = "important_params"
        st.rerun()
