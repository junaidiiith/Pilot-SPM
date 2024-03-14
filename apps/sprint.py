import json
import streamlit as st
from llm_chat import add_chat
from constants import GITHUB


def add_fixed_user_story_contents(user_story):

    c1, c2 = st.columns(2)
    with c1.container():
        st.markdown(f"#### **User Story**")
        st.markdown(f"**Title:** {user_story['title']}")
        st.markdown(f"**User Type:** {user_story['userType']}")
        st.markdown(f"**Description:** {user_story['description']}")
    
    with c2.container():
        development_plan = user_story['development_plan']
        st.markdown(f"#### **Development Plan**")
        for i, plan in enumerate(development_plan):
            st.markdown(f"**{i + 1}.** {plan}")
    
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1.container():
        st.markdown(f"#### **Extra KB**")
        upload_extra_kb = st.file_uploader(f"Upload External Knowledge for {user_story['title']}", type=["json"])
    
    with c2.container():
        relevant_links = user_story['relevant_links']
        st.markdown(f"#### **Relevant Links**")
        for i, relevant_link in enumerate(relevant_links):
            link, label = relevant_link['link'], relevant_link['label']
            st.markdown(f"**{i + 1}.** [{label}]({link})")

    st.markdown("---")


def app(llm_config):
    
    cols = st.columns(3)
    cols[1].markdown("### Fixed User Stories")

    user_stories = json.load(open('tmp/user_stories.json', 'rb'))['user_stories']
    for user_story in user_stories:
        with st.expander(user_story['title']):
            add_fixed_user_story_contents(user_story)

    st.markdown("---")

    cols = st.columns(3)
    if cols[1].button("Restart with Codebase Indexing"):
        st.session_state['current_page'] = GITHUB
        st.session_state['summary'] = None
        st.rerun()

    add_chat(
        llm_config, 
        place_holder_text="How can I help you?", 
        disabled=False
    )
    