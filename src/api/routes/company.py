from flask import Blueprint, request, jsonify, abort
from models import db, get_table


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

    ins = company.insert().values(name=name)
    result = conn.execute(ins)
    db.session.commit()

    company_data['id'] = result.inserted_primary_key[0]

    return jsonify(company_data)