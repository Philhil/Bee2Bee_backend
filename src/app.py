from flask import Flask, jsonify
from api.routes import api

def create_app(config=None):
    app = Flask(__name__)
    # TODO: load config from env
    setup_app(app)
    return app

def setup_app(app):
    app.register_blueprint(api)

    @app.route('/')
    def index():
        return jsonify(status=200, message='OK')


    @app.route('/healthcheck')
    def healthcheck():
        return jsonify(status=200, message='healthcheck OK')