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
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

load_dotenv('../secret/.env')
opencage_api_key = str(os.getenv('OPENCAGE_API'))

app = Flask(__name__, static_folder='public')
should_send_updates = False

CORS(app)  



cities = {
    'Barcelona': {"label": "Barcelona", "value": {"lat": 41.2971, "lng": 2.07846}},
    'Paris': {"label": "Paris", "value": {"lat": 49.454399, "lng": 2.11278}},
    'Rome': {"label": "Rome", "value": {"lat": 53.745098, "lng": -2.88306}},
    'Amsterdam': {"label": "Amsterdam", "value": {"lat": 52.308601, "lng": 4.76389}},
    'Munich': {"label": "Munich", "value": {"lat": 48.353802, "lng": 11.7861}},
    'London': {"label": "London", "value": {"lat": 51.874699, "lng": -0.368333}},
    'Prague': {"label": "Prague", "value": {"lat": 50.1008, "lng": 14.26}},
    'Madrid': {"label": "Madrid", "value": {"lat": 40.471926, "lng": -3.56264}},
    'Vienna': {"label": "Vienna", "value": {"lat": 48.110298, "lng": 16.5697}},
    'Berlin': {"label": "Berlin", "value": {"lat": 52.362247, "lng": 13.500672}},
    'Lisbon': {"label": "Lisbon", "value": {"lat": 38.7813, "lng": -9.13592}},
    'Budapest': {"label": "Budapest", "value": {"lat": 47.42976, "lng": 19.261093}},
    'Brussels': {"label": "Brussels", "value": {"lat": 50.901402, "lng": 4.48444}},
    'Dublin': {"label": "Dublin", "value": {"lat": 53.428713, "lng": -6.262121}},
    'Milan': {"label": "Milan", "value": {"lat": 45.673901, "lng": 9.70417}},
    'Florence': {"label": "Florence", "value": {"lat": 43.7696, "lng": 11.2558}},
    'Zurich': {"label": "Zurich", "value": {"lat": 47.3769, "lng": 8.5417}}
}

events_by_city = {
    "Barcelona": [
        "La Mercè Festival - Usually held from September 20th to 24th.",
        "Primavera Sound Festival - Usually held in late May or early June.",
        "Sonar Festival - Usually held in June."
    ],
    "Paris": [
        "Bastille Day (July 14th) - National holiday with festivities including fireworks and parades.",
        "Paris Fashion Week - Typically held in February/March and September/October.",
        "Nuit Blanche - Annual all-night arts festival held in October."
    ],
    "Amsterdam": [
        "King's Day (Koningsdag) - Celebrated on April 27th.",
        "Amsterdam Dance Event (ADE) - Typically held in October.",
        "Keukenhof Flower Exhibition - Usually open from late March to mid-May."
    ],
    "Munich": [
        "Oktoberfest - Usually held from late September to the first weekend in October.",
        "Tollwood Winter Festival - Typically held from late November to December.",
        "Munich Christmas Market - Usually open from late November to December."
    ],
    "London": [
        "Notting Hill Carnival - Typically held on the August bank holiday weekend.",
        "Wimbledon Championships - Usually held in late June and early July.",
        "London Fashion Week - Held twice a year in February/March and September/October."
    ],
    "Madrid": [
        "San Isidro Festival - Celebrated in May with various events throughout the month.",
        "Madrid Pride Parade (Orgullo) - Usually held in late June.",
        "FITUR (International Tourism Fair) - Typically held in January."
    ],
    "Vienna": [
        "Vienna Opera Ball - Usually held in late February.",
        "Vienna Film Festival (Viennale) - Typically held in October.",
        "Vienna Christmas Market - Usually open from mid-November to December."
    ],
    "Berlin": [
        "Berlinale (Berlin International Film Festival) - Typically held in February.",
        "Christopher Street Day (CSD Berlin) - Berlin's Pride parade, usually held in late July.",
        "Festival of Lights - Usually held in October."
    ],
    "Lisbon": [
        "Festas de Lisboa (Lisbon Festivities) - Celebrated throughout June.",
        "NOS Alive Festival - Usually held in July.",
        "Lisbon International Film Festival (LEFFEST) - Typically held in November."
    ],
    "Budapest": [
        "Budapest Wine Festival - Usually held in September.",
        "Sziget Festival - One of Europe's largest music festivals, typically held in August.",
        "Budapest Spring Festival - Usually held in March/April."
    ],
    "Brussels": [
        "Brussels Flower Carpet - A biennial event usually held in August.",
        "Brussels Christmas Market - Usually open from late November to December.",
        "Brussels Jazz Festival - Typically held in May."
    ],
    "Dublin": [
        "St. Patrick's Day Festival - Celebrated on March 17th.",
        "Dublin Horse Show - Typically held in August.",
        "Dublin Fringe Festival - Usually held in September."
    ],
    "Zurich": [
        "Street Parade - Europe's largest techno party, typically held in August.",
        "Zurich Film Festival - Usually held in September.",
        "Zurich Christmas Market - Usually open from late November to December."
    ],
    "Milan": [
        "Milan Fashion Week - Typically held in February/March and September/October.",
        "Milan Design Week (Salone del Mobile) - Usually held in April.",
        "Festa del Naviglio - A cultural festival usually held in June along the Naviglio Grande canal."
    ]
}



