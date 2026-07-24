import os
from flask import Flask
from models import db
from routes import main, auth

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'lashedbyme-super-secret-key')
    
    # 1. Grab cloud database URL if available, otherwise use local sqlite
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///lashedbyme.db')
    
    # 2. Fix PostgreSQL prefix formatting for SQLAlchemy compatibility
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    app.register_blueprint(main)
    app.register_blueprint(auth)

    with app.app_context():
        db.create_all()

    return app

# Serverless entry point for Vercel
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)