import pickle
import os
from collections import defaultdict
import networkx as nx
import json
from tqdm.auto import tqdm
import ast
import pathlib
from collections import deque


modules_classes_file = 'dataset/module_imports_and_classes.json'



def find_nodes_within_distance(graph, start_node, distance):
    q, visited = deque(), dict()
    q.append((start_node, 0))
    
    while q:
        n, d = q.popleft()
        if d <= distance:
            visited[n] = d
            neighbours = [neighbor for neighbor in graph.neighbors(n) if neighbor != n and neighbor not in visited]
            for neighbour in neighbours:
                if neighbour not in visited:
                    q.append((neighbour, d + 1))
    
    sorted_list = sorted(visited.items(), key=lambda x: x[1])
    return sorted_list


def get_all_imports(module_imports_data):
    all_imports = list(set(
        module_import for node in module_imports_data.values()\
            for module_imports in node.values() \
            for module_import in module_imports['imports'])
    )
    return all_imports


def extract_file_paths(module_imports_data):
    node_file_paths = set()
    for file_name, file_contents in module_imports_data.items():
        file_name = file_name.replace('/', '.').replace('.py', '')
        for node_name, _ in file_contents.items():
            node_file_path = f"{file_name}.{node_name}"
            node_file_paths.add(node_file_path)

    node_file_paths = list(node_file_paths)
    return node_file_paths


def get_imports_file_map(module_imports, node_file_paths):
    import_packages_map = defaultdict(list)
    for module_import in tqdm(module_imports, desc='Creating import file map'):
        for fp in node_file_paths:
            if fp.endswith(module_import) and fp.split('.')[-1] == module_import.split('.')[-1]:
                import_packages_map[module_import].append(fp)
    
    return import_packages_map


def get_used_aliases(tree, aliases):
    used_aliases = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            if node.id in aliases:
                import_name = aliases[node.id]
                used_aliases.add(import_name)
    return {u: [] for u in used_aliases}


def create_aliases_dict(tree):
    all_aliases = dict()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                import_as_name = alias.asname if alias.asname else alias.name
                all_aliases[import_as_name] = alias.name

        elif isinstance(node, ast.ImportFrom):
            module_name = node.module
            for alias in node.names:
                import_as_name = alias.asname if alias.asname else alias.name
                all_aliases[import_as_name] = f"{module_name}.{alias.name}"
    return all_aliases


def parse_file(file_path):
    file_contents = open(file_path).read()
    tree = ast.parse(file_contents)
    all_aliases = create_aliases_dict(tree)
    all_nodes_contents = dict()
    visited = set()

    def get_function_details(function_node):
        function_imports = get_used_aliases(function_node, all_aliases)
        details = {
            'type': 'function',
            'imports': function_imports,
            'docstring': ast.get_docstring(function_node),
            'body': ast.get_source_segment(file_contents, function_node),
        }
        return details

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node not in visited:
            class_imports = get_used_aliases(node, all_aliases)
            all_nodes_contents[node.name] = {
                'type': 'class',
                'imports': class_imports,
                'docstring': ast.get_docstring(node),
                'body': ast.get_source_segment(file_contents, node),
                'functions': dict()
            }
            visited.add(node)
            for subnode in ast.walk(node):
                if isinstance(subnode, ast.FunctionDef) and subnode not in visited:
                    all_nodes_contents[node.name]['functions'][subnode.name] = get_function_details(subnode)
                    visited.add(subnode)

        elif isinstance(node, ast.FunctionDef) and node not in visited:
            all_nodes_contents[node.name] = get_function_details(node)
            visited.add(node)

    return all_nodes_contents


def parse_files_in_dir(dir_path):
    pkg_paths = pathlib.Path(dir_path).glob('**/*.py')
    modules = [str(p) for p in pkg_paths]
    all_module_imports = dict()
    for i, module in tqdm(enumerate(modules), total=len(modules), desc='Parsing files'):
        module_imports_and_classes = parse_file(module)
        all_module_imports[module] = module_imports_and_classes
        

    return all_module_imports

def get_init_module_paths(repository):
    pkg_paths = pathlib.Path(repository).glob('**/__init__.py')
    modules = [str(p).replace('/__init__', '') for p in pkg_paths]
    return modules


def get_module_to_file_imports(module_imports_data, init_files):
    module_node_imports = get_all_imports(module_imports_data)
    all_files = list(module_imports_data.keys())
    module_to_file = defaultdict(set)

    for module_imports_node in tqdm(module_node_imports, desc='Creating module to file map'):
        module_imports_node = module_imports_node.split('.')
        node, module_import = module_imports_node[-1], '.'.join(module_imports_node[:-1])
        
        if module_import == '':
            continue
        
        for file in all_files:
            file_name = file.replace('/', '.').replace('.py', '')
            file_nodes = module_imports_data[file]
            if file_name.endswith(module_import) and node in file_nodes:
                module_to_file[module_import].add(file)
        
        for file in init_files:
            file_name = file.replace('/', '.').replace('.py', '')
            if file_name.endswith(module_import):
                module_to_file[module_import].add(file)
        
        # if module_import == 'llama_index.experimental.param_tuner':
        #     print(module_to_file[module_import])
        #     break

    module_to_file = {k: list(v) for k, v in module_to_file.items()}
    with open('module_to_file.json', 'w') as f:
        json.dump(module_to_file, f, indent=4)
        
    return module_to_file


