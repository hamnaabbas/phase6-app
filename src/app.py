import os
from datetime import datetime, timedelta

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from flask_restx import Api, Resource, fields, Namespace
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)


# ============================================================
# CORS
# ============================================================

# Allow React frontend running on localhost:3000
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": "http://localhost:3000"
        }
    },
    supports_credentials=True
)


# ============================================================
# CONFIGURATION
# ============================================================

app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY",
    "dev-secret-key"
)

app.config["JWT_SECRET_KEY"] = os.getenv(
    "JWT_SECRET_KEY",
    "dev-jwt-secret"
)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "sqlite:///dev.db"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# JWT expires after 1 hour
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

# Disable Flask-RESTX response masking
app.config["RESTX_MASK_SWAGGER"] = False


# ============================================================
# INITIALIZE EXTENSIONS
# ============================================================

db = SQLAlchemy(app)

jwt = JWTManager(app)


# ============================================================
# SWAGGER / RESTX CONFIGURATION
# ============================================================

authorizations = {
    "Bearer Auth": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization",
        "description": (
            "Enter your JWT token using this format: "
            "Bearer YOUR_ACCESS_TOKEN"
        )
    }
}


api = Api(
    app,
    version="1.0.0",
    title="Phase 5 REST API",
    description=(
        "Complete REST API with JWT authentication, "
        "user registration, login, profile and CRUD operations."
    ),
    doc="/docs",
    authorizations=authorizations,
    security="Bearer Auth"
)


# ============================================================
# DATABASE MODELS
# ============================================================

class User(db.Model):

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(80),
        unique=True,
        nullable=False,
        index=True
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    is_active = db.Column(
        db.Boolean,
        default=True
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(
            self.password_hash,
            password
        )

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat()
            if self.created_at else None,
            "is_active": self.is_active
        }


