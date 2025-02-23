from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from datetime import datetime
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from openai_helper import OpenAIHelper
from models import db, User, Question

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

ai_helper = OpenAIHelper()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('home'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/ask', methods=['POST'])
@login_required
def ask_endpoint():
    print("Received request at /ask endpoint")
    try:
        if not request.is_json:
            print("Error: Request is not JSON")
            return jsonify({'error': 'Request must be JSON'}), 400
            
        data = request.json
        print(f"Request data: {data}")
        if not data or 'query' not in data:
            print("Error: No query in request data")
            return jsonify({'error': 'No query provided'}), 400
            
        query = data.get('query', '')
        if not query.strip():
            return jsonify({'error': 'Empty query'}), 400
        
        # Check if this exact question was just asked in the last few seconds
        last_question = Question.query.filter_by(
            user_id=current_user.id,
            query=query
        ).order_by(Question.timestamp.desc()).first()
        
        if last_question and (datetime.utcnow() - last_question.timestamp).total_seconds() < 5:
            return jsonify({
                'response': last_question.response,
                'apiCalls': ai_helper.api_calls
            })
        
        print(f"Sending query to OpenAI: {query}")
        response = ai_helper.generate_response(query)
        print(f"OpenAI response: {response}")
        if response.startswith('Error:'):
            print(f"Error detected in response: {response}")
            return jsonify({'error': response}), 500
    
    # Store the question
        try:
            question = Question(
                query=query,
                response=response,
                user_id=current_user.id
            )
            db.session.add(question)
            db.session.commit()
            
            return jsonify({
                'response': response,
                'apiCalls': ai_helper.api_calls
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Database error occurred'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)