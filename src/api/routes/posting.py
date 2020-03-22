from flask import Blueprint, request, jsonify, abort
from models import db, get_table

posting_api = Blueprint(__name__, 'api', url_prefix="/api/v0/posting")

# test with http POST localhost:5000/api/v0/posting body:='{"companyId": 4, "title": "testtile", "description": "Testbeschreibung", "zipCode": "83730", "city": "Fischbachau", "type": 1, "start_time": "08:00:00", "end_time": "17:00:00", "daterange": "[2020-01-04, 2020-01-05)", "persons": 5, "skills": [1,2]}'
@posting_api.route('/', methods=['POST'])
def create_position():
    if not request.json:
        abort(400)
    data = request.json
    if not "body" in data:
        abort(405)   

    requiredKeys = ["companyId", "title", "description", "zipCode", "city", "type", "start_time", "end_time", "persons", "daterange"]
    for key in requiredKeys:
        if not key in data["body"]:
         abort(405)    

    
    conn = db.session.connection() 
    company = get_table('company')
    address = get_table('address')
    
    zipCode = data["body"]["zipCode"]
    city = data["body"]["city"]
    street = data["body"]["street"]
    houseNr = data["body"]["houseNr"]
    state = data["body"]["state"]
    country = data["body"]["country"]

    address_id = None
    ins = address.insert().values(
        zip_code=zipCode,
        city=city,
        street=street,
        house_nr=houseNr,
        state=state,
        country=country,
    )
    result = conn.execute(ins)
    address_id = result.inserted_primary_key[0]

    companyId = data["body"]["companyId"]
    title = data["body"]["title"]
    description = data["body"]["description"]
    positionType = data["body"]["type"]
    startTime = data["body"]["start_time"]
    endTime = data["body"]["end_time"]
    persons = data["body"]["persons"]
    daterange = data["body"]["daterange"]
    traveling = None
    radius = None
    if "traveling" in data["body"]:
        traveling = data["body"]["traveling"]
        if "radius" in data["body"]:
            radius = data["body"]["radius"]
    
    position = get_table('position')
    ins = position.insert().values(company_id=companyId, title=title, description=description, state_id=positionType, start_time=startTime, end_time=endTime, daterange=daterange, address_id=address_id, traveling=traveling, radius=radius, num_pers=persons)
    result = conn.execute(ins)
    position_id = result.inserted_primary_key[0]


    skills = data["body"]["skills"]
    positionSkill = get_table('position_skill')
    for skill in skills:
        ins = positionSkill.insert().values(position_id=position_id, skill_id=skill)
        result = conn.execute(ins)
    

    db.session.commit()
    return jsonify({
        "position_id": position_id,
        "companyId": companyId,
        "description": description 
        })
