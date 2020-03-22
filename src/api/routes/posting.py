from flask import Blueprint, request, jsonify, abort
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import DATERANGE
from models import db, get_table
from utils import geocoding, get_api_posting
import json
from geopy import distance

posting_api = Blueprint(__name__, 'api', url_prefix="/api/v0/posting")

# test with http POST localhost:5000/api/v0/posting/ body:='{"companyId": 4, "posting_type":1, "title": "testtile", "description": "Testbeschreibung", "address": {"zip_code": "83730", "city": "Fischbachau", "street": "Im Rothmoos", "number": "12"}, "skills": [1,2]}'

@posting_api.route('/', methods=['POST'])
def create_position():
    if not request.json:
        abort(400)
    data = request.json
    if not "body" in data:
        abort(405)

    # Check for required keys
    requiredKeys = ["title", "posting_type","address"]
    for key in requiredKeys:
        if not key in data["body"]:
            abort(405)
    address = ["zip_code", "city", "street"]
    for key in address:
        if not key in data["body"]["address"]:
            abort(405)

    # Add posting to db
    conn = db.session.connection()
    company = get_table('company')
    address = get_table('address')

    # First add address
    address_data = geocoding(
        data["body"]["address"].get("number"),
        data["body"]["address"].get("street"),
        data["body"]["address"].get("city"),
        data["body"]["address"].get("zip_code"),
        data["body"]["address"].get("state", "Deutschland"),
        data["body"]["address"].get("country", "de-DE")
        )
    address_id = None
    ins = address.insert().values(
        zip_code=address_data["zip_code"],
        city=address_data["city"],
        street=address_data["street"],
        house_nr=address_data["house_nr"],
        state=address_data["state"],
        country=address_data["country"],
        lon=address_data["lon"],
        lat=address_data["lat"]
        )
    result = conn.execute(ins)
    address_id = result.inserted_primary_key[0]

    # Get all data for db
    companyId = data["body"].get("companyId")
    title = data["body"].get("title")
    description = data["body"].get("description")
    positionType = data["body"].get("posting_type")
    wage_hourly = data["body"].get("wage_hourly")
    startTime = data["body"].get("work_time_start")
    endTime = data["body"].get("work_time_end")
    num_people = data["body"].get("num_people")
    daterange = data["body"].get("daterange")
    traveling = data["body"].get("travel_ability_needed")
    radius = data["body"].get("travel_radius")
    skills = data["body"].get("skills")

    position = get_table('position')
    ins = position.insert().values(company_id=companyId,
                                title=title,
                                description=description,
                                state_id=positionType,
                                start_time=startTime,
                                end_time=endTime,
                                daterange=daterange,
                                address_id=address_id,
                                traveling=traveling,
                                radius=radius,
                                num_pers=num_people,
                                price=wage_hourly,
                                skills=skills)
    result = conn.execute(ins)
    db.session.commit()

    # Get ID
    position_id = result.inserted_primary_key[0]

    return jsonify({
        "title" : title,
        "description" : description,
        "posting_type" : positionType,
        "num_people" : num_people,
        "work_time_start" : startTime,
        "work_time_end" : endTime,
        "companyId": companyId,
        "travel_ability_needed" : traveling,
        "travel_radius" : radius,
        "wage_hourly" : wage_hourly,
        "skills" : skills,
        "address" : {"zip_code": address_data["zip_code"],
                        "city": address_data["city"],
                        "street": address_data["street"],
                        "number": address_data["house_nr"],
                        "state": address_data["state"],
                        "country": address_data["country"],
                        "longitude":address_data["lon"],
                        "latitude":address_data["lat"]}
    })

