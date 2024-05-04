# import datetime
from datetime import timedelta, datetime
import json
from flask import Flask, send_from_directory, request, jsonify, make_response
import random
import time
import threading
import numpy as np
from math import radians, cos, sin, asin, sqrt
import requests
from flask_cors import CORS
from dotenv import load_dotenv
import os


load_dotenv('../secret/.env')
opencage_api_key = str(os.getenv('OPENCAGE_API'))

app = Flask(__name__, static_folder='public')
should_send_updates = False

CORS(app)  




@app.route('/search-cities', methods=['GET'])
def search_cities():
    query = request.args.get('query')
    url = f'https://api.opencagedata.com/geocode/v1/json?q={query}&key={opencage_api_key}'
    try:
        response = requests.get(url)
        data = response.json()
        return jsonify(data['results'])  
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route('/get-routes', methods=['POST'])
def get_routes():
    data = request.get_json() 
    print(f"{data=}")
    origin = data.get('origin')
    destination = data.get('destination')

    print(f"{origin=}")
    istanbul_mid = {"label": "Istanbul", "value": {"lat": 41.015137, "lng": 28.979530} }
    belgrade_mid = {"label": "Belgrade", "value": {"lat": 44.786568, "lng": 20.448922} }

    routes = [
        {
            "route_id": 1,
            "flights": [
                {"origin": origin, "destination": istanbul_mid, "departure": "10:00 AM", "arrival": "11:00 AM"},
                {"origin": istanbul_mid, "destination": destination, "departure": "01:00 PM", "arrival": "03:00 PM"}
            ]
        },
        {
            "route_id": 2,
            "flights": [
                {"origin": origin, "destination": destination, "departure": "11:00 AM", "arrival": "07:00 PM"}
            ]
        },
        {
            "route_id": 3,
            "flights": [
                {"origin": origin, "destination": istanbul_mid, "departure": "10:00 AM", "arrival": "11:00 AM"},
                {"origin": istanbul_mid, "destination": belgrade_mid, "departure": "01:00 PM", "arrival": "03:00 PM"},
                {"origin": belgrade_mid, "destination": destination, "departure": "01:00 PM", "arrival": "03:00 PM"}
            ]
        }
    ]
    return make_response(routes)




if __name__ == '__main__':
    app.run(debug=True)
