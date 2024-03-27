from llama_index.llms.openai import OpenAI
import streamlit as st
import requests
from prompt_templates.prompts import SYSTEM_PROMPT


openai_apikey = st.secrets["OPENAI_API_KEY"]
hf_api_key = st.secrets['HUGGINGFACEHUB_API_TOKEN']
any_scale_api_key = st.secrets['ANY_SCALE_API_TOKEN']



def get_any_scale_response(any_scale_session, mode_name, user_prompt, system_prompt=SYSTEM_PROMPT):
    api_base = "https://api.endpoints.anyscale.com/v1"
    url = f"{api_base}/chat/completions"
    body = {
        "model": mode_name,
        "messages": [{"role": "system", "content": system_prompt}, 
                    {"role": "user", "content": user_prompt}],
        "temperature": 0.7
    }

    try:
         with any_scale_session.post(url, headers={"Authorization": f"Bearer {any_scale_api_key}"}, json=body) as resp:
            response = resp.json()['choices'][0]['message']['content']
    except Exception as e:
        try:
            shortened_prompt = " ".join(user_prompt.split()[:2500])
            body['messages'][1]['content'] = shortened_prompt
            with any_scale_session.post(url, headers={"Authorization": f"Bearer {any_scale_api_key}"}, json=body) as resp:
                response = resp.json()['choices'][0]['message']['content']

        except Exception as e:
            try:
                shortened_prompt = " ".join(user_prompt.split()[:1200])
                with any_scale_session.post(url, headers={"Authorization": f"Bearer {any_scale_api_key}"}, json=body) as resp:
                    response = resp.json()['choices'][0]['message']['content']
            except Exception as e:
                response = "Error while generating summary"
                print(e)
                print(user_prompt)
    
    return response


def get_gpt_response(prompt):
    try:
        summary = OpenAI(api_key=openai_apikey).complete(prompt)
    except Exception as e:
        try:
            shortened_prompt = " ".join(prompt.split()[:2500])
            summary = OpenAI(api_key=openai_apikey).complete(shortened_prompt)
        except Exception as e:
            shortened_prompt = " ".join(prompt.split()[:1200])
            summary = OpenAI(api_key=openai_apikey).complete(shortened_prompt)
    
    return summary


def get_hf_response(llm_config, prompt):
    model_id = llm_config['model_id']
    headers = {"Authorization": f"Bearer {hf_api_key}"}
    API_URL = f"https://api-inference.huggingface.co/models/{model_id}"
    summary = requests.post(API_URL, headers=headers, json=prompt)
    return summary.json()


def get_llm_response(llm_config, prompt, session=None):
    if llm_config['type'] == 'openai':
        summary = get_gpt_response(prompt)
    elif llm_config['type'] == 'hf':
        summary = get_hf_response(llm_config, prompt)
    elif llm_config['type'] == 'anyscale':
        assert session is not None, "Session cannot be None for AnyScale"
        summary = get_any_scale_response(session, llm_config['model_id'], prompt)
    else:
        raise NotImplementedError
    return summary