class Item(db.Model):

    __tablename__ = "items"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    description = db.Column(
        db.String(255)
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    owner = db.relationship(
        "User",
        backref=db.backref(
            "items",
            lazy=True
        )
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat()
            if self.created_at else None
        }


# ============================================================
# CREATE DATABASE TABLES
# ============================================================

with app.app_context():
    db.create_all()


# ============================================================
# SWAGGER MODELS
# ============================================================

auth_model = api.model(
    "Login",
    {
        "username": fields.String(
            required=True,
            description="Username"
        ),

        "password": fields.String(
            required=True,
            description="Password"
        )
    }
)


register_model = api.model(
    "Register",
    {
        "username": fields.String(
            required=True,
            description="Username"
        ),

        "email": fields.String(
            required=True,
            description="Email address"
        ),

        "password": fields.String(
            required=True,
            description="Password"
        )
    }
)


item_model = api.model(
    "Item",
    {
        "name": fields.String(
            required=True,
            description="Item name"
        ),

        "description": fields.String(
            required=False,
            description="Item description"
        )
    }
)


item_response_model = api.model(
    "ItemResponse",
    {
        "id": fields.Integer(
            description="Item ID"
        ),

        "name": fields.String(
            description="Item name"
        ),

        "description": fields.String(
            description="Item description"
        ),

        "user_id": fields.Integer(
            description="Owner user ID"
        ),

        "created_at": fields.DateTime(
            description="Creation timestamp"
        )
    }
)


user_response_model = api.model(
    "UserResponse",
    {
        "id": fields.Integer(
            description="User ID"
        ),

        "username": fields.String(
            description="Username"
        ),

        "email": fields.String(
            description="Email address"
        ),

        "created_at": fields.DateTime(
            description="Registration timestamp"
        ),

        "is_active": fields.Boolean(
            description="Whether the account is active"
        )
    }
)


profile_response_model = api.model(
    "ProfileResponse",
    {
        "user": fields.Nested(
            user_response_model
        ),

        "item_count": fields.Integer(
            description="Number of items owned by the user"
        )
    }
)


login_response_model = api.model(
    "LoginResponse",
    {
        "message": fields.String(),
        "access_token": fields.String(),
        "token_type": fields.String(),
        "user": fields.Nested(
            user_response_model
        )
    }
)


# ============================================================
# NAMESPACES
# ============================================================

auth_ns = Namespace(
    "Authentication",
    description="User registration and login"
)

api.add_namespace(
    auth_ns,
    path="/api"
)


items_ns = Namespace(
    "Items",
    description="CRUD operations for user items"
)

api.add_namespace(
    items_ns,
    path="/api"
)


profile_ns = Namespace(
    "Profile",
    description="Authenticated user profile"
)

api.add_namespace(
    profile_ns,
    path="/api"
)


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return jsonify({
        "message": "Welcome to Phase 5 API",
        "status": "running",
        "version": "5.0.0",
        "database": "connected",
        "authentication": "JWT enabled",
        "swagger": "/docs"
    })


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/health")
def health():

    return jsonify({
        "status": "healthy"
    })


# ============================================================
# REGISTER
# ============================================================

@auth_ns.route("/register")
class Register(Resource):

    @auth_ns.expect(
        register_model,
        validate=True
    )

    @auth_ns.response(
        201,
        "User registered successfully"
    )

    @auth_ns.response(
        400,
        "Invalid input"
    )

    @auth_ns.response(
        409,
        "User already exists"
    )

    def post(self):

        """Register a new user"""

        data = request.get_json()

        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        # Validate
        if not username or not email or not password:

            return {
                "error": (
                    "Username, email, and password "
                    "are required"
                )
            }, 400

        # Check username
        existing_username = User.query.filter_by(
            username=username
        ).first()

        if existing_username:

            return {
                "error": "Username already exists"
            }, 409

        # Check email
        existing_email = User.query.filter_by(
            email=email
        ).first()

        if existing_email:

            return {
                "error": "Email already registered"
            }, 409

        # Create user
        user = User(
            username=username,
            email=email
        )

        user.set_password(password)

        db.session.add(user)

        db.session.commit()

        return {
            "message": "User registered successfully",
            "user": user.to_dict()
        }, 201


# ============================================================
# LOGIN
# ============================================================

@auth_ns.route("/login")
class Login(Resource):

    @auth_ns.expect(
        auth_model,
        validate=True
    )

    @auth_ns.marshal_with(
        login_response_model
    )

    @auth_ns.response(
        200,
        "Login successful"
    )

    @auth_ns.response(
        400,
        "Invalid input"
    )

    @auth_ns.response(
        401,
        "Invalid credentials"
    )

    @auth_ns.response(
        403,
        "Account deactivated"
    )

    def post(self):

        """Login and receive JWT access token"""

        data = request.get_json()

        username = data.get("username")
        password = data.get("password")

        if not username or not password:

            return {
                "error": (
                    "Username and password required"
                )
            }, 400

        # Find user
        user = User.query.filter_by(
            username=username
        ).first()

        # Validate credentials
        if (
            not user
            or not user.check_password(password)
        ):

            return {
                "error": "Invalid username or password"
            }, 401

        # Check active account
        if not user.is_active:

            return {
                "error": "Account is deactivated"
            }, 403

        # Create JWT
        access_token = create_access_token(
            identity=str(user.id)
        )

        return {
            "message": "Login successful",
            "access_token": access_token,
            "token_type": "Bearer",
            "user": user.to_dict()
        }, 200


# ============================================================
# GET ALL ITEMS
# ============================================================

@items_ns.route("/items")
class ItemsList(Resource):

    @items_ns.doc(
        security="Bearer Auth"
    )

    @items_ns.marshal_list_with(
        item_response_model
    )

    @items_ns.response(
        200,
        "Items retrieved successfully"
    )

    @items_ns.response(
        401,
        "Authentication required"
    )

    @jwt_required()
    def get(self):

        """Get all items belonging to the logged-in user"""

        current_user_id = get_jwt_identity()

        items = Item.query.filter_by(
            user_id=int(current_user_id)
        ).all()

        return [
            item.to_dict()
            for item in items
        ], 200


    @items_ns.doc(
        security="Bearer Auth"
    )

    @items_ns.expect(
        item_model,
        validate=True
    )

    @items_ns.marshal_with(
        item_response_model,
        code=201
    )

    @items_ns.response(
        201,
        "Item created successfully"
    )

    @items_ns.response(
        400,
        "Invalid input"
    )

    @items_ns.response(
        401,
        "Authentication required"
    )

    @jwt_required()
    def post(self):

        """Create a new item"""

        current_user_id = get_jwt_identity()

        data = request.get_json()

        name = data.get("name")
        description = data.get(
            "description",
            ""
        )

        if not name:

            return {
                "error": "Item name is required"
            }, 400

        item = Item(
            name=name,
            description=description,
            user_id=int(current_user_id)
        )

        db.session.add(item)

        db.session.commit()

        return item.to_dict(), 201


# ============================================================
# SINGLE ITEM
# ============================================================

@items_ns.route("/items/<int:id>")
@items_ns.param(
    "id",
    "The item ID"
)
class ItemResource(Resource):

    @items_ns.doc(
        security="Bearer Auth"
    )

    @items_ns.marshal_with(
        item_response_model
    )

    @items_ns.response(
        200,
        "Item retrieved successfully"
    )

    @items_ns.response(
        401,
        "Authentication required"
    )

    @items_ns.response(
        404,
        "Item not found"
    )

    @jwt_required()
    def get(self, id):

        """Get a specific item"""

        current_user_id = get_jwt_identity()

        item = Item.query.filter_by(
            id=id,
            user_id=int(current_user_id)
        ).first()

        if not item:

            return {
                "error": "Item not found"
            }, 404

        return item.to_dict(), 200


    @items_ns.doc(
        security="Bearer Auth"
    )

    @items_ns.expect(
        item_model
    )

    @items_ns.marshal_with(
        item_response_model
    )

    @items_ns.response(
        200,
        "Item updated successfully"
    )

    @items_ns.response(
        401,
        "Authentication required"
    )

    @items_ns.response(
        404,
        "Item not found"
    )

    @jwt_required()
    def put(self, id):

        """Update an existing item"""

        current_user_id = get_jwt_identity()

        item = Item.query.filter_by(
            id=id,
            user_id=int(current_user_id)
        ).first()

        if not item:

            return {
                "error": "Item not found"
            }, 404

        data = request.get_json()

        if data:

            if data.get("name") is not None:

                item.name = data.get("name")

            if data.get("description") is not None:

                item.description = data.get(
                    "description"
                )

        db.session.commit()

        return item.to_dict(), 200


    @items_ns.doc(
        security="Bearer Auth"
    )

    @items_ns.response(
        200,
        "Item deleted successfully"
    )

    @items_ns.response(
        401,
        "Authentication required"
    )

    @items_ns.response(
        404,
        "Item not found"
    )

    @jwt_required()
    def delete(self, id):

        """Delete an item"""

        current_user_id = get_jwt_identity()

        item = Item.query.filter_by(
            id=id,
            user_id=int(current_user_id)
        ).first()

        if not item:

            return {
                "error": "Item not found"
            }, 404

        db.session.delete(item)

        db.session.commit()

        return {
            "message": "Item deleted successfully"
        }, 200


# ============================================================
# PROFILE
# ============================================================

@profile_ns.route("/profile")
class Profile(Resource):

    @profile_ns.doc(
        security="Bearer Auth"
    )

    @profile_ns.marshal_with(
        profile_response_model
    )

    @profile_ns.response(
        200,
        "Profile retrieved successfully"
    )

    @profile_ns.response(
        401,
        "Authentication required"
    )

    @profile_ns.response(
        404,
        "User not found"
    )

    @jwt_required()
    def get(self):

        """Get authenticated user's profile"""

        current_user_id = get_jwt_identity()

        user = User.query.get(
            int(current_user_id)
        )

        if not user:

            return {
                "error": "User not found"
            }, 404

        return {
            "user": user.to_dict(),
            "item_count": len(user.items)
        }, 200


# ============================================================
# JWT ERROR HANDLERS
# ============================================================

@jwt.invalid_token_loader
def invalid_token_loader(error):

    return {
        "error": "Invalid token"
    }, 401


@jwt.expired_token_loader
def expired_token_loader(
    jwt_header,
    jwt_payload
):

    return {
        "error": "Token has expired"
    }, 401


@jwt.unauthorized_loader
def unauthorized_loader(error):

    return {
        "error": "Authorization token is required"
    }, 401


# ============================================================
# APPLICATION START
# ============================================================

if __name__ == "__main__":

    port = int(
        os.getenv(
            "PORT",
            8000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )