import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Register blueprints
    from routes.resume import resume_bp
    app.register_blueprint(resume_bp, url_prefix='/api')

    @app.route('/health')
    def health():
        return {"status": "healthy"}, 200

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
