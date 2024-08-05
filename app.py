from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os

app = Flask(__name__)

# Configure CORS
CORS(app, resources={r"/*": {"origins": "*"}})  # You can restrict origins if needed

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

    def __repr__(self):
        return f'<User {self.username}>'

class Template(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    template = db.Column(db.Text, nullable=False)
    user = db.relationship('User', backref=db.backref('templates', lazy=True))

    def __repr__(self):
        return f'<Template {self.id}>'

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
    user = user.query.filter_by(email=email).first()
    if user and user.password == password:
        # Prepare the response with user details
        response_data = {
            'message': 'Login successful!',
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'password': user.password
        }
        return jsonify(response_data), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401


@app.route('/template', methods=['POST'])
def add_template():
    user_id = request.form.get('user_id')
    template_content = request.form.get('template')

    if not user_id or not template_content:
        return jsonify({'error': 'Missing user_id or template content'}), 400

    try:
        new_template = Template(user_id=user_id, template=template_content)
        db.session.add(new_template)
        db.session.commit()

        return jsonify({'message': 'Template added successfully!'}), 201
    except Exception as e:
        print(f"Error adding template: {e}")
        return jsonify({'error': 'Failed to add template'}), 500

if __name__ == "__main__":
    app.run()