def add_files_to_module_imports(module_imports_data, module_to_file):
    for _, file_contents in module_imports_data.items():
        for _, node_content in file_contents.items():
            imports = node_content['imports']
            new_imports = dict()
            for module_import_node in imports:
                node_module_import = module_import_node.split('.')
                _, module_import = node_module_import[-1], '.'.join(node_module_import[:-1])
                new_imports[module_import_node] = module_to_file[module_import]\
                      if module_import in module_to_file else []
            node_content['imports'] = new_imports


def add_class_node_to_graph(graph, full_class_name, class_content):
    class_name = full_class_name.split('.')[-1]
    if not graph.has_node(full_class_name):
        graph.add_node(full_class_name, type='class')
        graph.nodes[full_class_name]['docstring'] = class_content['docstring']
        graph.nodes[full_class_name]['body'] = class_content['body']
        graph.nodes[full_class_name]['name'] = class_name
        

def add_function_node_to_graph(graph, full_function_name, function_content):
    function_name = full_function_name.split('.')[-1]
    if not graph.has_node(full_function_name):
        graph.add_node(full_function_name, type='function')
        graph.nodes[full_function_name]['docstring'] = function_content['docstring']
        graph.nodes[full_function_name]['body'] = function_content['body']
        graph.nodes[full_function_name]['name'] = function_name


def clean_file_name(name):
    f_name = name.replace('/', '.').replace('.py', '')
    f_name = f_name.replace('.__init__', '') if f_name.endswith('.__init__') else f_name
    return f_name


def create_graph_module_nodes(nxg, file_name):
    fp_units = file_name.split('.')

    ### Create module nodes

    for i in range(1, len(fp_units)):
        u = '.'.join(fp_units[:i])
        v = '.'.join(fp_units[:i + 1])

        if not nxg.has_node(u):
            nxg.add_node(u, name=fp_units[i-1], type='module')
        
        if not nxg.has_node(v):
            nxg.add_node(v, name=fp_units[i], type='module')

        if not nxg.has_edge(u, v):
            nxg.add_edge(u, v, type='module2module')


def create_graph_nodes(nxg, module_imports_data):
    for file_name, file_contents in tqdm(module_imports_data.items(), desc='Creating graph nodes'):
        f_name = clean_file_name(file_name)
        create_graph_module_nodes(nxg, f_name)

        ### Create class and function nodes

        for node_name, node_content in file_contents.items():
            full_node_name = f"{f_name}.{node_name}"
            if node_content['type'] == 'class':
                add_class_node_to_graph(nxg, full_node_name, node_content)
                
                for func_name, func_content in node_content['functions'].items():
                    full_func_name = f"{full_node_name}.{func_name}"
                    add_function_node_to_graph(nxg, full_func_name, func_content)
                    nxg.add_edge(full_node_name, full_func_name, type='class2function')

            elif node_content['type'] == 'function':
                add_function_node_to_graph(nxg, full_node_name, node_content)
            
            nxg.add_edge(f_name, full_node_name, type=f'module2{node_content["type"]}')
            
        

def create_graph_edges(nxg, module_imports_data, module_to_file):
    for file_name, file_contents in tqdm(module_imports_data.items(), desc='Creating graph edges'):
        f_name = clean_file_name(file_name)

        for node_name, node_content in file_contents.items():
            node_module = f"{f_name}.{node_name}"
            imports = node_content['imports']

            for module_imports_node, _ in imports.items():
                module_imports_node = module_imports_node.split('.')
                _, module_import = module_imports_node[-1], '.'.join(module_imports_node[:-1])
                if module_import == '' or module_import not in module_to_file:
                    continue

                module_file = module_to_file[module_import]
                module_file_names = [f.replace('/', '.').replace('.py', '') for f in module_file]
            
                for module_file_name in module_file_names:
                    assert nxg.has_node(node_module), f"Node not found: {node_module}, {file_name}"
                    assert nxg.has_node(module_file_name), f"Module not found: {module_file_name}"
                    nxg.add_edge(node_module, module_file_name, type='module2module')
                    
                    
def create_nxg(module_imports_data, module_to_file):
    nxg = nx.DiGraph()
    # print('Creating graph nodes')
    create_graph_nodes(nxg, module_imports_data)
    # print('Creating graph edges')
    create_graph_edges(nxg, module_imports_data, module_to_file)
    add_parent_attribute(nxg)
    return nxg


def add_parent_attribute(nxg):
    visited = set()
    def dfs_util(node):
        visited.add(node)
        for neighbour in nxg.neighbors(node):
            nxg.nodes[neighbour]['parent'] = node
            if neighbour not in visited:
                dfs_util(neighbour)
    
    for node in nxg.nodes:
        if node not in visited:
            dfs_util(node)

def create_module_graph(repository, f_name=modules_classes_file):
    if os.path.exists(f_name):
        with open(f_name, 'r') as f:
            module_imports_data = json.load(f)
            

    module_imports_data = parse_files_in_dir(repository)
    init_files = get_init_module_paths(repository)
    module_to_file = get_module_to_file_imports(module_imports_data, init_files)
    add_files_to_module_imports(module_imports_data, module_to_file)

    with open(f_name, 'w') as f:
        json.dump(module_imports_data, f, indent=4)
    nxg = create_nxg(module_imports_data, module_to_file)
    write_nxg(f'{repository}_module_graph.gpickle')
    
    return nxg

def load_nxg(repository):
    with open(f'{repository}_module_graph.gpickle', 'rb') as f:
        nxg = pickle.load(f)
    return nxg

def write_nxg(nxg, f_name):
    with open(f_name, 'wb') as f:
        pickle.dump(nxg, f, pickle.HIGHEST_PROTOCOL)