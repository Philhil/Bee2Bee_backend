import geopy
from geopy.geocoders import Nominatim
from geopy import distance
import pandas as pd


def calc_coordinates_from_address(address, geopy_app_name):
    geolocator = Nominatim(user_agent=geopy_app_name)
    try:
        geo_address = geolocator.geocode(address)
        return (geo_address.latitude, geo_address.longitude)
    except Error as e:
        print(e)
        
def calc_coordinates_from_address_row(row):
    geolocator = Nominatim(user_agent="specify_your_app_name_here")
    try:
        co = geolocator.geocode(row["address"])
        #row["lat"] = co.latitude
        #row["lon"] = co.longitude
        return co.latitude, co.longitude
    except Error as e:
        print(e)
        
def merge_columns_to_addresses(df):
    df["address"] = df[['street', 'house_nr', 'zip_code', 'city']].agg(' '.join, axis=1)
    
def determine_distance(co0, co1):
    dist = distance.distance(co0, co1)
    return dist.km

def determine_distance_from_row(row, origin_coordinates):
    row_coordinates = (row["lat"], row["lon"])
    dist = distance.distance(origin_coordinates, row_coordinates)
    return dist

def determine_geomatches(search_id, df):
    merge_columns_to_addresses(df)
    df['lat'], df['lon'] = zip(*df.apply(calc_coordinates_from_address_row, axis=1))
    origin = df.loc[df["id"] == search_id]
    origin_coordinates = (origin["lat"][1], origin["lon"][1])
    distances = df.apply(determine_distance_from_row, args=[origin_coordinates], axis=1)
    distances = distances.rename("distance")
    match_df = pd.concat([df.id, distances], axis=1, names=["id, distance"]).sort_values(by="distance")
    match_df = match_df.reset_index()
    matchlist = match_df["id"][1:4].tolist()
    return matchlist


if __name__ == '__main__':
    df = pd.DataFrame({"id":[0,1,2], "street":["Usedomer Strasse", "Breitscheidstrasse", "Saasa"],
                  "house_nr":["3","10","52"], "city":["Leipzig", "Stuttgart", "Eisenberg"],
                  "zip_code":["04159", "70174", "07607" ]})
    search_id = 1
    determine_geomatches(search_id, df)