from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    # import models so Flask-Migrate can detect them
    from app.models import User, Game, Comment  # noqa: F401

    from app.routes.main import bp as main_bp
    from app.routes.auth import bp as auth_bp
    from app.routes.games import bp as games_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(games_bp)

    return app
