if __name__ == '__main__':
    import json
    from module_graph.generate import load_nxg
    from code_summarization.llm_utils import LLM
    from code_summarization.summarize import summarize_node
    from tqdm.auto import tqdm

    repository = 'llama_index_local'
    nxg = load_nxg(repository)
    llms = json.load(open('llms.json', 'r'))

    llm = LLM(llms['mistral8x7b'])
    for node in tqdm(nxg.nodes, total=nxg.number_of_nodes()):
        summarize_node(llm, node, nxg)
        # break