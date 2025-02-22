from flask import Flask, render_template, request, jsonify
from openai_helper import OpenAIHelper

app = Flask(__name__)
ai_helper = OpenAIHelper()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_endpoint():
    data = request.json
    query = data.get('query', '')
    response = ai_helper.generate_response(query)
    return jsonify({
        'response': response,
        'apiCalls': ai_helper.api_calls
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)