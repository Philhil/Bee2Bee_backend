from flask import Blueprint
from flask import request
from flask import jsonify
from flask import json
from models import db

from sqlalchemy.sql import select
from sqlalchemy import Table

api = Blueprint(__name__, 'api', url_prefix="/api/v0/" )

@api.route('/')
def home():
    return 'Hello World!'

@api.route('/user', methods=['post', 'put'])
def user_data():
    json_data = request.get_json()

    if request.method == 'POST':
        conn = db.session.connection()
        user = Table('user', db.metadata, autoload=True, autoload_with=db.engine)
        s = user.insert().values(firstname= json_data.get('first_name'), lastname=json_data.get('name'), email=json_data.get('email'), pwd=json_data.get('secret'))
        result = conn.execute(s)
        output_user = {}
        output_user['id'] = result.inserted_primary_key
        output_user['name'] = json_data.get('name')
        output_user['first_name'] = json_data.get('first_name')
        output_user['secret'] = json_data.get('secret')
        output_user['email'] = json_data.get('email')
        db.session.commit()

        return jsonify(output_user)
