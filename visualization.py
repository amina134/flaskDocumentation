from pyvis.network import Network
import ast
import hashlib
from documentation import generate_enhanced_docs

def create_code_visualization(code):
    try:
        tree = ast.parse(code)
        net = Network(height="750px", width="100%", directed=True)
        
        # Add nodes
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_hash = hashlib.md5(node.name.encode()).hexdigest()[:8]
                net.add_node(
                    func_hash,
                    label=node.name,
                    title=generate_enhanced_docs(ast.unparse(node)),
                    shape="box",
                    color="#e8f4f8"
                )
                
                # Add edges
                for call in ast.walk(node):
                    if isinstance(call, ast.Call) and isinstance(call.func, ast.Name):
                        called_hash = hashlib.md5(call.func.id.encode()).hexdigest()[:8]
                        net.add_edge(func_hash, called_hash, label="calls", color="#6a9fb5")
        
        filename = f"static/graph_{hashlib.md5(code.encode()).hexdigest()[:8]}.html"
        net.show(filename)
        return filename
        
    except Exception as e:
        print(f"Visualization error: {str(e)}")
        return None