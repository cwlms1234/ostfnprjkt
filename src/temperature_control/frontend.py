import hmac

import streamlit as st
from utils.general_utils import fetch_config, fetch_src_file_path


# Set up loading Page, credentials are stored in ~/.streamlit/secrets.toml
def check_password():
    """Returns `True` if the user had a correct password."""

    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the username or password.
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False


if not check_password():
    st.stop()

# Main Streamlit app starts here

if "config" not in st.session_state:
    st.session_state["config"] = fetch_config()
pg = st.navigation(
    [
        st.Page(fetch_src_file_path("web_pages/1_Monitoring.py")),
        st.Page(fetch_src_file_path("web_pages/2_Stats.py")),
        st.Page(fetch_src_file_path("web_pages/3_File_Download_And_Settings.py")),
    ]
)
pg.run()
