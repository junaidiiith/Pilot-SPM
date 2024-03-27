import openai
import streamlit as st
import requests
from prompt_templates.prompts import SYSTEM_PROMPT


openai_apikey = st.secrets["OPENAI_API_KEY"]
hf_api_key = st.secrets['HUGGINGFACEHUB_API_TOKEN']
any_scale_api_key = st.secrets['ANY_SCALE_API_TOKEN']


def get_llm_response(client, model_name, prompt, system_prompt):
    chat_completion = client.chat.completions.create(
        model=f"{model_name}",
        messages=[{"role": "system", "content": f"{system_prompt}"},
                {"role": "user", "content": prompt}],
        temperature=0.7
    )

    try:
        response = chat_completion.choices[0].message.content
    except Exception as e:
        response = "Error while generating summary"
        print(e)
        print(prompt)

    return response


def get_any_scale_response(mode_name, user_prompt, system_prompt):
    client = openai.OpenAI(
        base_url = "https://api.endpoints.anyscale.com/v1",
        api_key=f"{any_scale_api_key}"
    )
    response = get_llm_response(client, mode_name, user_prompt, system_prompt)
    return response


def get_gpt_response(model_name, user_prompt, system_prompt):
    client = openai.OpenAI(api_key=f"{openai_apikey}")
    response = get_llm_response(client, model_name, user_prompt, system_prompt)
    return response


def get_hf_response(model_name, prompt):
    headers = {"Authorization": f"Bearer {hf_api_key}"}
    API_URL = f"https://api-inference.huggingface.co/models/{model_name}"
    summary = requests.post(API_URL, headers=headers, json=prompt)
    return summary.json()


class LLM():
    def __init__(self, llm_config):
        self.model_name = llm_config['model_id']
        self.model_type = llm_config['type']

    def get_response(self, prompt, system_prompt=SYSTEM_PROMPT):
        if self.model_type == 'openai':
            summary = get_gpt_response(self.model_name, prompt, system_prompt)
        elif self.model_type == 'hf':
            summary = get_hf_response(self.model_name, prompt, system_prompt)
        elif self.model_type == 'anyscale':
            summary = get_any_scale_response(self.model_name, prompt, system_prompt)
        else:
            raise NotImplementedError
        return summary