@posting_api.route('/', methods=['PUT'])
# test http PUT localhost:5000/api/v0/posting/ body:='{"id": 8, "posting_type":1, "title": "testtile", "description": "Testbeschreibung", "address": {"zip_code": "83730", "city": "Fischbachau", "street": "Im Rothmoos", "number": "12"}, "skills": [1,2]}'
def modify_position():
    if not request.json:
        abort(400)
    data = request.json
    if not "body" in data:
        abort(405)

    # Check for required keys
    requiredKeys = ["id"]
    for key in requiredKeys:
        if not key in data["body"]:
            abort(405)
    posting_id = data["body"]['id']

    # Convert input data
    new_data = {}
    for key, value in data['body'].items():
        if key == 'price':
            new_data['wage_hourly']=value
        elif key == 'num_people':
            new_data['num_pers'] = value
        elif key == 'posting_type':
            new_data['state_id'] = value
        elif key == 'travel_ability_needed':
            new_data['traveling'] = value
        elif key == 'travel_radius':
            new_data['travel_radius'] = value
        elif key != 'address':
            new_data[key] = value

    with db.engine.begin() as conn:
        position = get_table('position')
        update = position.update().where(position.c.id==data["body"]["id"]).values(**new_data)
        result = conn.execute(update)

    result_posting = result.rowcount

    if "address" in data["body"]:
        # Get address id
        with db.engine.begin() as conn:
            position = get_table('position')
            sel = select([position.c.address_id],
                position.c.id == posting_id
            )
            result = conn.execute(sel)
            address_id = result.fetchone()[0]

        address_data = geocoding(
            data["body"]["address"].get("number"),
            data["body"]["address"].get("street"),
            data["body"]["address"].get("city"),
            data["body"]["address"].get("zip_code"),
            data["body"]["address"].get("state", "Deutschland"),
            data["body"]["address"].get("country", "de-DE")
            )

        with db.engine.begin() as conn:
            address = get_table('address')
            update = address.update().where(address.c.id==address_id).values(**address_data)
            result = conn.execute(update)

        result_address = result.rowcount

    if result_address + result_posting == 0:
        abort(404)
    return jsonify(True)

@posting_api.route('/<int:posting_id>/', methods=['GET'])
# test with http GET localhost:5000/api/v0/posting/12/
def get_posting(posting_id):
    if type(posting_id) is not int:
        abort(400)

    # Look data in db
    with db.engine.begin() as conn:
        position = get_table('position')
        sel = select([position.c.id,
            position.c.title,
            position.c.num_pers,
            position.c.daterange,
            position.c.start_time,
            position.c.end_time,
            position.c.company_id,
            position.c.state_id,
            position.c.traveling,
            position.c.radius,
            position.c.address_id,
            position.c.description,
            position.c.price,
            position.c.skills
        ],
            position.c.id == posting_id
        )
        result = conn.execute(sel)
        posting_data = result.fetchone()

    # check if data is there
    if posting_data == None:
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
            address.c.id == posting_data['address_id']
        )
        result = conn.execute(sel)
        address_data = result.fetchone()

    # check if data is there
    if address_data == None:
        abort(404)

    return jsonify(get_api_posting(posting_data,address_data))

@posting_api.route('/<int:posting_id>/', methods=['DELETE'])
# test with http GET localhost:5000/api/v0/posting/12/
def remove_posting(posting_id):
    if type(posting_id) is not int:
        abort(400)

    # Delete data in db
    with db.engine.begin() as conn:
        position = get_table('position')
        delete = position.delete().where(position.c.id == posting_id)
        result = conn.execute(delete)

    if result.rowcount == 0:
        abort(404)
    return jsonify(True)

@posting_api.route("/get-all/")
# Test: http GET localhost:5000/api/v0/posting/get-all/
def get_all_postings():
    with db.engine.begin() as conn:
        position = get_table('position')
        address = get_table('address')
        joint = select([
            position,
            address.c.street,
            address.c.house_nr,
            address.c.city,
            address.c.state,
            address.c.country,
            address.c.zip_code,
            address.c.lon,
            address.c.lat
        ]).select_from(
            position.join(address)
        )
        result = conn.execute(joint)

    result_data = {'postings': []}

    for row in result:
        posting_data = get_api_posting(row,row)
        result_data['postings'].append(posting_data)
    return jsonify(result_data)

@posting_api.route("/query/", methods=['GET'])
# TEST http GET localhost:5000/api/v0/posting/query/ body:='{"posting_type":1,"longitude":11.94,"latitude":47.72,"radius":4.5}'
def get_defined_posting():
    # Check input for errors
    if not request.json:
        abort(400)
    data = request.json
    if not "body" in data:
        abort(405)

    # Check if all requiredKeys are there
    requiredKeys = ["posting_type", "longitude", "latitude","radius"]
    for key in requiredKeys:
        if not key in data["body"]:
            abort(405)

    with db.engine.begin() as conn:
        position = get_table('position')
        address = get_table('address')
        joint = select([
            position,
            address.c.street,
            address.c.house_nr,
            address.c.city,
            address.c.state,
            address.c.country,
            address.c.zip_code,
            address.c.lon,
            address.c.lat
        ], position.c.state_id == data["body"]["posting_type"]).select_from(
            position.join(address)
        )
        result = conn.execute(joint)

    result_data = {'postings': []}

    dest_coords = (data["body"]["longitude"],data["body"]["latitude"])
    for row in result:
        src_coords = (row['lon'], row['lat'])
        if distance.distance(dest_coords,src_coords) < data["body"]["radius"]:
            posting_data = get_api_posting(row,row)
            result_data['postings'].append(posting_data)
    return jsonify(result_data)
