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
import wikipedia
from transformers import pipeline
from numpy import dot
from numpy.linalg import norm

load_dotenv('../secret/.env')
opencage_api_key = str(os.getenv('OPENCAGE_API'))

app = Flask(__name__, static_folder='public')
should_send_updates = False

CORS(app)  

common_embedder = pipeline('feature-extraction', model='sentence-transformers/all-MiniLM-L6-v2')



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

similarities = {('Barcelona', 'hiking'): -0.07356697701118468,
 ('Barcelona', 'architecture'): 0.10132157119581477,
 ('Barcelona', 'opera'): 0.0750066973931789,
 ('Barcelona', 'beach'): 0.22013704457133224,
 ('Barcelona', 'skiing'): -0.02694621132750901,
 ('Barcelona', 'history'): -0.027294328159019297,
 ('Barcelona', 'clubbing'): 0.11107487504935376,
 ('Barcelona', 'football'): 0.042780815338316375,
 ('Barcelona', 'concerts'): 0.010298471553267753,
 ('Barcelona', 'pizza'): 0.12080471090685345,
 ('Barcelona', 'beer'): -0.0434480307824868,
 ('Paris', 'hiking'): -0.021730465969136047,
 ('Paris', 'architecture'): 0.09486664462158673,
 ('Paris', 'opera'): 0.07902341608888479,
 ('Paris', 'beach'): 0.14146735937106836,
 ('Paris', 'skiing'): -0.04848326415004869,
 ('Paris', 'history'): -0.01041568185702632,
 ('Paris', 'clubbing'): -0.06741052443472036,
 ('Paris', 'football'): 0.021670761732746967,
 ('Paris', 'concerts'): 0.06398347958080762,
 ('Paris', 'pizza'): 0.022419092276659416,
 ('Paris', 'beer'): -0.006662912776842151,
 ('Rome', 'hiking'): 0.051164810598574646,
 ('Rome', 'architecture'): 0.2726075939056531,
 ('Rome', 'opera'): 0.05374669321353546,
 ('Rome', 'beach'): 0.11618553313343374,
 ('Rome', 'skiing'): 0.020630777363221157,
 ('Rome', 'history'): -0.01243057015952246,
 ('Rome', 'clubbing'): 0.12001817063585034,
 ('Rome', 'football'): 0.028976306551724042,
 ('Rome', 'concerts'): 0.012435610065274284,
 ('Rome', 'pizza'): 0.08444656738034984,
 ('Rome', 'beer'): 0.08589049665677106,
 ('Amsterdam', 'hiking'): -0.06588641815699058,
 ('Amsterdam', 'architecture'): 0.08699959168351588,
 ('Amsterdam', 'opera'): 0.10597750899531483,
 ('Amsterdam', 'beach'): 0.02331846810964808,
 ('Amsterdam', 'skiing'): -0.06469483959475988,
 ('Amsterdam', 'history'): 0.019437931202952636,
 ('Amsterdam', 'clubbing'): 0.00792180493032342,
 ('Amsterdam', 'football'): -0.07195054426732017,
 ('Amsterdam', 'concerts'): -0.0022590388391344105,
 ('Amsterdam', 'pizza'): -0.055100433112926436,
 ('Amsterdam', 'beer'): 0.049961470273999414,
 ('Munich', 'hiking'): -0.0090042463423077,
 ('Munich', 'architecture'): 0.19384635272220757,
 ('Munich', 'opera'): 0.09682061576827945,
 ('Munich', 'beach'): 0.1631885860569966,
 ('Munich', 'skiing'): 0.03555049765572852,
 ('Munich', 'history'): 0.006373054698914993,
 ('Munich', 'clubbing'): -0.017377191571195914,
 ('Munich', 'football'): 0.05901160171667882,
 ('Munich', 'concerts'): 0.026376283323454378,
 ('Munich', 'pizza'): 0.002813229244870872,
 ('Munich', 'beer'): 0.13858826129176283,
 ('London', 'hiking'): -0.10573101600367618,
 ('London', 'architecture'): 0.12331598688925474,
 ('London', 'opera'): -0.04478477673963469,
 ('London', 'beach'): 0.06371823035938812,
 ('London', 'skiing'): -0.1339118649484115,
 ('London', 'history'): 0.06033520495804659,
 ('London', 'clubbing'): -0.03336119585895229,
 ('London', 'football'): 0.03479274963655813,
 ('London', 'concerts'): 0.00998033592414719,
 ('London', 'pizza'): -0.005020246053674749,
 ('London', 'beer'): 0.02506233315755639,
 ('Prague', 'hiking'): 0.021522501066855552,
 ('Prague', 'architecture'): 0.03946172103095877,
 ('Prague', 'opera'): 0.039217117669271294,
 ('Prague', 'beach'): -0.008794571899388655,
 ('Prague', 'skiing'): 0.09536231486561954,
 ('Prague', 'history'): 0.031830112526689006,
 ('Prague', 'clubbing'): 0.1091989423976992,
 ('Prague', 'football'): 0.08831911711522952,
 ('Prague', 'concerts'): 0.07402965255371556,
 ('Prague', 'pizza'): 0.13463834105522063,
 ('Prague', 'beer'): 0.17879898294627172,
 ('Madrid', 'hiking'): -0.09265190022371829,
 ('Madrid', 'architecture'): 0.10104407281632516,
 ('Madrid', 'opera'): 0.0876149095921664,
 ('Madrid', 'beach'): 0.10176841147807146,
 ('Madrid', 'skiing'): -0.06141186616280755,
 ('Madrid', 'history'): -0.023978644774820763,
 ('Madrid', 'clubbing'): 0.03522604930118705,
 ('Madrid', 'football'): 0.07412291248356905,
 ('Madrid', 'concerts'): 0.008840960660417818,
 ('Madrid', 'pizza'): 0.10324872605249855,
 ('Madrid', 'beer'): -0.06488605296770907,
 ('Florence', 'hiking'): -0.026032444586902674,
 ('Florence', 'architecture'): 0.0692295982954012,
 ('Florence', 'opera'): 0.11485299335362022,
 ('Florence', 'beach'): -0.046867944637792126,
 ('Florence', 'skiing'): 0.12757837593986482,
 ('Florence', 'history'): 0.0285938709465593,
 ('Florence', 'clubbing'): 0.16229479618088485,
 ('Florence', 'football'): 0.07977275132680153,
 ('Florence', 'concerts'): 0.0029259033247493256,
 ('Florence', 'pizza'): 0.06762239294576958,
 ('Florence', 'beer'): 0.07164891559796585,
 ('Vienna', 'hiking'): 0.006504879375459346,
 ('Vienna', 'architecture'): 0.0405785290565561,
 ('Vienna', 'opera'): -0.2419204235738462,
 ('Vienna', 'beach'): 0.26544323329921143,
 ('Vienna', 'skiing'): -0.08070003585885227,
 ('Vienna', 'history'): 0.07720526362212467,
 ('Vienna', 'clubbing'): -0.028514251797467836,
 ('Vienna', 'football'): 0.046372500743628704,
 ('Vienna', 'concerts'): -0.027779057100728123,
 ('Vienna', 'pizza'): -0.07872865882834562,
 ('Vienna', 'beer'): -0.03456636110062178,
 ('Berlin', 'hiking'): -0.07599136385633852,
 ('Berlin', 'architecture'): 0.08376211717957989,
 ('Berlin', 'opera'): 0.0420990547977548,
 ('Berlin', 'beach'): 0.11476090444048845,
 ('Berlin', 'skiing'): -0.036097004075440454,
 ('Berlin', 'history'): -0.014946901854646946,
 ('Berlin', 'clubbing'): -0.011365313930671406,
 ('Berlin', 'football'): 0.0846832342811371,
 ('Berlin', 'concerts'): 0.025670629939068174,
 ('Berlin', 'pizza'): 0.028214554323335913,
 ('Berlin', 'beer'): 0.023466524500202073,
 ('Lisbon', 'hiking'): -0.0022459274262316056,
 ('Lisbon', 'architecture'): 0.1238402291547893,
 ('Lisbon', 'opera'): 0.05379646671877261,
 ('Lisbon', 'beach'): 0.1974543641796051,
 ('Lisbon', 'skiing'): -0.02585409165828346,
 ('Lisbon', 'history'): -0.033945383637814776,
 ('Lisbon', 'clubbing'): 0.07193144606384101,
 ('Lisbon', 'football'): -0.0009617834790488888,
 ('Lisbon', 'concerts'): -0.041344225876915684,
 ('Lisbon', 'pizza'): 0.00026850116224943,
 ('Lisbon', 'beer'): -0.041820632511691824,
 ('Budapest', 'hiking'): -0.04426586485956246,
 ('Budapest', 'architecture'): 0.124243629621924,
 ('Budapest', 'opera'): 0.06728686390438651,
 ('Budapest', 'beach'): 0.07222731094922508,
 ('Budapest', 'skiing'): -0.03404771868838362,
 ('Budapest', 'history'): -0.017251990747172548,
 ('Budapest', 'clubbing'): -0.029789253155632762,
 ('Budapest', 'football'): -0.020019579722217497,
 ('Budapest', 'concerts'): 0.027057397556013243,
 ('Budapest', 'pizza'): -0.02066238177595051,
 ('Budapest', 'beer'): 0.06842558834726047,
 ('Brussels', 'hiking'): -0.046313112518283725,
 ('Brussels', 'architecture'): -0.003170204560905411,
 ('Brussels', 'opera'): -0.023175242010111015,
 ('Brussels', 'beach'): 0.08045519865475982,
 ('Brussels', 'skiing'): -0.05775937734531884,
 ('Brussels', 'history'): -0.03895638936126361,
 ('Brussels', 'clubbing'): -0.05208634235518569,
 ('Brussels', 'football'): 0.005742880445573742,
 ('Brussels', 'concerts'): 0.0191491888791957,
 ('Brussels', 'pizza'): 0.03634513632387012,
 ('Brussels', 'beer'): 0.06887153473213734,
 ('Dublin', 'hiking'): -0.0194666969595631,
 ('Dublin', 'architecture'): 0.05463609417381506,
 ('Dublin', 'opera'): -0.11870501238475889,
 ('Dublin', 'beach'): 0.1409375064445101,
 ('Dublin', 'skiing'): -0.05022674718325068,
 ('Dublin', 'history'): 0.04315761860175913,
 ('Dublin', 'clubbing'): 0.04029767046054733,
 ('Dublin', 'football'): 0.019125819672658275,
 ('Dublin', 'concerts'): -0.046182751468728495,
 ('Dublin', 'pizza'): -0.11397780817220263,
 ('Dublin', 'beer'): 0.055835739510743096,
 ('Zurich', 'hiking'): 0.002586528910616923,
 ('Zurich', 'architecture'): 0.13109136423816276,
 ('Zurich', 'opera'): 0.0793977925549077,
 ('Zurich', 'beach'): 0.1855966876104852,
 ('Zurich', 'skiing'): 0.08470291652426845,
 ('Zurich', 'history'): -0.0032532925828185127,
 ('Zurich', 'clubbing'): -0.018165406084258533,
 ('Zurich', 'football'): 0.03204318445946471,
 ('Zurich', 'concerts'): 0.009894054822913901,
 ('Zurich', 'pizza'): 0.047736145834714534,
 ('Zurich', 'beer'): 0.00737129993771901,
 ('Milan', 'hiking'): -0.10261514414229021,
 ('Milan', 'architecture'): 0.1956268334298206,
 ('Milan', 'opera'): 0.1775256039353126,
 ('Milan', 'beach'): 0.08688453709648292,
 ('Milan', 'skiing'): -0.08076042642779312,
 ('Milan', 'history'): -0.04314616127373127,
 ('Milan', 'clubbing'): 0.05804084820111719,
 ('Milan', 'football'): 0.03808972602387922,
 ('Milan', 'concerts'): 0.0426010579114743,
 ('Milan', 'pizza'): 0.17683344635591303,
 ('Milan', 'beer'): -0.035102928371866716}


