from streamlit_extras.stylable_container import stylable_container
from styling import bg_color_template, st_markdown_template, add_properties_to_css
import streamlit as st
from llm_chat import add_chat
from constants import GITHUB, JIRA

bg_color_template = """
{{
        background-color: {color};
        padding: 0.5em;
        border-radius: 1em;
}}
"""

st_markdown_template = """
.stMarkdown {
        padding-right: 1.5em;
    }
"""

def add_properties_to_css(css, **kwargs):
    if not kwargs:
        return css
    return css.format(**kwargs)




def add_fixed_user_story_contents(user_story):
    css_style = add_properties_to_css(bg_color_template, color="#cacecf")

    cols = st.columns([3, 10, 1])
    cols[1].markdown(f"### User Story: {user_story['title']}")

    c1, c2 = st.columns(2)
    with c1:
        with stylable_container(
            key=f"user_story_details",
            css_styles=[
                css_style,
                st_markdown_template
            ]
        ):
            st.markdown(f"#### **Details**")
            
            st.markdown(f"**User Type:** {user_story['userType']}")
            st.markdown(f"**Description:** {user_story['description']}")
    
    with c2:
        with stylable_container(
            key=f"dev_plan",
            css_styles=[
                css_style,
                st_markdown_template
            ]
        ):
            development_plan = user_story['development_plan']
            st.markdown(f"#### **Development Plan**")
            for i, plan in enumerate(development_plan):
                st.markdown(f"**{i + 1}.** {plan}")
    
    
    # with stylable_container(
    #     key=f"extra_kb",
    #     css_styles=[
    #         css_style,
    #         st_markdown_template
    #     ]
    # ):
    st.markdown(f"#### **Extra Knowledge Base**")
    upload_extra_kb = st.file_uploader(f"Upload External Knowledge for {user_story['title']}", type=["json"])


    with stylable_container(
        key=f"relevant_links",
        css_styles=[
            css_style,
            st_markdown_template
        ]
    ):
        relevant_links = user_story['relevant_links']
        st.markdown(f"#### **Relevant Links**")
        for i, relevant_link in enumerate(relevant_links):
            link, label = relevant_link['link'], relevant_link['label']
            st.markdown(f"**{i + 1}.** [{label}]({link})")


def app(llm_config):
    story_to_fix = st.session_state.get('story_to_fix')
    add_fixed_user_story_contents(story_to_fix)

    # user_stories = json.load(open('tmp/user_stories.json', 'rb'))['user_stories']
    # for user_story in user_stories:
    #     with st.expander(user_story['title']):
    #         add_fixed_user_story_contents(user_story)

    # st.markdown("---")

    cols = st.columns([7, 1, 1, 5])

    if cols[0].button("Go Back"):
        st.session_state['current_page'] = JIRA
        st.session_state['came_from_sprint'] = True
        st.rerun()

    # if cols[-1].button("Restart with Codebase Indexing"):
    #     st.session_state['current_page'] = GITHUB
    #     st.session_state['summary'] = None
    #     st.rerun()

    

    add_chat(
        llm_config, 
        place_holder_text="How can I help you?", 
        disabled=False
    )
    