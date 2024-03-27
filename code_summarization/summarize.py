import os
from prompt_templates.prompts import (
    FUNC_SUMMARIZATION_PROMPT, 
    COMBINE_FUNCTION_SUMMARIZATION_PROMPT,
    CLASS_SUMMARIZATION_PROMPT,
    COMBINE_CLASS_SUMMARIZATION_PROMPT,
    COMBINE_MODULE_SUMMARIZATION_PROMPT
)
from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter,
)


CHUNK_SIZE = 3000
CHUNK_OVERLAP = 500
python_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)

summaries_dir = 'summaries'

def summarize_docs(document, node_prompt, combine_prompt):
    docs = python_splitter.create_documents([document])
    split_summaries = list()
    for doc in docs:
        prompt = f"{node_prompt}\n\n{doc.page_content}"
        # summary = get_llm_response(prompt)
        summary = f"Summary of: {prompt}"
        split_summaries.append(summary)
    
    summaries = "\n".join(split_summaries)
    combine_summary_prompt = f"{combine_prompt}\n\n{summaries}"
    # response = get_llm_response(combine_summary_prompt)
    response = f"Summary of: {combine_summary_prompt}"
    return response


def summarize_code_node(node, nxg):
    node_type = nxg.nodes[node]['type']
    body = nxg.nodes[node]['body']
    node_prompt = FUNC_SUMMARIZATION_PROMPT \
        if node_type == 'function' else CLASS_SUMMARIZATION_PROMPT
    combine_prompt = COMBINE_FUNCTION_SUMMARIZATION_PROMPT \
        if node_type == 'function' else COMBINE_CLASS_SUMMARIZATION_PROMPT
    summary = summarize_docs(body, node_prompt, combine_prompt)
    return summary


def summarize_module_node(node, nxg):
    node_summaries = list()
    for neighbour in nxg.neighbors(node):
        summary = summarize_node(neighbour, nxg)
        node_summaries.append((neighbour, summary))
    
    combined_summary = "\n".join([f"{n}:\n{s}" for n, s in node_summaries])
    node_prompt = COMBINE_MODULE_SUMMARIZATION_PROMPT
    combine_prompt = COMBINE_MODULE_SUMMARIZATION_PROMPT
    summary = summarize_docs(combined_summary, node_prompt, combine_prompt)
    return summary


def summarize_node(node, nxg):
    os.makedirs(summaries_dir, exist_ok=True)
    if os.path.exists(f"{summaries_dir}/{node}.txt"):
        with open(f"{summaries_dir}/{node}.txt", 'r') as f:
            return f.read()

    node_type = nxg.nodes[node]['type']
    summary = summarize_module_node(node, nxg) if node_type == 'module' else summarize_code_node(node, nxg)
    
    with open(f"{summaries_dir}/{node}.txt", 'w') as f:
        f.write(summary)