interests = ["hiking","architecture","opera","beach","skiing","history","clubbing","football","concerts","pizza","beer"]



def get_all_embeddings(cities, interests):
    def get_embeddings(text,embedder):
        """
        Generate embeddings for the given text using the specified embedder and average across all tokens.
        """
        embeddings = embedder(text)
        # The output is a list of lists, one for each token in the text
        # We take the mean to get a single vector for the text
        return [sum(col) / len(col) for col in zip(*embeddings[0])]

    # Using the same model for both for consistency
    # common_embedder = pipeline('feature-extraction', model='sentence-transformers/all-MiniLM-L6-v2')

    # Generating embeddings for cities
    city_embeddings = {}
    for city in cities:
        intro_text = get_wikipedia_intro(city)
        if intro_text:
            city_embeddings[city] = get_embeddings(intro_text, common_embedder)

    # Generating embeddings for interests
    interest_embeddings = {}
    for interest in interests:
        interest_embeddings[interest] = get_embeddings(interest, common_embedder)

    return city_embeddings,interest_embeddings



def get_wikipedia_intro(city_name):
    """
    Fetch the introductory paragraph of a city from Wikipedia.
    """
    try:
        # Get the summary (introductory text) of the page
        summary = wikipedia.summary(city_name, sentences=5)  # Adjust the number of sentences as needed
        return summary
    except wikipedia.exceptions.PageError:
        print(f"No page found for {city_name}")
        return None
    except wikipedia.exceptions.DisambiguationError as e:
        print(f"Disambiguation error for {city_name}, taking first option: {e.options[0]}")
        return wikipedia.summary(e.options[0], sentences=5)




