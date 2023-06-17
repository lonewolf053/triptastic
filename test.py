import requests
import json
from time import sleep
import itertools
from flask import Flask, request, jsonify
import math

app = Flask(__name__)

def returnlat(a, location):
    url = "https://trueway-geocoding.p.rapidapi.com/Geocode"
    querystring = {"address": a, "language": "en"}
    headers = {
        "X-RapidAPI-Key": "YOUR-API-KEY-HERE",
        "X-RapidAPI-Host": "trueway-geocoding.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()
    return [(data['results'][0]['location']['lat']), (data['results'][0]['location']['lng'])]

@app.route('/home', methods=['POST'])
def home():
    data = request.get_json()
    location = data['place']
    
    url = "https://api.foursquare.com/v3/places/search"
    headers = {
        "accept": "application/json",
        "Authorization": "YOUR-API-KEY-HERE"
    }
    params = {
        "v": "20230501",
        "near": location,
        "query": "tourist",
        "limit": 5  # Adjust the limit as per your requirement
    }
    response = requests.get(url, headers=headers, params=params, stream=True)
    data = response.json()

    pois = []
    poadd = []
    latlist = []
    lnglist = []
    for i in range(5):
        pois.append(data['results'][i]['name'])

    for j in range(5):
        x, y = returnlat(pois[j] +" " + location, location)
        poadd.append({
            'place' : pois[j],
            'lat':x,
            'lng':y
        })

    poaddjson = {'places': poadd}
    return jsonify(poaddjson)

@app.route('/path', methods=['POST'])
def path():
    data1 = request.get_json()
    point0 = str(data1['places'][0]['lat'])+','+str(data1['places'][0]['lng'])
    point1 = str(data1['places'][1]['lat'])+','+str(data1['places'][1]['lng'])
    point2 = str(data1['places'][2]['lat'])+','+str(data1['places'][2]['lng'])
    point3 = str(data1['places'][3]['lat'])+','+str(data1['places'][3]['lng'])
    point4 = str(data1['places'][4]['lat'])+','+str(data1['places'][4]['lng'])

    def distancer2(pointa, pointb): #API for distances
        url = "https://trueway-directions2.p.rapidapi.com/FindDrivingPath"

        querystring = {"origin":pointa,"destination":pointb}
        

        headers = {
            "X-RapidAPI-Key": "YOUR-API-KEY-HERE",
            "X-RapidAPI-Host": "trueway-directions2.p.rapidapi.com"
        }

        response = requests.get(url, headers=headers, params=querystring)

        return(response.json()['route']['distance'])

    def haversine(pointa, pointb):    #Formula for distances
    # Splitting the coordinates
        lat1, lon1 = map(float, pointa.split(","))
        lat2, lon2 = map(float, pointb.split(","))

        # Convert to radians
        lat1 = math.radians(lat1)
        lon1 = math.radians(lon1)
        lat2 = math.radians(lat2)
        lon2 = math.radians(lon2)

        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        radius_of_earth = 6371  # in kilometers, change to 3956 for miles
        distance = radius_of_earth * c

        return distance*1000

    disdicter = {}
    disdicter['01'] = haversine(point0, point1)
    disdicter['02'] = haversine(point0, point2)
    # sleep(1)
    disdicter['03'] = haversine(point0, point3)
    disdicter['04'] = haversine(point0, point4)
    # sleep(1)
    disdicter['12'] = haversine(point1, point2)
    disdicter['13'] = haversine(point1, point3)
    # sleep(1)
    disdicter['14'] = haversine(point1, point4)
    disdicter['23'] = haversine(point2, point3)
    # sleep(1)
    disdicter['24'] = haversine(point2, point4)
    disdicter['34'] = haversine(point3, point4)

    distances = disdicter
    def tsp(distances):

        places = ['0', '1', '2', '3', '4']
        permutations = list(itertools.permutations(places))

        shortest_distance = float('inf')
        shortest_path = None

        for perm in permutations:
            path_distance = 0

            for i in range(len(perm) - 1):
                place_a = perm[i]
                place_b = perm[i + 1]
                key = place_a + place_b

                if key in distances:
                    path_distance += distances[key]
                else:

                    key = place_b + place_a
                    path_distance += distances[key]

            if path_distance < shortest_distance:
                shortest_distance = path_distance
                shortest_path = perm

        return shortest_path, shortest_distance

    shortest_path, shortest_distance = tsp(distances)
    placelist = []
    latlist = []
    longlist = []
    finalpathret = {'places':[]}
    for i in range(5):
        placelist.append(data1['places'][int(shortest_path[i])]['place'])
        latlist.append(data1['places'][int(shortest_path[i])]['lat'])
        longlist.append(data1['places'][int(shortest_path[i])]['lng'])
    for j in range(5):
        finalpathret['places'].append({
            'place': placelist[j],
            'lat': latlist[j],
            'lng': longlist[j]
        })
    return jsonify(finalpathret)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

