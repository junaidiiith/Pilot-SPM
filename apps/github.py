import streamlit as st
from time import sleep
from llm_chat import add_chat
from constants import JIRA


MAX_COLS = 7
CENTRAL = MAX_COLS // 2
LEFT_END = CENTRAL - min(2, CENTRAL)
RIGHT_END = CENTRAL + min(2, CENTRAL)



def get_repo_summary(path):

    return {
        "title": "Shuup",
        "description": "Shuup is an Open Source E-Commerce Platform based on Django and Python. It is a versatile and flexible platform that can be used to build all kinds of e-commerce solutions. It is a versatile and flexible platform that can be used to build all kinds of e-commerce solutions. It is a versatile and flexible platform that can be used to build all kinds of e-commerce solutions. It is a versatile and flexible platform that can be used to build all kinds of e-commerce solutions. It is a versatile and flexible platform that can be used to build all kinds of e-commerce solutions. It is a versatile and flexible platform that can be used to build all kinds of e-commerce solutions. It is a versatile and flexible platform that can be used to build all kinds of e-commerce solutions. It is a versatile and flexible platform that can be used to build all kinds of e-commerce solutions. It is a versatile and flexible platform that can be used to build all kinds of e-commerce solutions.",
        "tags": ["python", "django", "ecommerce"],
        "modules": {
            "shuup.core": {
                "title": "Shuup Core",
                "description": "Shuup Core is the main module of Shuup",
                "classes": ["Product", "Order", "Customer"],
            },
            "shuup.front": {
                "title": "Shuup Front",
                "description": "Shuup Front is the front end module of Shuup",
                "classes": ["ProductView", "OrderView", "CustomerView"],
            },
            "shuup.admin": {
                "title": "Shuup Admin",
                "description": "Shuup Admin is the admin module of Shuup",
                "classes": ["ProductAdmin", "OrderAdmin", "CustomerAdmin"],
            },
        }
    }

def show_summary(summary):
    st.markdown(f"# {summary['title']}")
    st.markdown(summary['description'])
    st.markdown(f"### Tags: {', '.join(summary['tags'])}")

    st.markdown("## Modules")
    for _, module_info in summary['modules'].items():
        st.markdown(f"### {module_info['title']}")
        st.markdown(module_info['description'])
        st.markdown(f"#### Classes: {', '.join(module_info['classes'])}")


def link_repo(url):
    with st.spinner("Linking your codebase..."):
        sleep(5)

    summary = get_repo_summary(url)
    return summary


def read_repo(zip_file):
    
    with st.spinner("Reading your codebase..."):
        sleep(5)

    summary = get_repo_summary(zip_file)
    return summary
    

def app(llm_config):
    st.markdown("### Link your codebase")
    github_url = st.text_input("Enter GitHub Repo URL")
    cols = st.columns(3)
    with cols[1]:
        link = st.button("Link GitHub Repo")
    
    cols = st.columns(MAX_COLS)
    cols[CENTRAL].markdown("### Or")
    
    zip_file = st.file_uploader("Upload Codebase Zip", type=["zip"])

    cols = st.columns(3)
    with cols[1]:
        read = st.button("Read Codebase")
    
    summary_placeholder = st.empty()

    if link and github_url != "":
        summary = link_repo(github_url)       
        st.session_state['summary'] = summary 

    if read and zip_file is not None:
        summary = read_repo(zip_file)
        st.session_state['summary'] = summary
    
    summary = st.session_state.get('summary', None)
    if summary is not None:
        with summary_placeholder.container():
            show_summary(summary)
        _, project_planning, _ = st.columns(3)
        
        if project_planning.button('### Begin Project Planning'):
            st.session_state['current_page'] = JIRA
            st.rerun()
        

    add_chat(
        llm_config, 
        place_holder_text="Talk to your code!", 
        disabled=not st.session_state.get('summary', False)
    )