# Function to calculate travel time between two locations
def calculate_train_travel_time(origin, destination):
    global trains_df
    
    row = trains_df[(trains_df['Start'] == origin) & (trains_df['End'] == destination)]
    row_alt = trains_df[(trains_df['End'] == origin) & (trains_df['Start'] == destination)]
    if not row.empty:
        time = row['travel_time'].values[0]
        return time
    elif not row_alt.empty:
        time = row_alt['travel_time'].values[0]
        return time
    else:
        return None

# Function to calculate total travel time for a route
def calculate_total_train_travel_time(route_id, routes):

    route_flights = {route['route_id']: route['flights'] for route in routes}

    flights = route_flights.get(route_id, [])
    total_time = 0
    for i, flight in enumerate(flights):
        origin = flight['origin']['label']
        destination = flight['destination']['label']
        layover_time = 0
        if i < len(flights) - 1:
            next_flight = flights[i + 1]
            layover_destination = next_flight['destination']['label']
            layover_time = calculate_train_travel_time(destination, layover_destination)
        travel_time = calculate_train_travel_time(origin, destination)
        if travel_time is not None and layover_time is not None:
            total_time += travel_time + layover_time
    return int(total_time)


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
    # print(f"{cities[source_match]}")
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


def get_similarities(city_embeddings,interest_embeddings):
    def cosine_similarity(vec1, vec2):
        """
        Calculate the cosine similarity between two vectors.
        Args:
        vec1 (list): First vector.
        vec2 (list): Second vector.

        Returns:
        float: Cosine similarity between the two vectors.
        """
        return dot(vec1, vec2) / (norm(vec1) * norm(vec2))

    def find_similarities(cities, interests, city_embeddings, interest_embeddings):
        similarities = {}
        for city in cities:
            for interest in interests:
                sim_score = cosine_similarity(city_embeddings[city], interest_embeddings[interest])
                similarities[(city, interest)] = sim_score
        return similarities

    similarities = find_similarities(city_embeddings.keys(), interest_embeddings.keys(), city_embeddings, interest_embeddings)
    return similarities


def sort_routes(interests,routes,similarities):
    layover_similarity = {}
    
    for route in routes:
        layovers = [flight['destination']['label'] for flight in route['flights'][:-1]]  
        print(f"{type(layovers)=}")
        print(f"{layovers=}")

        for layover in layovers:
            if layover not in layover_similarity:
                layover_similarity[layover] = 0
            for interest in interests:
                if (layover, interest) in similarities:
                    layover_similarity[layover] += similarities[(layover, interest)]
    
    sorted_routes = sorted(routes[1:], key=lambda x: sum(layover_similarity[flight['destination']['label']] for flight in x['flights'][:-1]), reverse=True)
    
    sorted_routes.insert(0, routes[0])
    return sorted_routes


@app.route('/search-cities', methods=['GET'])
def search_cities():
    # print("API Request for city query sent")
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
    global trains_df

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



    for route in transit_routes[1:]:
        route['Total Train Travel Time (minutes)'] = calculate_total_train_travel_time(route['route_id'], transit_routes) # this is now our train routes
        # print(f"{route['total_travel_time (minutes)']=}")


    # city_embeddings, interest_embeddings = get_all_embeddings(cities.keys(), interests)
    
    # similarities = get_similarities(city_embeddings, interest_embeddings)

    sorted_routes = sort_routes(interests, transit_routes, similarities)
    print(f"{sorted_routes=}")
    return make_response(sorted_routes)

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
    global trains_df

    G1 = read_graph("../data/test_.csv")
    trains_df = pd.read_csv('../data/TRAIN_FINAL_2.csv')


    app.run(debug=True)