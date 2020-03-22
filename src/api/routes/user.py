from flask import Blueprint, request, jsonify, abort, Response
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, get_table

from sqlalchemy.sql import select
from sqlalchemy import Table
import secrets

user_api = Blueprint(__name__, 'api', url_prefix="/api/v0/user" )

@user_api.route('/', methods=['POST'])
def user_post():
    # Check input for errors
    if not request.json:
        abort(400)
    
    json_data = request.json  

    # Check if all requiredKeys are there and have required length
    requiredKeys = ["email", "company_id", "name", "secret"]
    for key in requiredKeys:
        if not key in json_data:
            abort(405)
    session_key = secrets.token_hex()

    if len(json_data['email']) == 0:
        abort(405)
    
    if not isinstance(json_data['company_id'], int):
        abort(405)

    # FIXME: Validate company_id against database

    # Insert data to db
    with db.engine.begin() as conn:
        user = get_table('user')
        ins = user.insert().values(
            email=json_data.get('email'),
            name=json_data.get('name'),
            pwd=generate_password_hash(json_data.get('secret', "hunter2")), # Password is optional for POC
            session_key=session_key,
            company_id=json_data.get('company_id')
        )
        result = conn.execute(ins)

    # Generate output json
    output_user = {   
        'id': result.inserted_primary_key[0],
        'company_id': json_data.get('company_id'),
        'name': json_data.get('name', ''),
        'email': json_data.get('email'),
        'token': session_key
    } 

    return jsonify(output_user)


@user_api.route('/<int:userid>/', methods=['GET'])
# test with http GET localhost:5000/api/v0/user/12/
def get_user(userid):
    if type(userid) is not int:
        abort(400)
    
    # Look data in db
    with db.engine.begin() as conn:
        user = get_table('user')
        sel = select([
            user.c.id,
            user.c.name,
            user.c.email,
            user.c.company_id],
            user.c.id == userid # TODO: Check token
        )
        result = conn.execute(sel)
        data = result.fetchone()

    # check if data is there
    if data == None:
        abort(404)

    # prepare output
    output_user = {   
        'id': data['id'],
        'company_id': data['company_id'],
        'name': data['name'] or '',
        'email': data['email'],
    } 

    return jsonify(output_user)
