from flask import Blueprint, request, jsonify, abort
from models import db, get_table

from sqlalchemy.sql import select
from sqlalchemy import Table

user_api = Blueprint(__name__, 'api', url_prefix="/api/v0/user" )

@user_api.route('/', methods=['POST'])
def user_data():
    if not request.json:
        abort(400)
    data = request.json
    if not "body" in data:
        abort(405)
    if not "name" in data["body"]:
        abort(405)
    if len(data["body"]["name"]) == 0:
        abort(405)

    json_data = data["body"]

    
    with db.engine.begin() as conn:        
        user = get_table('user')
        ins = user.insert().values(
            email=json_data.get('email'), 
            firstname=json_data.get('first_name'), 
            lastname=json_data.get('name'),         
            pwd=json_data.get('secret'), 
            company_id=json_data.get('company_id')
        )
        result = conn.execute(ins)


    output_user = {}
    output_user['id'] = result.inserted_primary_key[0]
    output_user['name'] = json_data.get('name')
    output_user['first_name'] = json_data.get('first_name')
    output_user['secret'] = json_data.get('secret')
    output_user['email'] = json_data.get('email')
    output_user['company_id'] = json_data.get('company_id')
    

    return jsonify(output_user)