def read_graph(graph_path):
    global G1

    given_data = pd.read_csv(graph_path)

    G1 = nx.from_pandas_edgelist(given_data, 'Departure City', 'Arrival City', create_using=nx.DiGraph())

    # Plot the graph
    # plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G1)  # positions for all nodes
    nx.draw_networkx_nodes(G1, pos, node_size=700)
    nx.draw_networkx_edges(G1, pos, edgelist=G1.edges(), arrowstyle='->', arrowsize=20)
    nx.draw_networkx_labels(G1, pos, font_size=12, font_family='sans-serif')
    # plt.title("Network Graph of City Connections")
    # plt.axis('off')  # Turn off the axis
    # plt.show()
    return G1


def find_matching_city(G, input_city):
    """Return the first city in the graph that contains the input_city substring, or None if no match is found."""
    for node in G.nodes:
        if input_city in node:
            return node
    return None  # or any appropriate value indicating no match was found

def find_transit_routes(G, source, destination):
    """
    Find all routes from matching source to destination cities with possible transits
    """
    source_match = find_matching_city(G, source)
    destination_match = find_matching_city(G, destination)
    all_routes = []
    route_id = 1  
    if source_match is None or destination_match is None:
        return None # or return old dummy data with direct flight
    
    cities[source_match]['Events'] = events_by_city[source_match]
    print(f"{cities[source_match]}")
    if G.has_edge(source_match, destination_match):
        all_routes.append({
            "route_id": route_id,
            "flights": [{"origin": cities[source_match], "destination": cities[destination_match]}]
        })
        route_id += 1
    # Transit routes

    paths = list(nx.all_simple_paths(G, source_match, destination_match))
    for path in paths:
        if 3<= len(path) <= 4:  # Exclude direct flights
            route_flights = []
            for i in range(len(path) - 1):
                if path[i] in events_by_city:
                    cities[path[i]]['Events'] = events_by_city[path[i]]
                route_flights.append({"origin": cities[path[i]], "destination": cities[path[i+1]]})
            all_routes.append({
                "route_id": route_id, 
                "flights": route_flights
            })
            route_id += 1

    # Sort routes by the number of trips
    # all_routes.sort(key=lambda x: x['route_id'])

    return all_routes




@app.route('/search-cities', methods=['GET'])
def search_cities():
    print("API Request for city query sent")
    query = request.args.get('query')
    url = f'https://api.opencagedata.com/geocode/v1/json?q={query}&key={opencage_api_key}'
    try:
        response = requests.get(url)
        data = response.json()
        return jsonify(data['results'])  
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

def find_city_substring(graph, city_name):
    for node in graph.nodes:
        if  node.lower() in city_name.lower():
            return node
    return None

@app.route('/get-routes', methods=['POST'])
def get_routes():
    global G1

    data = request.get_json() 
    # print(f"{data=}")
    origin = data.get('origin')
    destination = data.get('destination')

    # print(f"{origin=}")
    # istanbul_mid = {"label": "Istanbul", "value": {"lat": 41.015137, "lng": 28.979530} }
    # belgrade_mid = {"label": "Belgrade", "value": {"lat": 44.786568, "lng": 20.448922} }


    # for every city in graph, check if it is in 
    source = find_city_substring(G1, origin["label"])
    destin = find_city_substring(G1, destination["label"])
    # if source:
    #     # print(f"Node '{source}' contains substring of.")
    # else:
    #     # print("No node contains the city as a substring.")
    #     # print(f"{source,G1=}")
    #     for node in G1.nodes():
    #         # print(node)


    transit_routes = find_transit_routes(G1, source, destin)
    return make_response(transit_routes)


    routes = [
        {
            "route_id": 1,
            "flights": [
                {"origin": origin, "destination": cities['Paris'], "departure": "10:00 AM", "arrival": "11:00 AM"},
                {"origin": cities['Paris'], "destination": destination, "departure": "01:00 PM", "arrival": "03:00 PM"}
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
                {"origin": origin, "destination": cities['Paris'], "departure": "10:00 AM", "arrival": "11:00 AM"},
                {"origin": cities['Paris'], "destination": cities['Milan'], "departure": "01:00 PM", "arrival": "03:00 PM"},
                {"origin": cities['Milan'], "destination": destination, "departure": "01:00 PM", "arrival": "03:00 PM"}
            ]
        }
    ]
    return make_response(routes)




if __name__ == '__main__':
    global G1
    G1 = read_graph("../data/test_.csv")
    app.run(debug=True)