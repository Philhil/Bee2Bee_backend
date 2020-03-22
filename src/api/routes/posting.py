from flask import Blueprint, request, jsonify, abort
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import DATERANGE
from models import db, get_table
from utils import geocoding
import json
from geopy import distance

posting_api = Blueprint(__name__, 'api', url_prefix="/api/v0/posting")

# test with http POST localhost:5000/api/v0/posting body:='{"companyId": 4, "title": "testtile", "description": "Testbeschreibung", "price": 15, "zipCode": "83730", "city": "Fischbachau", "type": 1, "start_time": "08:00:00", "end_time": "17:00:00", "daterange": "[2020-01-04, 2020-01-05)", "persons": 5, "skills": [1,2]}'
@posting_api.route('/', methods=['POST'])
def create_position():
    if not request.json:
        abort(400)
    data = request.json
    if not "body" in data:
        abort(405)

    #requiredKeys = ["companyId", "title", "description", "zipCode", "city", "type", "start_time", "end_time", "persons", "daterange", "price"]
    requiredKeys = ["companyId", "title", "description",
                    "zipCode", "city", "type", "street", "persons", "price"]

    for key in requiredKeys:
        if not key in data["body"]:
            abort(405)

    conn = db.session.connection()
    company = get_table('company')
    address = get_table('address')

    address_data = geocoding(data["body"].get("houseNr"), data["body"]["street"], data["body"]["city"],
                             data["body"]["zipCode"], data["body"].get("state"), data["body"].get("country", "de-DE"))
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

    companyId = data["body"]["companyId"]
    title = data["body"]["title"]
    description = data["body"]["description"]
    positionType = data["body"]["type"]
    price = data["body"]["price"]
    startTime = data["body"].get("start_time")
    endTime = data["body"].get("end_time")
    persons = data["body"]["persons"]
    daterange = data["body"].get("daterange")
    traveling = data["body"].get("traveling")
    radius = data["body"].get("radius")
    skills = data["body"].get("skills")

    position = get_table('position')
    ins = position.insert().values(company_id=companyId, title=title, description=description, state_id=positionType, start_time=startTime,
                                   end_time=endTime, daterange=daterange, address_id=address_id, traveling=traveling, radius=radius, num_pers=persons, price=price, skills=skills)
    result = conn.execute(ins)
    position_id = result.inserted_primary_key[0]

    #positionSkill = get_table('position_skill')
    # if skills:
    #    for skill in skills:
    #        ins = positionSkill.insert().values(position_id=position_id, skill_id=skill)
    #        result = conn.execute(ins)

    db.session.commit()
    return jsonify({
        "position_id": position_id,
        "companyId": companyId,
        "description": description
    })

@posting_api.route('/', methods=['PUT'])
def modify_position():
    # TODO
    abort(400)

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

    # prepare output
    output_posting = {
        'id': posting_data['id'],
        'title': posting_data['title'],
        'num_pers': posting_data['num_pers'],
        'daterange': "NOT_SUPPORTED",  # FIXME
        'start_time': "NOT_SUPPORTED",  # FIXME
        'end_time': "NOT_SUPPORTED",  # FIXME
        'company_id': posting_data['company_id'],
        'state_id': posting_data['state_id'],
        'traveling': posting_data['traveling'],
        'radius': posting_data['radius'],
        'description': posting_data['description'],
        'price': posting_data['price'],
        'skills': posting_data['skills'],
        'street': address_data['street'],
        'house_nr': address_data['house_nr'],
        'city': address_data['city'],
        'state': address_data['state'],
        'country': address_data['country'],
        'zip_code': address_data['zip_code'],
        'lon': address_data['lon'],
        'lat': address_data['lat'],
    }
    return jsonify(output_posting)

@posting_api.route("/get-all/")
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
        posting_data = {}
        for key, value in row.items():
            if key == 'daterange':
                value = "NOT_SUPPORTED"  # FIXME
            if key == 'start_time':
                value = "NOT_SUPPORTED"  # FIXME
            if key == 'end_time':
                value = "NOT_SUPPORTED"  # FIXME
            posting_data[key] = value
        result_data['postings'].append(posting_data)
    return jsonify(result_data)

@posting_api.route("/query/", methods=['GET'])
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
            posting_data = {}
            for key, value in row.items():
                if key == 'daterange':
                    value = "NOT_SUPPORTED"  # FIXME
                if key == 'start_time':
                    value = "NOT_SUPPORTED"  # FIXME
                if key == 'end_time':
                    value = "NOT_SUPPORTED"  # FIXME
                posting_data[key] = value
                result_data['postings'].append(posting_data)
    return jsonify(result_data)
