import streamlit as st
import openai
import random

openai_apikey = st.secrets["OPENAI_API_KEY"]
any_scale_api_key = st.secrets['ANY_SCALE_API_TOKEN']


def get_llm_client(llm_config):
    if llm_config['type'] == 'openai':
        client = openai.OpenAI(api_key=openai_apikey)
    elif llm_config['type'] == 'anyscale':
        client = openai.OpenAI(
            base_url = "https://api.endpoints.anyscale.com/v1",
            api_key=any_scale_api_key
        )
    else:
        raise ValueError('Invalid LLM type')
    
    return client


def get_llm_response(llm_config, messages):
    client = get_llm_client(llm_config)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        while True:
            try:
                chat_completion_response = client.chat.completions.create(
                    model=llm_config['model_id'],
                    messages=messages,
                    stream=True,
                )
                for response in chat_completion_response:
                    full_response += (response.choices[0].delta.content or "")
                    message_placeholder.markdown(full_response + "▌")

            except openai.BadRequestError as e:
                error_message = (e.response.json()['error']['message'] or "")
                if 'PromptTooLongError' in error_message:
                    print("Prompt too long, removing first message...")
                    messages.pop(0)
                

                full_response = ""

            if full_response != "":
                break
        message_placeholder.markdown(full_response)
        
    return full_response

def add_chat(llm_config, place_holder_text, disabled):
    messages = st.session_state.get(f'{place_holder_text}_messages', [])
    for message in messages:
        st.chat_message(message["role"]).markdown(message["content"])

    if prompt := st.chat_input(f"{place_holder_text}...", disabled=disabled):
        st.chat_message("user").markdown(prompt)
        messages.append({"role": "user", "content": prompt})
        response = get_llm_response(llm_config, messages)
        messages.append({"role": "assistant", "content": response})
        st.session_state[f'{place_holder_text}_messages'] = messages


def generate_response():
    responses = [
        "This is an insightful point!",
        "I never thought about it that way.",
        "That's an interesting take on the topic.",
        "You bring up a good argument, let's explore it further.",
        "Let's delve deeper into this subject.",
        "Your perspective is quite unique!",
        "This is a great prompt to consider.",
        "You've touched on a key issue there."
    ]
    return random.choice(responses)
