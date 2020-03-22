import requests


def geocoding(house_nr, street, city, zip_code, state, country):
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
