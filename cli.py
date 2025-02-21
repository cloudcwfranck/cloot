
import typer
from flask import Flask, render_template, request, jsonify
from openai_helper import OpenAIHelper
from cloud_auth import CloudAuthManager

app = Flask(__name__)
ai_helper = OpenAIHelper()
cloud_manager = CloudAuthManager()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_endpoint():
    data = request.json
    query = data.get('query', '')
    response = ai_helper.generate_response(query)
    return response

@app.route('/auth/aws', methods=['POST'])
def auth_aws():
    data = request.json
    result = cloud_manager.authenticate_aws(
        data.get('access_key'),
        data.get('secret_key'),
        data.get('command')
    )
    return jsonify({'success': isinstance(result, dict), 'result': result})

@app.route('/deploy', methods=['POST'])
def deploy():
    data = request.json
    provider = data.get('provider')
    command = data.get('command')
    
    if not provider or not command:
        return jsonify({'error': 'Missing provider or command'}), 400
        
    try:
        if provider == 'aws':
            result = cloud_manager.deploy_aws(command)
        elif provider == 'azure':
            result = cloud_manager.deploy_azure(command)
        elif provider == 'gcp':
            result = cloud_manager.deploy_gcp(command)
        else:
            return jsonify({'error': 'Invalid provider'}), 400
            
        return jsonify({'message': 'Deployment successful', 'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/auth/azure', methods=['POST'])
def auth_azure():
    data = request.json
    result = cloud_manager.authenticate_azure(
        data.get('tenant_id'),
        data.get('client_id'),
        data.get('client_secret')
    )
    return jsonify({'success': result is True, 'error': result if isinstance(result, str) else None})

@app.route('/auth/gcp', methods=['POST'])
def auth_gcp():
    data = request.json
    result = cloud_manager.authenticate_gcp(data.get('credentials'))
    return jsonify({'success': result is True, 'error': result if isinstance(result, str) else None})

@app.route('/costs', methods=['GET'])
def get_costs():
    insights = cloud_manager.get_cost_insights()
    return jsonify(insights)

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
