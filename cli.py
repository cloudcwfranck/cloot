from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import os
from datetime import datetime
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from openai_helper import OpenAIHelper
from models import db, User, Question, Folder

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['STRIPE_PUBLIC_KEY'] = 'your_stripe_public_key'
app.config['STRIPE_SECRET_KEY'] = 'your_stripe_secret_key'

import stripe
stripe.api_key = app.config['STRIPE_SECRET_KEY']

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
def landing():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('landing.html')

@app.route('/home')
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
        if current_user.credits <= 0:
            return jsonify({
                'error': 'No credits remaining',
                'upgrade_required': True,
                'upgrade_url': url_for('upgrade')
            }), 403

        if not request.is_json:
            print("Error: Request is not JSON")
            return jsonify({'error': 'Request must be JSON'}), 400
            
        data = request.json
        print(f"Request data: {data}")
        if not data or 'query' not in data:
            print("Error: No query in request data")
            return jsonify({'error': 'No query provided'}), 400
            
        query = data.get('query', '').strip()
        if not query:
            return jsonify({'error': 'Empty query'}), 400
            
        print(f"Processing query: {query}")
        
        # Check for duplicate recent questions
        last_question = db.session.query(Question).filter_by(
            user_id=current_user.id,
            query=query
        ).order_by(Question.timestamp.desc()).first()
        
        if last_question and (datetime.utcnow() - last_question.timestamp).total_seconds() < 5:
            return jsonify({
                'response': last_question.response,
                'apiCalls': ai_helper.api_calls
            })
        
        try:
            response = ai_helper.generate_response(query)
            print(f"AI Response: {response}")
            
            if response.startswith('Error:'):
                print(f"Error in response: {response}")
                return jsonify({'error': response}), 500
            elif not response:
                print("Empty response received")
                return jsonify({'error': 'Empty response from AI'}), 500
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return jsonify({'error': f'Failed to generate response: {str(e)}'}), 500
            
        # Store the question
        try:
            question = Question(
                query=query,
                response=response,
                user_id=current_user.id
            )
            db.session.add(question)
            current_user.credits -= 1
            db.session.commit()
            print(f"Stored question in database: {query}")
            
            return jsonify({
                'response': response,
                'apiCalls': ai_helper.api_calls,
                'credits_remaining': current_user.credits
            })
        except Exception as e:
            db.session.rollback()
            print(f"Database error: {str(e)}")
            return jsonify({'error': 'Database error occurred'}), 500
            
    except Exception as e:
        print(f"Unexpected error in ask_endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
@app.route('/upgrade')
@login_required
def upgrade():
    return render_template('upgrade.html', stripe_public_key=app.config['STRIPE_PUBLIC_KEY'])

@app.route('/folders', methods=['GET', 'POST'])
@login_required
def folders():
    if request.method == 'POST':
        folder_name = request.form.get('folder_name')
        if not folder_name:
            flash('Folder name cannot be empty')
            return redirect(url_for('folders'))
            
        new_folder = Folder(name=folder_name, user_id=current_user.id)
        db.session.add(new_folder)
        db.session.commit()
        flash(f'Folder "{folder_name}" created successfully')
        
    folders = Folder.query.filter_by(user_id=current_user.id).all()
    return render_template('folders.html', folders=folders)

@app.route('/folders/<int:folder_id>', methods=['GET'])
@login_required
def folder_details(folder_id):
    folder = Folder.query.filter_by(id=folder_id, user_id=current_user.id).first_or_404()
    questions = Question.query.filter_by(folder_id=folder_id).order_by(Question.timestamp.desc()).all()
    return render_template('folder_details.html', folder=folder, questions=questions)

@app.route('/folders/<int:folder_id>/delete', methods=['POST'])
@login_required
def delete_folder(folder_id):
    folder = Folder.query.filter_by(id=folder_id, user_id=current_user.id).first_or_404()
    
    # Move all questions to 'unfiled' (set folder_id to None)
    Question.query.filter_by(folder_id=folder_id).update({Question.folder_id: None})
    
    db.session.delete(folder)
    db.session.commit()
    flash(f'Folder "{folder.name}" deleted successfully')
    return redirect(url_for('folders'))

@app.route('/questions/<int:question_id>/move', methods=['POST'])
@login_required
def move_question(question_id):
    question = Question.query.filter_by(id=question_id, user_id=current_user.id).first_or_404()
    folder_id = request.form.get('folder_id')
    
    if folder_id == '':
        question.folder_id = None
    else:
        folder = Folder.query.filter_by(id=folder_id, user_id=current_user.id).first_or_404()
        question.folder_id = folder.id
        
    db.session.commit()
    return jsonify({'success': True})

@app.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout():
    plan = request.form.get('plan')
    
    if plan == 'annual':
        price = 1000  # $10.00
        interval = 'year'
    else:
        price = 1500  # $15.00
        interval = 'month'
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': price,
                    'product_data': {
                        'name': f'Cloot {interval.capitalize()} Plan',
                    },
                    'recurring': {
                        'interval': interval,
                    }
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.host_url + 'payment-success',
            cancel_url=request.host_url + 'upgrade',
            customer_email=current_user.username
        )
        return jsonify({'id': checkout_session.id})
    except Exception as e:
        return jsonify({'error': str(e)}), 403

@app.route('/payment-success')
@login_required
def payment_success():
    return render_template('payment_success.html')
