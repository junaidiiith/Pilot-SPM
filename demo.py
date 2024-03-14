import streamlit as st
import json
import os
import streamlit as st
import streamlit_authenticator as stauth
from streamlit_option_menu import option_menu


import yaml
from yaml.loader import SafeLoader

from multiapp import MultiApp
from apps import github, jira, sprint, user_stories
from constants import GITHUB, JIRA, SPRINT, USER_STORIES



app = MultiApp()
app.add_app(GITHUB, github.app)
app.add_app(JIRA, jira.app)
app.add_app(SPRINT, sprint.app)
app.add_app(USER_STORIES, user_stories.app)

st.set_page_config(
    page_title="Smartest Development Plan", 
    page_icon="🧠", 
    layout='centered', 
    initial_sidebar_state="collapsed"
)

with open('authmeta/authentication.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
)

name, authentication_status, username = authenticator.login()

if authentication_status is False:
    st.error("Username or password is incorrect!")
    # show_pages([
    #     Page('demo.py', 'Chat UI', '💬')
    # ])

if authentication_status is None:
    st.warning("Enter your username and password to login!")
    # show_pages([
    #     Page('demo.py', 'Chat UI', '💬')
    # ])
    

if authentication_status:
    os.makedirs('tmp', exist_ok=True)
    authenticator.logout('Logout', 'sidebar')
    st.sidebar.title(f"Welcome {name}!")

    selected = option_menu(
        menu_title=None,  # required
        options=["Home", "About", "Contact"],  # required
        icons=["house", "book", "envelope"],  # optional
        menu_icon="cast",  # optional
        default_index=0,  # optional
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#2596be"},
            "icon": {"color": "orange", "font-size": "25px"},
            "nav-link": {
                "font-size": "25px",
                "text-align": "left",
                "margin": "0px",
                "--hover-color": "#e38e3a",
            },
            "nav-link-selected": {"background-color": "#2596be"},
        },
    )

    # if selected == "Home":
    #     st.session_state['current_page'] = GITHUB
        # st.rerun()

    # st.success(f"Welcome {username}!")
    llm_name = config['credentials']['usernames'][username]['llm']
    llm_configs = json.load(open('llms.json'))
    llm_config = llm_configs[llm_name]

    args = {
        GITHUB: llm_config,
        JIRA: llm_config,
        SPRINT: llm_config,
        USER_STORIES: llm_config
    }

    for app_name, arguments in args.items():
        # print("Setting args for", app_name)
        app.set_args(app_name, arguments)


    current_page = st.session_state.get('current_page', GITHUB)
    # show_pages([
    #     Page('demo.py', 'Chat UI', '💬'),
    #     # Page('modules.py', 'Modules', '📦'),
    # ])

    st.markdown("# Your Smartest Development Plan")

    print("Current page", current_page)
    app.run(current_page)

