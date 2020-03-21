from flask import Blueprint, request, jsonify, abort
from models import db, get_table

posting_api = Blueprint(__name__, 'api', url_prefix="/api/v0/posting")

# test with http POST localhost:5000/api/v0/posting body:='{"companyId": 4, "description": "Testbeschreibung", "zipCode": "83730", "location": "Fischbachau", "type": 1, "start_time": "2020-03-16T08:00:00", "end_time": "2020-03-16T17:00:00"}'
@posting_api.route('/', methods=['POST'])
def create_position():
    if not request.json:
        abort(400)
    data = request.json
    if not "body" in data:
        abort(405)   

    requiredKeys = ["companyId", "description", "zipCode", "location", "type", "start_time", "end_time", "persons"]
    #for requiredKeys in data["body"]:
    #     abort(405)    

    companyId = data["body"]["companyId"]
    description = data["body"]["description"]
    zipCode = data["body"]["zipCode"]
    city = data["body"]["location"]
    positionType = data["body"]["type"]
    startTime = data["body"]["start_time"]
    endTime = data["body"]["start_time"]
    persons = data["body"]["persons"]
    skills = data["body"]["skills"]
    
    position = get_table('position')


    ins = position.insert().values(company_id=companyId, description=description, state_id=positionType, start_time=startTime, end_time=endTime)
    conn = db.session.connection()        
    result = conn.execute(ins)
    db.session.commit()
    return jsonify({
        "id": result.inserted_primary_key[0],
        "companyId": companyId,
        "description": description 
        })
