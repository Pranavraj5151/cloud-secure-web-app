from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from flask_jwt_extended import JWTManager
from flask_wtf.csrf import CSRFProtect
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
limiter = Limiter(key_func=get_remote_address)
jwt = JWTManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    limiter.init_app(app)
    jwt.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'main.login'
    login_manager.login_message_category = 'info'

    # Exempt JWT API endpoints from CSRF protection
    # (API clients authenticate via Bearer token, not session cookies)
    from app.routes import main, api_login, api_me, api_tasks, health
    csrf.exempt(api_login)
    csrf.exempt(api_me)
    csrf.exempt(api_tasks)
    csrf.exempt(health)

    app.register_blueprint(main)

    with app.app_context():
        try:
            db.create_all()
        except Exception:
            pass

    return app
