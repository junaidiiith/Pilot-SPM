import json
import os


current_file_dir = os.path.dirname(os.path.abspath(__file__))

PROMPTS_FILE = os.path.join(current_file_dir, "prompts.json")

prompts = json.load(open(PROMPTS_FILE, "r"))

SYSTEM_PROMPT = prompts["system_prompt"]
FUNC_SUMMARIZATION_PROMPT = prompts["function_summarization_prompt"]
CLASS_SUMMARIZATION_PROMPT = prompts["class_summarization_prompt"]
COMBINE_FUNCTION_SUMMARIZATION_PROMPT = prompts["combine_function_summaries"]
COMBINE_CLASS_SUMMARIZATION_PROMPT = prompts["combine_class_summaries"]
COMBINE_MODULE_SUMMARIZATION_PROMPT = prompts["combine_module_summaries"]