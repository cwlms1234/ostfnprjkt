import hmac
from datetime import datetime, time

import streamlit as st
from utils.plots import (
    create_heatmap_plot,
    create_pump_diagram,
    create_temperature_distribution_chart,
)

from temperature_control.utils.general_utils import fetch_config, write_config
from temperature_control.utils.sql_utils import (
    fetch_df_for_time_interval,
    fetch_newest_timestamp,
    fetch_oldest_timestamp,
)


def get_login_page():
    """Checks user credentials before allowing access to the app"""
    # https://docs.streamlit.io/knowledge-base/deploy/authentication-without-sso

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
            # del st.session_state["username"]
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
    """Allows users specified in config.yaml / admins to edit the configuration"""
    st.write("Measuring Parameters:")
    st.session_state["config"] = fetch_config()

    # Set up the top line of buttons
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

    # Set up the middle line of buttons
    middle_left_cfg_button, middle_middle_cfg_button, middle_right_cfg_button = (
        st.columns(3)
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

    # Set up lower buttons to reset / write config
    bottom_left_cfg_button, bottom_right_cfg_button = st.columns(2)
    with bottom_left_cfg_button:
        if st.button(label="Write to config", use_container_width=True):
            write_config(st.session_state["config"])
    with bottom_right_cfg_button:
        if st.button(label="Reset to default config", use_container_width=True):
            write_config(fetch_config("default_config.yaml"))
            st.session_state["config"] = fetch_config()


def get_stat_widget():
    """Allows users to create a dataframe of a chosen timeframe and to download it or
    create charts from its data"""
    content_selector = None
    db_cfg = st.session_state["config"]["db"]

    # Initialize selection elements
    title_placeholder = st.empty()
    start_date_select = st.empty()
    end_date_select = st.empty()
    left_stat_column, middle_stat_column, right_stat_column = st.columns(spec=3)
    content_placeholder = st.empty()

    # Let user choose timeframe:
    newest_ts = fetch_newest_timestamp(db_cfg)
    oldest_ts = fetch_oldest_timestamp(db_cfg)
    title_placeholder.write(
        f"Select data interval between {oldest_ts.date()} and {newest_ts.date()}."
    )

    start_date = oldest_ts
    start_date = start_date_select.date_input(
        label="Start Date", min_value=oldest_ts, max_value=newest_ts
    )
    end_date = end_date_select.date_input(
        label="End Date", min_value=start_date, max_value=newest_ts
    )

    # Make sure single day queries return data by querying the full day
    if start_date == end_date:
        start_date = datetime.combine(start_date, time.min)
        end_date = datetime.combine(end_date, time.max)

    # Set up buttons to make actions / choose what content to display:
    with left_stat_column:
        # Fetch dataframe for chosen timeframe
        if st.button(
            label="Execute Query", use_container_width=True, key="execute_query"
        ):
            st.session_state["stat_interval_df"] = fetch_df_for_time_interval(
                db_cfg,
                start_date,
                end_date,
            )
            st.session_state["df_exists"] = True
            content_selector = "executed_query"

        # Choose to display a diagram for temperature distribution
        if st.button(
            label="Show Temp Distribution",
            use_container_width=True,
            disabled=not st.session_state["df_exists"],
            key="show_temp_dist",
        ):
            content_selector = "show_temp_distribution"

    with middle_stat_column:
        # Show the selected dataframe
        if st.button(
            label="Preview Data",
            use_container_width=True,
            disabled=not st.session_state["df_exists"],
            key="preview data",
        ):
            content_selector = "preview_df"

        # Choose to show a heatmap
        if st.button(
            label="Show Heatmap",
            use_container_width=True,
            disabled=not st.session_state["df_exists"],
            key="show heatmap",
        ):
            content_selector = "show_heatmap"

    with right_stat_column:
        # Downlaod the chosen dataframe
        st.download_button(
            label="Download as CSV",
            data=st.session_state["stat_interval_df"].to_csv().encode("utf-8"),
            file_name=f"{start_date}_{end_date}.csv",
            mime="text/csv",
            use_container_width=True,
            disabled=not st.session_state["df_exists"],
            key="download data",
        )

        # Choose to show a pump activity pie chart
        if st.button(
            label="Show Pump Uptime",
            use_container_width=True,
            disabled=not st.session_state["df_exists"],
            key="show pump uptime",
        ):
            content_selector = "show_pump_uptime"

    # Generate page content based on the user's choice
    match content_selector:
        case "executed_query":
            # Show success message
            content_placeholder.success(
                f"Query fechted {len(st.session_state['stat_interval_df'])} lines!"
            )
        case "preview_df":
            # Show the chosen dataframe
            content_placeholder.dataframe(
                data=st.session_state["stat_interval_df"], use_container_width=True
            )
        case "show_heatmap":
            figure = create_heatmap_plot(
                st.session_state["stat_interval_df"], st.session_state["config"]
            )
            content_placeholder.plotly_chart(
                figure_or_data=figure, use_container_width=True
            )
        case "show_temp_distribution":
            figure = create_temperature_distribution_chart(
                st.session_state["stat_interval_df"], st.session_state["config"]
            )
            content_placeholder.plotly_chart(
                figure_or_data=figure, use_container_width=True
            )
        case "show_pump_uptime":
            figure = create_pump_diagram(
                st.session_state["stat_interval_df"], st.session_state["config"]
            )
            content_placeholder.plotly_chart(
                figure_or_data=figure, use_container_width=True
            )
