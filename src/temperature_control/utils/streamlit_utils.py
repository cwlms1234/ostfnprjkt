import hmac
import streamlit as st

from temperature_control.utils.general_utils import fetch_config, write_config
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


def get_cfg_widget():
    st.write("Measuring Parameters:")

    top_left_cfg_button, top_middle_cfg_button, top_right_cfg_button = st.columns(3)
    with top_left_cfg_button:
        update_frequency_minutes = st.number_input(
            label="Update interval (minutes)",
            step=0.5,
            value=float(
                (st.session_state["config"]["execution_specs"]["update_frequency"]) / 60
            ),
        )
        st.session_state["config"]["execution_specs"]["update_frequency"] = (
            update_frequency_minutes * 60
        )

    with top_middle_cfg_button:
        min_threshold = st.number_input(
            label="Deactivation Threshold (°C)",
            step=1,
            value=st.session_state["config"]["temperature_thresholds"][
                "deactivation_threshold"
            ],
        )
        st.session_state["config"]["temperature_thresholds"][
            "deactivation_threshold"
        ] = min_threshold

    with top_right_cfg_button:
        max_threshold = st.number_input(
            label="Activation Threshold (°C)",
            step=1,
            value=st.session_state["config"]["temperature_thresholds"][
                "activation_threshold"
            ],
        )
        st.session_state["config"]["temperature_thresholds"]["activation_threshold"] = (
            max_threshold
        )

    st.write("Monitoring Parameters:")

    middle_left_cfg_button, middle_middle_cfg_button, middle_right_cfg_button = (
        st.columns([1, 1, 1])
    )
    with middle_left_cfg_button:
        warning_limit = st.number_input(
            label="Warning value (°C)",
            step=1,
            value=st.session_state["config"]["temperature_thresholds"]["warning_limit"],
        )
        st.session_state["config"]["temperature_thresholds"]["warning_limit"] = (
            warning_limit
        )
    with middle_middle_cfg_button:
        alert_limit = st.number_input(
            label="Alert value (°C)",
            step=1,
            value=st.session_state["config"]["temperature_thresholds"]["alert_limit"],
        )
        st.session_state["config"]["temperature_thresholds"]["alert_limit"] = (
            alert_limit
        )
    with middle_right_cfg_button:
        pass

    bottom_left_cfg_button, bottom_right_cfg_button = st.columns(2)
    with bottom_left_cfg_button:
        if st.button(label="Write to config", use_container_width=True):
            print(st.session_state["config"])
            write_config(st.session_state["config"])
    with bottom_right_cfg_button:
        if st.button(label="Load default config", use_container_width=True):
            write_config(fetch_config("default_config.yaml"))