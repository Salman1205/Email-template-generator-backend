from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os
import google.generativeai as genai
from rake_nltk import Rake
import random
import requests

app = Flask(__name__)

# Configure CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# SQLAlchemy configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://ateeb_admin:ishaq321!@emailtemplatebyateeb.mysql.database.azure.com/ateeb_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Secret Key for sessions and other purposes
app.secret_key = os.environ.get('SECRET_KEY', '12345678')

# Initialize SQLAlchemy and Bcrypt
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

# Define User Model
class users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Template(db.Model):
    __tablename__ = 'templates'  # Explicitly specify the table name
    
    template_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    template = db.Column(db.Text, nullable=False)
    
    # Define relationship to User
    user = db.relationship('users', backref=db.backref('templates', lazy=True))

    def __repr__(self):
        return f'<Template {self.template_id}>'


# Ensure the database tables are created
with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return jsonify({"message": "Hello from Vercel!"})

@app.route('/register', methods=['POST'])
def register():
    # data = request.get_json()
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    if not username or not email or not password:
        return jsonify({'error': 'Missing fields'}), 400

    # Directly use the password without hashing
    new_user = users(username=username, email=email, password=password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully!'}), 201

@app.route('/login', methods=['POST'])
def login():
    # data = request.get_json()
    email = request.form.get('email')
    password = request.form.get('password')
    print(email,password)
    user = users.query.filter_by(email=email).first()
    if user and user.password == password:
        response_data = {
            'message': 'Login successful!',
            'user_id': user.id,
            'username': user.username,
            'email': user.email
        }
        return jsonify(response_data), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/template', methods=['POST'])
def add_template():
    data = request.get_json()
    user_id = data.get('user_id')
    template_content = data.get('template')
    print(user_id, template_content)

    if not user_id or not template_content:
        return jsonify({
            'error': 'Missing user_id or template content',
            'user_id': user_id,
            'template_content': template_content
        }), 400

    try:
        new_template = Template(userid=user_id, template=template_content)
        db.session.add(new_template)
        db.session.commit()

        return jsonify({'message': 'Template added successfully!'}), 201
    except Exception as e:
        print(f"Error adding template: {e}")
        return jsonify({'error': 'Failed to add template'}), 500

@app.route('/templates', methods=['GET'])
def get_templates(user_id):
    try:
        templates = Template.query.filter_by(userid=user_id).all()
        templates_list = [{'template_id': t.template_id, 'template': t.template} for t in templates]

        if not templates_list:
            return jsonify({'message': 'No templates found for this user'}), 404
        
        return jsonify({'templates': templates_list}), 200
    except Exception as e:
        print(f"Error retrieving templates: {e}")
        return jsonify({'error': 'Failed to retrieve templates'}), 500

if __name__ == "__main__":
    app.run()