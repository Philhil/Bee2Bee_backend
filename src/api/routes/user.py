from flask import Blueprint, request, jsonify, abort
from models import db, get_table

from sqlalchemy.sql import select
from sqlalchemy import Table

user_api = Blueprint(__name__, 'api', url_prefix="/api/v0/user" )

@user_api.route('/', methods=['POST'])
def user_data():
    # Check input for errors
    if not request.json:
        abort(400)
    data = request.json
    if not "body" in data:
        abort(405)
    if len(data["body"]["name"]) == 0:
        abort(405)

    # Check if all requiredKeys are there
    requiredKeys = ["name", "first_name"]
    for key in requiredKeys:
        if not key in data["body"]:
            abort(405)
    print('test')

    json_data = data["body"]

    # Insert data to db
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

    # Generate output json
    output_user = {}
    output_user['id'] = result.inserted_primary_key[0]
    output_user['name'] = json_data.get('name')
    output_user['first_name'] = json_data.get('first_name')
    output_user['secret'] = json_data.get('secret')
    output_user['email'] = json_data.get('email')
    output_user['company_id'] = json_data.get('company_id')

    return jsonify(output_user)

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
            user.c.pwd],
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
