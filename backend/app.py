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



def find_matching_cities(G, input_city):
    """
    Return a list of cities in the graph that contain the input_city substring, case-sensitive.
    """
    return [node for node in G.nodes if input_city in node]

def has_direct_route(G, source, destination):
    """
    Check if there is a direct route between any matching source and destination cities.
    """
    source_matches = find_matching_cities(G, source)
    destination_matches = find_matching_cities(G, destination)
    for src in source_matches:
        for dest in destination_matches:
            if G.has_edge(src, dest):
                return True
            elif G.has_edge(dest,src):
                return True
    return False

def find_transit_routes(G, source, destination):
    """
    Find all routes from matching source to destination cities with possible transits.
    """
    source_matches = find_matching_cities(G, source)
    destination_matches = find_matching_cities(G, destination)
    all_routes = []
    for src in source_matches:
        for dest in destination_matches:
            paths = list(nx.all_simple_paths(G, src, dest))
            #paths_reverse = list(nx.all_simple_paths(G,dest,src))
            #print(paths)
            #print(paths_reverse)
            for path in paths:
                if 3 <= len(path) <= 4:
                    formatted_path = " -> ".join(path)
                    all_routes.append(formatted_path)
    return paths
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
    print(f"{data=}")
    origin = data.get('origin')
    destination = data.get('destination')

    print(f"{origin=}")
    # istanbul_mid = {"label": "Istanbul", "value": {"lat": 41.015137, "lng": 28.979530} }
    # belgrade_mid = {"label": "Belgrade", "value": {"lat": 44.786568, "lng": 20.448922} }
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
        'Milan': {"label": "Milan", "value": {"lat": 45.673901, "lng": 9.70417}}
    }

    # for every city in graph, check if it is in 
    source = find_city_substring(G1, origin["label"])
    destin = find_city_substring(G1, destination["label"])
    if source:
        print(f"Node '{source}' contains substring of.")
    else:
        print("No node contains the city as a substring.")
        print(f"{source,G1=}")
        for node in G1.nodes():
            print(node)

    if has_direct_route(G1, source, destin):
        print(f"There is a direct route from {source} to {destin}.")
        print("additional steps: ")
        transit_routes = find_transit_routes(G1, source, destin)
        print("Possible transit routes found:")
        for route in transit_routes:
            print(route)
    else:
        print("No direct route found. Checking for transit routes...")
        transit_routes = find_transit_routes(G1, source, destin)
        if transit_routes:
            print("Possible transit routes found:")
            for route in transit_routes:
                if 3 <= len(route) <= 4:
                    print(route)
        else:
            print("No possible transit routes found.")




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