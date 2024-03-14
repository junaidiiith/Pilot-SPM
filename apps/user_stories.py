import streamlit as st


def app(llm_config):
    st.markdown("### Link your JIRA")
    jira_url = st.text_input("Enter JIRA URL")


