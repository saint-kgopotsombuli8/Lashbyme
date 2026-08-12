import sys
import os

# Guarantee root project directory is in sys.path
basedir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, basedir)

from flask import Flask
from models import db
from routes import main, auth

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'lashedbyme-super-secret-key')
    
    # Use /tmp for Vercel serverless, and local root directory for local development
    if os.environ.get('VERCEL'):
        default_db = 'sqlite:////tmp/lashedbyme.db'
    else:
        default_db = f"sqlite:///{os.path.join(basedir, 'lashedbyme.db')}"
    
    db_url = os.environ.get('DATABASE_URL', default_db)
    
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
        
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    app.register_blueprint(main)
    app.register_blueprint(auth)

    # Ensure database tables exist on every serverless request execution
    @app.before_request
    def initialize_database():
        try:
            db.create_all()
        except Exception as e:
            app.logger.error(f"Database setup error: {e}")

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)