from flask import Flask, flash, redirect, url_for  
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
import os
db = SQLAlchemy()

def create_app():

    load_dotenv()
    app = Flask(__name__, template_folder='templates', static_folder='static')
    password = ""
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://root:{password}@localhost:3306/recommendation_system_db"
  
    app.secret_key = os.getenv("SECRET_KEY")

    db.init_app(app)


    login_manager = LoginManager()
    login_manager.init_app(app)


    from models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    bcrypt = Bcrypt(app)

    @login_manager.unauthorized_handler
    def unauthorized_callback():
        flash("You must login first.", "error")
        return redirect(url_for('login'))
    
    from route import register_routes
    register_routes(app, db,bcrypt)
    migrate = Migrate(app,db)

    return app

    
