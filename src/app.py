import os
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

app = Flask(__name__)

CORS(
    app,
    resources={r"/api/*": {"origins": "http://localhost:3000"}},
    supports_credentials=True
)
# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///dev.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    owner = db.relationship('User', backref=db.backref('items', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat()
        }

# Create tables
with app.app_context():
    db.create_all()

# Routes - Public
@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to Phase 3 API",
        "status": "running",
        "version": "3.0.0",
        "database": "connected",
        "authentication": "enabled"
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validate input
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Username, email, and password are required'}), 400
    
    # Check if user exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 409
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 409
    
    # Create new user
    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': 'User registered successfully',
        'user': user.to_dict()
    }), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400
    
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account is deactivated'}), 403
    
    # Create access token
      # Create access token
    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'token_type': 'Bearer',
        'user': user.to_dict()
    })

# Routes - Protected
@app.route('/api/items', methods=['GET'])
@jwt_required()
def get_items():
    current_user_id = get_jwt_identity()
    items = Item.query.filter_by(user_id=current_user_id).all()
    return jsonify([item.to_dict() for item in items])

@app.route('/api/items', methods=['POST'])
@jwt_required()
def create_item():
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Item name is required'}), 400
    
    item = Item(name=data['name'], description=data.get('description', ''), user_id=current_user_id)
    db.session.add(item)
    db.session.commit()
    
    return jsonify(item.to_dict()), 201

@app.route('/api/items/<int:id>', methods=['GET'])
@jwt_required()
def get_item(id):
    current_user_id = get_jwt_identity()
    item = Item.query.filter_by(id=id, user_id=current_user_id).first_or_404()
    return jsonify(item.to_dict())

@app.route('/api/items/<int:id>', methods=['PUT'])
@jwt_required()
def update_item(id):
    current_user_id = get_jwt_identity()
    item = Item.query.filter_by(id=id, user_id=current_user_id).first_or_404()
    
    data = request.get_json()
    if data:
        item.name = data.get('name', item.name)
        item.description = data.get('description', item.description)
    
    db.session.commit()
    return jsonify(item.to_dict())

@app.route('/api/items/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_item(id):
    current_user_id = get_jwt_identity()
    item = Item.query.filter_by(id=id, user_id=current_user_id).first_or_404()
    
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Item deleted'})

@app.route('/api/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    return jsonify({
        'user': user.to_dict(),
        'item_count': len(user.items)
    })

# Error handlers
@jwt.invalid_token_loader
def invalid_token_loader(error):
    return jsonify({'error': 'Invalid token'}), 401

@jwt.expired_token_loader
def expired_token_loader(jwt_header, jwt_payload):
    return jsonify({'error': 'Token has expired'}), 401

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)