from flask import Blueprint, request, jsonify, abort
from models import db, get_table

from sqlalchemy.sql import select
from sqlalchemy import Table

company_api = Blueprint(__name__, 'api', url_prefix="/api/v0/company")


# test with http POST localhost:5000/api/v0/company/ body:='{"name": "Bar Ltd"}'
@company_api.route('/', methods=['POST'])
def create_company():
    if not request.json:
        abort(400)
    data = request.json
    if not "body" in data:
        abort(405)
    if not "name" in data["body"]:
        abort(405)
    if len(data["body"]["name"]) == 0:
        abort(405)

    name = data["body"]["name"]
    address_data = {}
    has_address_info = False
    address_keys = ['zip_code', 'street', 'house_nr', 'city', 'state', 'country']
    for address_key in address_keys:
        if address_key in data["body"]:
            has_address_info = True
        address_data[address_key] = data["body"].get(address_key, None)

    conn = db.session.connection()
    company = get_table('company')
    address = get_table('address')

    address_id = None
    if has_address_info:
        ins = address.insert().values(
            **address_data
        )
        result = conn.execute(ins)
        address_id = result.inserted_primary_key[0]

    company_data = {
        "name": name
    }
    if has_address_info:
        company_data['address_id'] = address_id

    ins = company.insert().values(name=name, address_id=address_id)
    result = conn.execute(ins)
    db.session.commit()

    company_data['id'] = result.inserted_primary_key[0]

    return jsonify(company_data)

@company_api.route('/', methods=['PUT'])
def change_company():
    # TODO
    abort(400)

@company_api.route('/<int:company_id>/', methods=['GET'])
# test with http GET localhost:5000/api/v0/company/7/
def get_company(company_id):
    if type(company_id) is not int:
        abort(400)

    # Look data in db
    with db.engine.begin() as conn:
        company = get_table('company')
        sel = select([company.c.id,
            company.c.name,
            company.c.address_id],
            company.c.id == company_id
        )
        result = conn.execute(sel)
        company_data = result.fetchone()

    # check if data is there
    if company_data == None:
        abort(404)

    # Look address in db
    with db.engine.begin() as conn:
        address = get_table('address')
        sel = select([address.c.street,
            address.c.house_nr,
            address.c.city,
            address.c.state,
            address.c.country,
            address.c.zip_code,
            address.c.lon,
            address.c.lat
            ],
            address.c.id == company_data['address_id']
        )
        result = conn.execute(sel)
        address_data = result.fetchone()

    # check if data is there
    if address_data == None:
        abort(404)

    # prepare output
    output_company = {
        'id': company_data['id'],
        'name': company_data['name'],
        'street': address_data['street'],
        'house_nr': address_data['house_nr'],
        'city': address_data['city'],
        'state': address_data['state'],
        'country': address_data['country'],
        'zip_code': address_data['zip_code'],
        'lon': address_data['lon'],
        'lat': address_data['lat'],
    }
    return jsonify(output_company)

@company_api.route('/<int:company_id>/', methods=['DELETE'])
def delete_company(company_id):
    # TODO
    abort(400)
