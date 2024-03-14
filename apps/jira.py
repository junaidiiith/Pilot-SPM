import json
import pandas as pd
import streamlit as st
from llm_chat import add_chat
from constants import SPRINT

MAX_COLS = 11
CENTRAL = MAX_COLS // 2
LEFT_END = CENTRAL - min(2, CENTRAL)
RIGHT_END = CENTRAL + min(2, CENTRAL)
user_stories_cols = ["title", "userType","description"]


def print_insights(insights_list):
    st.markdown("### Insights")
    st.markdown(f"**Total Insights:** {len(insights_list)}")
    for i, insight in enumerate(insights_list):
        title, description = insight['title'], insight['description']
        st.markdown(f"#### **{i + 1}.** {title}")
        st.markdown(f"**Description:** {description}")
        st.markdown("---")


def print_df(stories_df, key, value):
    df = stories_df.loc[stories_df[key] == value][user_stories_cols]
    for i, story in df.iterrows():
        st.markdown(f"#### {i}. {story['title']}")
        st.markdown(f"**User Type:** {story['userType']}")
        st.markdown(f"**Description:** {story['description']}")
    
    st.markdown("---")


def app(llm_config):
    cols = st.columns(3)
    cols[1].markdown("### Link your Project Management Tool")

    cols = st.columns(5)
    with cols[1]:
        jira = st.button("Connect To Jira")
    
    with cols[3]:
        notion = st.button("Connect To Notion")

    cols = st.columns(MAX_COLS)
    cols[CENTRAL].markdown("### Or")

    user_stories_file = st.file_uploader("Upload Your User Stories", type=["json"])

    cols = st.columns(MAX_COLS)
    with cols[CENTRAL]:
        go = st.button("Go")
    
    if go:
        if user_stories_file is not None:
            with open('tmp/user_stories.json', 'wb') as f:
                f.write(user_stories_file.getvalue())

            user_stories = json.load(open('tmp/user_stories.json', 'rb'))
            user_stories_df = pd.DataFrame(user_stories['user_stories'])
            
            
            user_stories_df.index = [i for i in range(1, len(user_stories_df) + 1)]
            status_container = st.empty()
            with status_container.container():
                not_started, in_progress, done = st.columns(3)
                with not_started:
                    st.markdown("### Not Started ❌")
                    print_df(user_stories_df, 'status', 'not started')
                
                with in_progress:
                    st.markdown("### In Progress 🤔")
                    print_df(user_stories_df, 'status', 'pending')

                with done:
                    st.markdown("### Done ✅")
                    print_df(user_stories_df, 'status', 'completed')


            st.markdown("---")
            print_insights(user_stories['insights'])
            st.session_state['insights_created'] = True
            
    insights_created = st.session_state.get('insights_created', False)
    
    if insights_created:
        cols = st.columns(5)
        fix_sprint = cols[2].button("### Fix Sprint")
        
        if fix_sprint:
            st.session_state['current_page'] = SPRINT
            st.rerun()
            
    add_chat(
        llm_config, 
        place_holder_text="Learn More About Insights from User Stories!", 
        disabled=not insights_created
    )