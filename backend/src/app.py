import os
import secrets
from datetime import datetime, timedelta
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_restx import Api, Resource, fields, Namespace
import resend
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///dev.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['RESTX_MASK_SWAGGER'] = False

# Resend configuration
resend.api_key = os.getenv('RESEND_API_KEY')
RESEND_FROM_EMAIL = os.getenv('RESEND_FROM_EMAIL', 'onboarding@resend.dev')
app.config['FRONTEND_URL'] = os.getenv('FRONTEND_URL', 'http://localhost:3000')

# Initialize extensions
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Create API with Swagger
api = Api(
    app,
    version='1.0.0',
    title='Phase 8 API',
    description='Complete REST API with email verification and password reset',
    doc='/docs',
    contact='your.email@example.com',
    security='Bearer Auth'
)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    email_verified = db.Column(db.Boolean, default=False)
    email_verification_token = db.Column(db.String(255), unique=True)
    password_reset_token = db.Column(db.String(255), unique=True)
    password_reset_expires = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_verification_token(self):
        self.email_verification_token = secrets.token_urlsafe(32)
        return self.email_verification_token

    def generate_reset_token(self):
        self.password_reset_token = secrets.token_urlsafe(32)
        self.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
        return self.password_reset_token

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'email_verified': self.email_verified,
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

