from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

# Инициализация расширений
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

# Куда перенаправлять пользователя, если он не авторизован
login_manager.login_view = 'auth.login'
login_manager.login_message = "Пожалуйста, войдите в систему, чтобы получить доступ к этой странице."
login_manager.login_message_category = "info"

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Инициализация БД и миграций
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Регистрация Blueprint-ов (мы создадим их в следующих шагах)
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.routes.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.routes.bookings import bp as bookings_bp
    app.register_blueprint(bookings_bp, url_prefix='/bookings')

    from app.routes.workplaces import bp as workplaces_bp
    app.register_blueprint(workplaces_bp, url_prefix='/workplaces')

    from app.routes.admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app