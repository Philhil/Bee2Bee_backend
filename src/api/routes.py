from flask import Blueprint
api = Blueprint(__name__, 'api', url_prefix="/api/v0/" )

@api.route('/')
def home():
    return 'Hello World!'