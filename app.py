from flask import Flask, request, jsonify, render_template
from flask_cors import CORS  # Important for AJAX requests
import subprocess
import os
from pathlib import Path
from documentation import generate_enhanced_docs 
app = Flask(__name__)
CORS(app)
app.config['PROPAGATE_EXCEPTIONS'] = True  # ← Add this line
# In app.py, add after Flask initialization
app.config['WTF_CSRF_ENABLED'] = False
app.config['DEBUG'] = True  # Also recommended during development
documentation_db = {}

import traceback

@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({
        "error": str(e),
        "traceback": traceback.format_exc()
    }), 500







# Your routes here...
@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/document', methods=['POST'])
def document_code():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data received"}), 400
            
        code = data.get('code')
        if not code:
            return jsonify({"error": "Missing code parameter"}), 400
            
        docs = generate_enhanced_docs(code)
        documentation_db[code] = docs  # Store in cache
        return jsonify({"documentation": docs})
        
    except Exception as e:
        app.logger.error(f"Error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500


@app.route('/ask', methods=['POST'])  
def ask_question():  
    code = request.json['code']  
    question = request.json['question']  

    # Get existing documentation or generate it if not present.  
    docs = documentation_db.get(code, generate_enhanced_docs(code))  
    
    # Construct a prompt with the question and existing documentation  
    # prompt = f"""  
    Documentation Context:  
    {docs}  
    
    Question:  
    {question}  
    
    Answer concisely with code examples where appropriate, especially for complexity analysis.  
    """  
    
    # Call the model to get an answer based on the prompt  
    result = subprocess.run(  
        f'ollama run deepseek-coder "{prompt}"',  
        shell=True,  
        capture_output=True,  
        text=True  
    )  
    
    return jsonify({"answer": result.stdout.strip()})  



if __name__ == '__main__':  
    app.run(host='0.0.0.0', port=5001, debug=True) 