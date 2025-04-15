from flask import Flask
app = Flask(__name__)

@app.route('/')  # This decorator is REQUIRED for the root URL
def home():
    return "Hello World!"  # Simple response to verify it works

if __name__ == '__main__':
    app.run(port=5001, debug=True)  # Explicit port