import subprocess  
from flask import Flask, request, jsonify, render_template  
from flask_cors import CORS  

app = Flask(__name__)  
CORS(app)  
documentation_db = {}  

def generate_enhanced_docs(code):  
    try:  
        result = subprocess.run(  
            f'ollama run deepseek-coder "Document this code: {code}"',  
            shell=True,  
            capture_output=True,  
            text=True,  
            timeout=60  
        )  
        if result.returncode != 0:  
            raise Exception(f"Ollama error: {result.stderr.strip()}")  
        return result.stdout.strip()  # Clean up and return the output  
    except subprocess.TimeoutExpired:  
        return "Documentation generation timed out."  
    except Exception as e:  
        print(f"Error: {str(e)}")  # Debugging output  
        return "Failed to generate documentation."   

@app.route('/')  
def index():  
    return render_template('upload.html')  

@app.route('/document', methods=['POST'])  
def document_code():  
    try:  
        data = request.get_json()  
        if not data or 'code' not in data:  
            return jsonify({"error": "Invalid request"}), 400  
            
        code = data['code']  
        docs = generate_enhanced_docs(code)  
        documentation_db[code] = docs  # Cache documents  
        return jsonify({"documentation": docs})  
        
    except Exception as e:  
        return jsonify({"error": str(e)}), 500  

@app.route('/ask', methods=['POST'])  
def ask_question():  
    try:  
        code = request.json['code']  
        question = request.json['question']  
        docs = documentation_db.get(code, generate_enhanced_docs(code))  # Generate if not present  
        
        # Construct a prompt for the answer  
        prompt = f"""Documentation Context:\n{docs}\nQuestion:\n{question}\nAnswer concisely with code examples where appropriate."""  
        
        result = subprocess.run(  
            f'ollama run deepseek-coder "{prompt}"',  
            shell=True,  
            capture_output=True,  
            text=True  
        )  
        
        return jsonify({"answer": result.stdout.strip()})  
    except Exception as e:  
        return jsonify({"error": str(e)}), 500  

if __name__ == '__main__':  
    app.run(host='0.0.0.0', port=5001, debug=True)