# Email functions using Resend
def send_verification_email(user, token):
    """Send email verification email using Resend"""
    verification_url = f"{app.config['FRONTEND_URL']}/verify-email/{token}"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
            .button {{ display: inline-block; padding: 12px 24px; background: #0070f3; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .button:hover {{ background: #0051cc; }}
            .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <h2>Verify Your Email</h2>
        <p>Hi {user.username},</p>
        <p>Thanks for registering! Please verify your email address by clicking the button below:</p>
        <a href="{verification_url}" class="button">Verify Email</a>
        <p>Or copy and paste this link:</p>
        <p style="word-break: break-all; color: #666; background: #f5f5f5; padding: 10px; border-radius: 4px;">{verification_url}</p>
        <p>This link expires in 24 hours.</p>
        <p>If you didn't create this account, please ignore this email.</p>
        <div class="footer">
            <p>Phase 8 App</p>
        </div>
    </body>
    </html>
    """
    
    try:
        email = resend.Emails.send({
            "from": f"Phase 8 App <{RESEND_FROM_EMAIL}>",
            "to": user.email,
            "subject": "Verify Your Email - Phase 8 App",
            "html": html_body
        })
        print(f"Verification email sent: {email}")
        return True
    except Exception as e:
        print(f"Failed to send verification email: {e}")
        return False

def send_welcome_email(user):
    """Send welcome email after verification using Resend"""
    dashboard_url = f"{app.config['FRONTEND_URL']}/dashboard"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
            .button {{ display: inline-block; padding: 12px 24px; background: #0070f3; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <h2 style="color: #0070f3;">Welcome to Phase 8 App! 🎉</h2>
        <p>Hi {user.username},</p>
        <p>Your email has been verified successfully! You're all set up.</p>
        <p>Get started by exploring your dashboard:</p>
        <a href="{dashboard_url}" class="button">Go to Dashboard</a>
        <p>What you can do:</p>
        <ul>
            <li>Create and manage your items</li>
            <li>View your profile and stats</li>
            <li>Access our API documentation</li>
        </ul>
        <p>Need help? Contact us at support@example.com</p>
        <div class="footer">
            <p>Phase 8 App</p>
        </div>
    </body>
    </html>
    """
    
    try:
        email = resend.Emails.send({
            "from": f"Phase 8 App <{RESEND_FROM_EMAIL}>",
            "to": user.email,
            "subject": "Welcome to Phase 8 App!",
            "html": html_body
        })
        print(f"Welcome email sent: {email}")
        return True
    except Exception as e:
        print(f"Failed to send welcome email: {e}")
        return False

def send_password_reset_email(user, token):
    """Send password reset email using Resend"""
    reset_url = f"{app.config['FRONTEND_URL']}/reset-password/{token}"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
            .button {{ display: inline-block; padding: 12px 24px; background: #e74c3c; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .warning {{ background: #fff3cd; border: 1px solid #ffc107; padding: 10px; border-radius: 4px; margin: 20px 0; }}
            .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <h2 style="color: #e74c3c;">Password Reset Request</h2>
        <p>Hi {user.username},</p>
        <p>We received a request to reset your password. Click the button below to reset it:</p>
        <a href="{reset_url}" class="button">Reset Password</a>
        <p>Or copy and paste this link:</p>
        <p style="word-break: break-all; color: #666; background: #f5f5f5; padding: 10px; border-radius: 4px;">{reset_url}</p>
        <div class="warning">
            <strong>⚠️ Important:</strong> This link expires in 1 hour for security reasons.
        </div>
        <p>If you didn't request this, you can safely ignore this email. Your password will remain unchanged.</p>
        <p>For security, don't share this link with anyone.</p>
        <div class="footer">
            <p>Phase 8 App</p>
        </div>
    </body>
    </html>
    """
    
    try:
        email = resend.Emails.send({
            "from": f"Phase 8 App <{RESEND_FROM_EMAIL}>",
            "to": user.email,
            "subject": "Password Reset Request - Phase 8 App",
            "html": html_body
        })
        print(f"Password reset email sent: {email}")
        return True
    except Exception as e:
        print(f"Failed to send password reset email: {e}")
        return False

# Create tables
with app.app_context():
    db.create_all()

# Define API models for Swagger
auth_model = api.model('Auth', {
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password')
})

register_model = api.model('Register', {
    'username': fields.String(required=True, description='Username'),
    'email': fields.String(required=True, description='Email address'),
    'password': fields.String(required=True, description='Password')
})

reset_password_model = api.model('ResetPassword', {
    'token': fields.String(required=True, description='Reset token from email'),
    'password': fields.String(required=True, description='New password')
})

item_model = api.model('Item', {
    'name': fields.String(required=True, description='Item name'),
    'description': fields.String(description='Item description')
})

item_response_model = api.model('ItemResponse', {
    'id': fields.Integer(description='Item ID'),
    'name': fields.String(description='Item name'),
    'description': fields.String(description='Item description'),
    'user_id': fields.Integer(description='Owner user ID'),
    'created_at': fields.DateTime(description='Creation timestamp')
})

user_response_model = api.model('UserResponse', {
    'id': fields.Integer(description='User ID'),
    'username': fields.String(description='Username'),
    'email': fields.String(description='Email address'),
    'email_verified': fields.Boolean(description='Email verification status'),
    'created_at': fields.DateTime(description='Registration timestamp')
})

# Create namespaces
auth_ns = Namespace('Authentication', description='Authentication operations')
api.add_namespace(auth_ns, path='/api')

items_ns = Namespace('Items', description='Item operations')
api.add_namespace(items_ns, path='/api')

profile_ns = Namespace('Profile', description='User profile operations')
api.add_namespace(profile_ns, path='/api')

email_ns = Namespace('Email', description='Email verification and password reset')
api.add_namespace(email_ns, path='/api')

# Authentication endpoints
@auth_ns.route('/register')
class Register(Resource):
    @auth_ns.expect(register_model)
    @auth_ns.response(201, 'User registered successfully', user_response_model)
    @auth_ns.response(400, 'Invalid input')
    @auth_ns.response(409, 'User already exists')
    def post(self):
        """Register a new user and send verification email"""
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('email') or not data.get('password'):
            return {'error': 'Username, email, and password are required'}, 400
        
        if User.query.filter_by(username=data['username']).first():
            return {'error': 'Username already exists'}, 409
        
        if User.query.filter_by(email=data['email']).first():
            return {'error': 'Email already registered'}, 409
        
        user = User(username=data['username'], email=data['email'])
        user.set_password(data['password'])
        token = user.generate_verification_token()
        
        db.session.add(user)
        db.session.commit()
        
        # Send verification email using Resend
        send_verification_email(user, token)
        
        return {
            'message': 'User registered successfully. Please check your email to verify your account.',
            'user': user.to_dict()
        }, 201

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(auth_model)
    @auth_ns.response(200, 'Login successful')
    @auth_ns.response(400, 'Invalid input')
    @auth_ns.response(401, 'Invalid credentials')
    @auth_ns.response(403, 'Email not verified or account deactivated')
    def post(self):
        """Login and get JWT access token"""
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return {'error': 'Username and password required'}, 400
        
        user = User.query.filter_by(username=data['username']).first()
        
        if not user or not user.check_password(data['password']):
            return {'error': 'Invalid username or password'}, 401
        
        if not user.email_verified:
            return {'error': 'Please verify your email before logging in'}, 403
        
        if not user.is_active:
            return {'error': 'Account is deactivated'}, 403
        
        access_token = create_access_token(identity=user.id)
        
        return {
            'message': 'Login successful',
            'access_token': access_token,
            'token_type': 'Bearer',
            'user': user.to_dict()
        }

# Email verification endpoints
@email_ns.route('/verify-email/<token>')
class VerifyEmail(Resource):
    @email_ns.doc('verify_email')
    @email_ns.response(200, 'Email verified successfully')
    @email_ns.response(400, 'Invalid or expired token')
    def get(self, token):
        """Verify email address with token from email"""
        user = User.query.filter_by(email_verification_token=token).first()
        
        if not user:
            return {'error': 'Invalid verification token'}, 400
        
        # Check if token is expired (24 hours)
        if datetime.utcnow() - user.created_at > timedelta(hours=24):
            return {'error': 'Verification token has expired'}, 400
        
        user.email_verified = True
        user.email_verification_token = None
        db.session.commit()
        
        # Send welcome email using Resend
        send_welcome_email(user)
        
        return {'message': 'Email verified successfully! You can now login.'}

@email_ns.route('/resend-verification')
class ResendVerification(Resource):
    @email_ns.expect(api.model('ResendVerification', {
        'email': fields.String(required=True, description='Email address')
    }))
    @email_ns.response(200, 'Verification email sent')
    @email_ns.response(404, 'User not found')
    def post(self):
        """Resend verification email"""
        data = request.get_json()
        
        if not data or not data.get('email'):
            return {'error': 'Email is required'}, 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user:
            return {'error': 'User not found'}, 404
        
        if user.email_verified:
            return {'error': 'Email already verified'}, 400
        
        token = user.generate_verification_token()
        db.session.commit()
        
        send_verification_email(user, token)
        
        return {'message': 'Verification email sent. Please check your inbox.'}

# Password reset endpoints
@email_ns.route('/forgot-password')
class ForgotPassword(Resource):
    @email_ns.expect(api.model('ForgotPassword', {
        'email': fields.String(required=True, description='Email address')
    }))
    @email_ns.response(200, 'Password reset email sent')
    @email_ns.response(404, 'User not found')
    def post(self):
        """Request password reset email"""
        data = request.get_json()
        
        if not data or not data.get('email'):
            return {'error': 'Email is required'}, 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user:
            # Don't reveal if email exists for security
            return {'message': 'If the email exists, a password reset link has been sent.'}
        
        token = user.generate_reset_token()
        db.session.commit()
        
        send_password_reset_email(user, token)
        
        return {'message': 'If the email exists, a password reset link has been sent.'}

@email_ns.route('/reset-password')
class ResetPassword(Resource):
    @email_ns.expect(reset_password_model)
    @email_ns.response(200, 'Password reset successful')
    @email_ns.response(400, 'Invalid or expired token')
    def post(self):
        """Reset password with token from email"""
        data = request.get_json()
        
        if not data or not data.get('token') or not data.get('password'):
            return {'error': 'Token and new password are required'}, 400
        
        if len(data['password']) < 6:
            return {'error': 'Password must be at least 6 characters'}, 400
        
        user = User.query.filter_by(password_reset_token=data['token']).first()
        
        if not user:
            return {'error': 'Invalid reset token'}, 400
        
        # Check if token is expired
        if not user.password_reset_expires or datetime.utcnow() > user.password_reset_expires:
            return {'error': 'Reset token has expired'}, 400
        
        user.set_password(data['password'])
        user.password_reset_token = None
        user.password_reset_expires = None
        db.session.commit()
        
        return {'message': 'Password reset successful. You can now login with your new password.'}

# Items endpoints
@items_ns.route('/items')
class ItemsList(Resource):
    @items_ns.doc('list_items')
    @items_ns.marshal_list_with(item_response_model)
    @items_ns.response(200, 'Success')
    @items_ns.response(401, 'Token required')
    @items_ns.doc(security='Bearer')
    @jwt_required()
    def get(self):
        """Get all items for the authenticated user"""
        current_user_id = get_jwt_identity()
        items = Item.query.filter_by(user_id=current_user_id).all()
        return [item.to_dict() for item in items]

    @items_ns.doc('create_item')
    @items_ns.expect(item_model)
    @items_ns.marshal_with(item_response_model, code=201)
    @items_ns.response(201, 'Item created successfully')
    @items_ns.response(400, 'Invalid input')
    @items_ns.response(401, 'Token required')
    @items_ns.doc(security='Bearer')
    @jwt_required()
    def post(self):
        """Create a new item"""
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('name'):
            return {'error': 'Item name is required'}, 400
        
        item = Item(name=data['name'], description=data.get('description', ''), user_id=current_user_id)
        db.session.add(item)
        db.session.commit()
        
        return item.to_dict(), 201

@items_ns.route('/items/<int:id>')
@items_ns.param('id', 'The item ID')
@items_ns.response(404, 'Item not found')
class ItemResource(Resource):
    @items_ns.doc('get_item')
    @items_ns.marshal_with(item_response_model)
    @items_ns.response(200, 'Success')
    @items_ns.response(401, 'Token required')
    @items_ns.doc(security='Bearer')
    @jwt_required()
    def get(self, id):
        """Get a specific item by ID"""
        current_user_id = get_jwt_identity()
        item = Item.query.filter_by(id=id, user_id=current_user_id).first_or_404()
        return item.to_dict()

    @items_ns.doc('update_item')
    @items_ns.expect(item_model)
    @items_ns.marshal_with(item_response_model)
    @items_ns.response(200, 'Item updated successfully')
    @items_ns.response(401, 'Token required')
    @items_ns.response(404, 'Item not found')
    @items_ns.doc(security='Bearer')
    @jwt_required()
    def put(self, id):
        """Update an existing item"""
        current_user_id = get_jwt_identity()
        item = Item.query.filter_by(id=id, user_id=current_user_id).first_or_404()
        
        data = request.get_json()
        if data:
            item.name = data.get('name', item.name)
            item.description = data.get('description', item.description)
        
        db.session.commit()
        return item.to_dict()

    @items_ns.doc('delete_item')
    @items_ns.response(200, 'Item deleted successfully')
    @items_ns.response(401, 'Token required')
    @items_ns.response(404, 'Item not found')
    @items_ns.doc(security='Bearer')
    @jwt_required()
    def delete(self, id):
        """Delete an item"""
        current_user_id = get_jwt_identity()
        item = Item.query.filter_by(id=id, user_id=current_user_id).first_or_404()
        
        db.session.delete(item)
        db.session.commit()
        return {'message': 'Item deleted'}

# Profile endpoint
@profile_ns.route('/profile')
class Profile(Resource):
    @profile_ns.doc('get_profile')
    @profile_ns.marshal_with(api.model('ProfileResponse', {
        'user': fields.Nested(user_response_model),
        'item_count': fields.Integer(description='Total items owned by user')
    }))
    @profile_ns.response(200, 'Success')
    @profile_ns.response(401, 'Token required')
    @profile_ns.doc(security='Bearer')
    @jwt_required()
    def get(self):
        """Get authenticated user's profile"""
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        return {
            'user': user.to_dict(),
            'item_count': len(user.items)
        }

# Health check
@app.route('/health')
def health():
    """Health check endpoint"""
    return {'status': 'healthy'}

# Error handlers
@jwt.invalid_token_loader
def invalid_token_loader(error):
    return {'error': 'Invalid token'}, 401

@jwt.expired_token_loader
def expired_token_loader(jwt_header, jwt_payload):
    return {'error': 'Token has expired'}, 401

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8000))
    debug = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
