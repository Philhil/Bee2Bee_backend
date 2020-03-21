import awsgi
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify(status=200, message='OK')


@app.route('/foo')
def foo():
    return jsonify(status=200, message='foo is OK')

def lambda_handler(event, context):
    return awsgi.response(app, event, context)