import requests


def geocoding(house_nr, street, city, zip_code, state, country):
    print(house_nr, street, city, zip_code, state, country)
    searchQuery = ''
    if house_nr:
        searchQuery += house_nr + '+'
    searchQuery += street.replace(' ', '+') + '+' + city + '+' + zip_code
    res = requests.get('https://nominatim.openstreetmap.org/search?q=' +
                       searchQuery + '&format=jsonv2&addressdetails=1')
    data = res.json()
    if data[0]:
        lat = data[0]["lat"]
        lon = data[0]["lon"]
        if not state:
            state = data[0]["address"]["state"]
        if not country:
            country = data[0]["address"]["country"]
    else:
        lat = None
        lon = None
    address_data = {
        "house_nr": house_nr,
        "street": street,
        "city": city,
        "zip_code": zip_code,
        "state": state,
        "country": country,
        "lon": lon,
        "lat": lat
    }
    return address_data

def get_api_posting(db_posting_data, db_address_data):
    return({
            'id': db_posting_data['id'],
            'company_id': db_posting_data['company_id'],
            'title': db_posting_data['title'],
            'description': db_posting_data['description'],
            'wage_hourly': db_posting_data['price'],
            'address' : {'street': db_address_data['street'],
                        'house_nr': db_address_data['house_nr'],
                        'city': db_address_data['city'],
                        'state': db_address_data['state'],
                        'country': db_address_data['country'],
                        'zip_code':db_address_data['zip_code'],                 'longitude':db_address_data["lon"],
                        'latitude':db_address_data["lat"]},
            'num_people': db_posting_data['num_pers'],
            'posting_type': db_posting_data['state_id'],
            'work_time_start': "NOT_SUPPORTED",  # FIXME
            'work_time_end': "NOT_SUPPORTED",  # FIXME
            'travel_ability_needed': db_posting_data['traveling'],
            'travel_radius': db_posting_data['radius'],
            'skills': db_posting_data['skills']
        })
