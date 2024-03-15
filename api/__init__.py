from flask import Flask
from utilities import logger
from flask_sqlalchemy import SQLAlchemy
from waitress import serve
import os, socket

db = SQLAlchemy()

if not os.path.exists('api/matches'):
    logger.info("Created matches folder")
    os.mkdir('api/matches')
if not os.path.exists('api/demos'):
    logger.info("Created demos folder")
    os.mkdir('api/demos')
    
    
def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///static/app.db"
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

    db.init_app(app)

    from .routes import routes as main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app


def get_local_ip():
    try:
        host_name = socket.gethostname()
        local_ip = socket.gethostbyname(host_name)
        return local_ip
    except Exception as e:
        logger.error(f"An error occurred while getting local IP: {e}")
        return None



def run_flask():
    app = create_app()
    ip = get_local_ip()
    port = int(os.getenv('WEB_INTERFACE'))
    #app.run(debug=True, port=port)
    serve(app, host=ip, port=port)
    

    

