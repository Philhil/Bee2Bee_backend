from flask import Blueprint, request, jsonify, abort
from models import db, get_table
api = Blueprint(__name__, 'api', url_prefix="/api/v0/" )

@api.route('/')
def home():
    return 'Hello World!'


# test with http POST localhost:5000/api/v0/company body:='{"name": "Bar Ltd"}'
@api.route('/company', methods=['POST'])
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
    company = get_table('company')

    ins = company.insert().values(name=name)
    conn = db.session.connection()        
    result = conn.execute(ins)
    db.session.commit()
    return jsonify({
        "id": result.inserted_primary_key[0],
        "name": name
        })
