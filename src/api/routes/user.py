from flask import Blueprint, request, jsonify, abort
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
    data = request.json
    if not "body" in data:
        abort(405)
    if len(data["body"]["name"]) == 0:
        abort(405)

    # Check if all requiredKeys are there
    requiredKeys = ["name", "email", "secret", "company_id"]
    for key in requiredKeys:
        if not key in data["body"]:
            abort(405)

    session_key = secrets.token_hex()

    json_data = data["body"]

    # Insert data to db
    with db.engine.begin() as conn:
        user = get_table('user')
        ins = user.insert().values(
            email=json_data.get('email'),
            name=json_data.get('name'),
            pwd=json_data.get('secret'),
            session_key=session_key,
            company_id=json_data.get('company_id')
        )
        result = conn.execute(ins)

    # Generate output json
    output_user = {}
    output_user['id'] = result.inserted_primary_key[0]
    output_user['name'] = json_data.get('name')
    output_user['token'] = json_data.get('session_key')
    output_user['email'] = json_data.get('email')
    output_user['company_id'] = json_data.get('company_id')

    return jsonify(output_user)

@user_api.route('/', methods=['PUT'])
def user_put():
    # TODO
    abort(400)

@user_api.route('/<int:userid>/', methods=['GET'])
# test with http GET localhost:5000/api/v0/user/12/
def get_user(userid):
    if type(userid) is not int:
        abort(400)

    # Look data in db
    with db.engine.begin() as conn:
        user = get_table('user')
        sel = select([user.c.id,
            user.c.lastname,
            user.c.firstname,
            user.c.email,
            user.c.company_id,
            user.c.session_key == token],
            user.c.id == userid
        )
        result = conn.execute(sel)
        data = result.fetchone()

    # check if data is there
    if data == None:
        abort(404)

    # prepare output
    output_user = {
        'id': data['id'],
        'name': data['lastname'],
        'first_name': data['firstname'],
        'email': data['email'],
        'company_id': data['company_id'],
        'secret': data['pwd']
    }
    return jsonify(output_user)

@user_api.route('/<int:userid>/', methods=['DELETE'])
def delete_user(userid):
    # TODO
    abort(400)
