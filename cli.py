
import typer
from flask import Flask, render_template, request, jsonify
from openai_helper import OpenAIHelper

app = Flask(__name__)
ai_helper = OpenAIHelper()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_endpoint():
    query = request.form.get('query', '')
    file = request.files.get('file')
    
    file_content = None
    if file:
        file_content = file.read().decode('utf-8')
    
    try:
        response = ai_helper.generate_response(query, file_content)
        return jsonify({
            'response': response,
            'apiCalls': ai_helper.api_calls
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

@app.command()
def ask(
    query: str = typer.Argument(..., help="Your cloud engineering question or request"),
):
    """
    Ask CloudBot to generate cloud commands or provide explanations
    """
    with console.status("[bold green]Generating response..."):
        response = ai_helper.generate_response(query)
        
    console.print(Panel(
        Markdown(response),
        title="CloudBot Response",
        border_style="blue"
    ))

@app.command()
def version():
    """Display the current version of CloudBot"""
    console.print("CloudBot v1.0.0")
