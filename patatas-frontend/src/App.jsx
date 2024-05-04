import React, { useState } from 'react';
import AsyncSelect from 'react-select/async';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
// import startMarkerImg from '/potato.svg';  // Adjust the path according to your folder structure
import startMarkerImg from '/Green_Arrow_Down.svg';  // Adjust the path according to your folder structure
// import endMarkerImg from '/patatas_bravas.svg';
import endMarkerImg from '/Red_Arrow_Down.svg';
import lukasTotal from '/total.svg'
import hotelBudget from '/budget.svg'
import hotelNormal from '/normal.svg'
import hotelExpensive from '/expensive.svg'
import CreatableSelect from 'react-select/creatable';

import './App.css';
import {useMap, MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import axios from 'axios';
import 'leaflet-polylinedecorator';
// Define marker icons


const colors = ["red", "blue", "green", "purple", "orange", "cyan", "magenta", "lime", "pink", "teal"]; // Extend this list based on the expected number of routes

const cities = {
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
// Get coordinates from the city name
  // Generic function to get coordinates for a given location object
  const getCoordinates = (location) => {
    if (location.value && location.value.lat && location.value.lng) {
      return [location.value.lat, location.value.lng];
    } else if (location.label && cities[location.label]) {
      return [cities[location.label].value.lat, cities[location.label].value.lng];
    }
    return null; // Return null if nothing is applicable
  };


function getColor(index) {
  return colors[index % colors.length]; // Loop through the colors array cyclically
}

const startIcon = new L.Icon({
  iconUrl: startMarkerImg, // ensure you have this image in your public folder or imported
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const endIcon = new L.Icon({
  iconUrl: endMarkerImg, // ensure you have this image in your public folder or imported
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});


// Define orange marker icon
const orangeIcon = new L.Icon({
  iconUrl: 'Orange_Circle.svg',  // Make sure to have this SVG in your public folder or properly imported
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});


const PolylineWithArrows = ({ positions, color }) => {
  const map = useMap();

  React.useEffect(() => {
    if (!map) return;

    // Define the polyline
    const polyline = L.polyline(positions, { color: color });

    // Define the decorator with arrows
    const decorator = L.polylineDecorator(polyline, {
      patterns: [
        // defines the pattern of arrows along the polyline
        { offset: '100%', repeat: 0, symbol: L.Symbol.arrowHead({ pixelSize: 15, polygon: false, pathOptions: { stroke: true, color: color } }) }
      ]
    });

    // Add the polyline and decorator to the map
    polyline.addTo(map);
    decorator.addTo(map);

    // Cleanup function to remove layers when component unmounts
    return () => {
      polyline.remove();
      decorator.remove();
    };
  }, [map, positions, color]); // Dependency array to react appropriately on changes

  return null;
};

function App() {
  const [destination, setDestination] = useState({});
  const [origin, setOrigin] = useState({});
  const [routes, setRoutes] = useState([]);
  const [activeRoute, setActiveRoute] = useState(null);
  const [hoveredIcon, setHoveredIcon] = useState('');
  const [visibleRoutes, setVisibleRoutes] = useState({});  // State to manage visibility of each route
  const [activeRouteIndex, setActiveRouteIndex] = useState(null); // Track the index of the active route


  const fetchCities = async (inputValue) => {
    if (!inputValue) return [];
    try {
      const response = await fetch(`http://localhost:5000/search-cities?query=${encodeURIComponent(inputValue)}`);
      const results = await response.json();
      return results.map(result => ({
        label: result.formatted,
        value: result.geometry,
      }));
    } catch (error) {
      console.error('Error fetching cities:', error);
      return [];
    }
  };

  const handleOriginChange = selectedOption => {
    setOrigin(selectedOption);
    console.log(selectedOption)
  };

  const handleDestinationChange = selectedOption => {
    setDestination(selectedOption);
  };
  const handleRouteClick = (routeIndex, flightIndex) => {
    const routeKey = `route-${routeIndex}-flight-${flightIndex}`;

    // Check if the same route is being clicked
    if (routeIndex === activeRouteIndex) {
      // Reset active route and index if the same route is clicked again
      setActiveRoute(null);
      setActiveRouteIndex(null);
    } else {
      // Set the active route and index
      setActiveRoute(routeKey);
      setActiveRouteIndex(routeIndex);
      scrollToFlightDetail(routeKey);
    }
  };

  
  const fetchRoutes = async () => {
    
    if (origin && origin.value && destination && destination.value) {
        try {
            const response = await axios.post('http://localhost:5000/get-routes', {
                origin: origin,
                destination: destination
            });
            setRoutes(response.data);
            console.log(response.data);
        } catch (error) {
            console.error('Error fetching routes:', error);
        }
    }
};
const scrollToFlightDetail = (id) => {
  const element = document.getElementById(id);
  if (element) {
    element.scrollIntoView({ behavior: "smooth", block: "start" });
    element.classList.add('highlight');
  }
};
  // Custom styles for react-select
  const customStyles = {
    menu: (provided) => ({
      ...provided,
      zIndex: 1000 // High enough to be on top of almost anything else in the view
    }),
    option: (provided, state) => ({
      ...provided,
      color: 'black', // This will make the text color black
      backgroundColor: state.isSelected ? 'lightgray' : 'white'
    }),
    // You can add more customizations here for other parts of the select
  };
  return (
    <div className="App">
      <div className="head-container">
        <a href="https://www.thespanishchef.com/recipes/the-ultimate-patatas-bravas" target="_blank">
          <img src={startMarkerImg} className="logo" alt="Vite logo" />
        </a>
        <h1>TravelAdjuster</h1>
        <a href="https://www.thespanishchef.com/recipes/the-ultimate-patatas-bravas" target="_blank">
          <img src={endMarkerImg} className="logo react" alt="React logo" />
        </a>
      </div>
      <div className='select-container'>
        {/* <AsyncSelect
          className='selection'
          cacheOptions
          loadOptions={fetchCities}
          onChange={handleOriginChange}
          placeholder="Select origin..."
          styles={customStyles}
        />
        <br/>
        <br/>

        <AsyncSelect 
          className='selection'
          cacheOptions
          loadOptions={fetchCities}
          onChange={handleDestinationChange}
          placeholder="Select destination..."
          styles={customStyles}
        /> */}

        <CreatableSelect
          className='selection'
          isClearable
          cacheOptions
          loadOptions={fetchCities}
          onChange={handleOriginChange}
          placeholder="Select or type origin..."
        />
        <CreatableSelect
          className='selection'
          isClearable
          cacheOptions
          loadOptions={fetchCities}
          onChange={handleDestinationChange}
          placeholder="Select or type destination..."
        />

        <button onClick={fetchRoutes}>Find Routes</button>

      </div>
      <br/>
      <br/>
      <MapContainer center={[50, 10]} zoom={4} scrollWheelZoom={true} style={{ height: '70vh', width: '100%' }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {getCoordinates(origin) && (
          <Marker 
            position={getCoordinates(origin)} 
            icon={startIcon}
          >
            <Popup>
              Start of Trip: {origin.label || "Unknown Location"}
            </Popup>
          </Marker>
        )}
        {getCoordinates(destination) && (
          <Marker 
            position={getCoordinates(destination)} 
            icon={endIcon}
          >
            <Popup>
              End of Trip: {destination.label || "Unknown Location"}
            </Popup>
          </Marker>
        )}
{routes && routes.map((route, routeIndex) => 
  route.flights?.slice(1).map((stop, stopIndex) => (
    <Marker key={`stop-${routeIndex}-${stopIndex}`} position={[stop.origin.value.lat, stop.origin.value.lng]} icon={orangeIcon}>
      <Popup>
        {console.log(stop.origin)}
        {Object.entries(stop.origin)
          .filter(([key]) => key !== 'value' && key !== 'malue')  // Filter out 'value' and 'malue' keys
          .map(([key, value], index) => (
            <div key={index}>
              <b>{key}:</b> {value}  
            </div>
          ))
        }
      </Popup>
    </Marker>
)))}
        {routes.map((route, routeIndex) =>
          route.flights.map((flight, flightIndex) => {
            let flightOrigin = [flight.origin.value.lat, flight.origin.value.lng];
            let flightDestination = [flight.destination.value.lat, flight.destination.value.lng];
            const flightKey = `route-${routeIndex}-flight-${flightIndex}`;

            // Render polyline only if its route is the active route or no route is active
            if (routeIndex === activeRouteIndex || activeRouteIndex === null) {
              return (
                <Polyline
                  key={flightKey}
                  positions={[flightOrigin, flightDestination]}
                  color={getColor(routeIndex)}
                  weight={5}
                  dashArray="10, 20"
                  eventHandlers={{
                    click: () => handleRouteClick(routeIndex, flightIndex)
                  }}
                >
                  <Popup>
                    {`Flight from ${flight.origin.label} to ${flight.destination.label}`}
                    <br />
                    {/* {`Departure: ${flight.departure}, Arrival: ${flight.arrival}`} */}
                  </Popup>
                </Polyline>
              );
            }
            return null;
          })
        )}
      </MapContainer>



      <div className="route-details-container">
        {routes.map((route, index) => (
          <div key={`route-${index}`} className="route-card">
            <h4>Route {index + 1}</h4>
            {route.flights.map((flight, idx) => (
              // <div key={`route-${index}-flight-${idx}`} className="flight-card">
              <div
                id={`route-${index}-flight-${idx}`} // Set the id here
                className={`flight-card ${activeRoute === `route-${index}-flight-${idx}` ? 'highlight' : ''}`}
                key={`route-${index}-flight-${idx}`}
              >
                {Object.entries(flight).map(([key, value]) => {
                  // Check if value is an object and handle it appropriately
                  let displayValue;
                  if (typeof value === 'object' && value !== null) {
                    // Assuming 'value' might be an object with properties 'label' and 'value'
                    displayValue = `${value.label} (${value.value.lat}, ${value.value.lng})`; // Adjust this according to what 'value' actually contains
                    console.log(displayValue);
                  } else {
                    // It's not an object, so we can display it directly
                    displayValue = value;
                  }
                  return (
                    <p key={`route-${index}-flight-${idx}-${key}`}>
                      <strong>{key[0].toUpperCase() + key.slice(1)}:</strong> {displayValue}
                    </p>
                  );
                })}
              </div>
            ))}
          </div>
        ))}
      </div>
      <div className="svg-container">
        <div className="svg-im">
          <img
            src={hotelBudget}
            alt="Icon 1 Description"
            className={`example-icon ${hoveredIcon === 'icon1' ? 'hovered' : ''}`}
            onMouseEnter={() => setHoveredIcon('icon1')}
            onMouseLeave={() => setHoveredIcon('')}
          />
          <div className='svg-content' style={{display: hoveredIcon === 'icon1' ? 'block' : 'none'}}>
            <h1>20 - 50 Eur</h1>
            <p>Economic Option</p>
          </div>
        </div>
        <div className="svg-im">
          <img
            src={hotelNormal}
            alt="Icon 2 Description"
            className={`example-icon ${hoveredIcon === 'icon2' ? 'hovered' : ''}`}
            onMouseEnter={() => setHoveredIcon('icon2')}
            onMouseLeave={() => setHoveredIcon('')}
          />
          <div className='svg-content' style={{display: hoveredIcon === 'icon2' ? 'block' : 'none'}}>
            <h1>60 - 150 Eur</h1>
            <p>Base Option</p>
          </div>
        </div>
        <div className="svg-im">
          <img
            src={hotelExpensive}
            alt="Icon 3 Description"
            className={`example-icon ${hoveredIcon === 'icon3' ? 'hovered' : ''}`}
            onMouseEnter={() => setHoveredIcon('icon3')}
            onMouseLeave={() => setHoveredIcon('')}
          />
          <div className='svg-content' style={{display: hoveredIcon === 'icon3' ? 'block' : 'none'}}>
            <h1>160 - 300 Eur</h1>
            <p>Luxurious Option</p>
          </div>
        </div>


      </div>

    </div>
  );
}

export default App;
