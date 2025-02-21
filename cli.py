
import typer
from flask import Flask, render_template, request, jsonify
from openai_helper import OpenAIHelper
from forum_scraper import scrape_suggestions

app = Flask(__name__)
ai_helper = OpenAIHelper()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])


@app.route('/suggestions')
def get_suggestions():
    suggestions = scrape_suggestions()
    return jsonify(suggestions)


def ask_endpoint():
    data = request.json
    query = data.get('query', '')
    response = ai_helper.generate_response(query)
    return response

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
