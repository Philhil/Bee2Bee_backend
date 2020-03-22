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


@user_api.route('/<string:token>/', methods=['GET'])
# test with http GET localhost:5000/api/v0/user/12/
def get_user(session_token):
    if type(session_token) is not string:
        abort(400)
    
    # Look data in db
    with db.engine.begin() as conn:
        user = get_table('user')
        sel = select([
            user.c.id,
            user.c.name,
            user.c.email,
            user.c.company_id],
            user.c.session_key == session_token
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


@user_api.route('/auth', methods=['POST'])
def user_auth():
    # Check input for errors
    if not request.json:
        abort(400)
    data = request.json

    if not "body" in data:
        abort(405)

    # Check if all requiredKeys are there
    requiredKeys = ["email", "secret"]
    for key in requiredKeys:
        if not key in data["body"]:
            abort(405)

    with db.engine.begin() as conn:
        user = get_table('user')
        sel = select([
            user.c.pwd
        ], user.c.email == data["body"]["email"])
        result = conn.execute(sel)
        user_data = result.fetchone()

    if user_data == None:
        abort(404)
    print(check_password_hash(user_data["pwd"], data["body"]["secret"]))
    if not check_password_hash(user_data["pwd"], data["body"]["secret"]):
        abort(403)

    session_key = secrets.token_hex()

    json_data = data["body"]

    # Insert data to db
    with db.engine.begin() as conn:
        user = get_table('user')
        ins = user.update().where(user.c.email == data["body"]["email"]).values(
            session_key=session_key,
        )
        result = conn.execute(ins)

    # Generate output json
    output_user = {}
    output_user['token'] = session_key

    return jsonify(output_user)