import React, { useState } from 'react';
import AsyncSelect from 'react-select/async';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
// import startMarkerImg from '/potato.svg';  // Adjust the path according to your folder structure
import startMarkerImg from '/Green_Arrow_Down.svg';  // Adjust the path according to your folder structure
// import endMarkerImg from '/patatas_bravas.svg';
import endMarkerImg from '/Red_Arrow_Down.svg';

import './App.css';
import {useMap, MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import axios from 'axios';
import 'leaflet-polylinedecorator';
// Define marker icons
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
  iconUrl: '/Orange_Arrow_Down.svg',  // Make sure to have this SVG in your public folder or properly imported
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

function createNumberIcon(number) {
  const icon = L.divIcon({
    className: 'custom-number-icon', // Custom class for additional styling
    html: `<div style="background-color: white; border: 1px solid black; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; font-size: 12px;">
            ${number}
           </div>`, // HTML content for the icon
    iconSize: [30, 30], // Size of the icon
    iconAnchor: [15, 15], // Anchor position to properly position the icon
  });
  return icon;
}
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
  const [markedPositions, setMarkedPositions] = useState([]);
  const isPositionMarked = (lat, lng) => {
    const precision = 0.00001; // Fine-tune precision as needed
    const marked = markedPositions.some(pos =>
      Math.abs(pos.lat - lat) < precision && Math.abs(pos.lng - lng) < precision
    );
    if (marked) {
      console.log(`Position already marked: (${lat}, ${lng})`);
    }
    return marked;
  };

  const addMarkedPosition = (lat, lng) => {
    console.log(`Adding marked position: (${lat}, ${lng})`);
    setMarkedPositions(current => [...current, { lat, lng }]);
  };
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

  
  const fetchRoutes = async () => {
    
    if (origin && origin.value && destination && destination.value) {
        setMarkedPositions([]);

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
        <AsyncSelect
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
        />
        <button onClick={fetchRoutes}>Find Routes</button>

      </div>
      <br/>
      <br/>
      <MapContainer center={[50, 10]} zoom={4} scrollWheelZoom={true} style={{ height: '70vh', width: '100%' }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        {origin && origin.value && (
          <Marker position={[origin.value.lat, origin.value.lng]} icon={startIcon}>
            <Popup>
              Start of Trip
            </Popup>
          </Marker>
        )}
        {destination && destination.value && (
          <Marker position={[destination.value.lat, destination.value.lng]} icon={endIcon}>
            <Popup>
              End of Trip
            </Popup>
          </Marker>
        )}
        {/* TODO fix adding Intermediate markers */}
        {/* {routes.map((route, routeIndex) => (
          route.flights.map((nodeFlight, nodeIndex) => {
            console.log(markedPositions);
            if (nodeIndex > 0 && !isPositionMarked(nodeFlight.origin.value.lat, nodeFlight.origin.value.lng)) {
              console.log("Adding new orange marker")
              addMarkedPosition(nodeFlight.origin.value.lat, nodeFlight.origin.value.lng);
              return (
                // <Marker key={`node-${routeIndex}-${flightIndex}-${nodeIndex}`} position={[nodeFlight.origin.value.lat, nodeFlight.origin.value.lng]} icon={endMarkerImg}>
                //   <Popup>{`Intermediate Origin of Flight ${nodeIndex + 1}`}</Popup>
                // </Marker>
                <Marker key={`node-${routeIndex}-${nodeIndex}`} position={[nodeFlight.destination.value.lat, nodeFlight.destination.value.lng]} icon={startIcon}>
                  <Popup>
                      Intermediate Step
                  </Popup>
                </Marker>
              );
            }
          })
        ))} */}
        {routes.map((route, routeIndex) => (
          route.flights.map((flight, flightIndex) => {
            // Determine the correct origin and destination for each flight
            console.log(flight);
            console.log(`${routeIndex}-${flightIndex}`);

            // const flightOrigin = flightIndex === 0 ? [origin.value.lat, origin.value.lng] : [route.flights[flightIndex - 1].destination.value.lat, route.flights[flightIndex - 1].destination.value.lng];
            // const flightDestination = [flight.value.lat, flight.value.lng];
            let flightOrigin = [flight.origin.value.lat, flight.origin.value.lng];
            let flightDestination = [flight.destination.value.lat, flight.destination.value.lng];

            const flightKey = `flight-${routeIndex}-${flightIndex}`;

            return (
              // <PolylineWithArrows
              //   key={`${routeIndex}-${flightIndex}`}
              //   positions={[flightOrigin, flightDestination]}
              //   color={routeIndex % 2 ? "blue" : "red"}
              //   eventHandlers={{
              //     click: () => {
              //       setActiveRoute(`route-${routeIndex}-flight-${flightIndex}`);
              //       scrollToFlightDetail(`route-${routeIndex}-flight-${flightIndex}`);
              //     }
              //   }}
              // >
              //   <Popup>
              //     {`Flight from ${flight.origin.label} to ${flight.destination.label}`}
              //     <br />
              //     {`Departure: ${flight.departure}, Arrival: ${flight.arrival}`}
              //   </Popup>
              // </PolylineWithArrows>
              
              <React.Fragment key={flightKey}>  

                <Polyline
                  key={`${routeIndex}-${flightIndex}`}
                  positions={[flightOrigin, flightDestination]}
                  color={routeIndex % 2 ? "blue" : "red"}
                  weight={5}
                  dashArray="10, 20" // Larger gaps than dashes, can adjust for more noticeable direction
                  dashOffset="0"
                  eventHandlers={{
                    click: () => {
                      setActiveRoute(`route-${routeIndex}-flight-${flightIndex}`);
                      scrollToFlightDetail(`route-${routeIndex}-flight-${flightIndex}`);
                    }
                  }}
                >
                  
                  <Popup>
                    {`Flight from ${flight.origin.label} to ${flight.destination.label}`}
                    <br />
                    {`Departure: ${flight.departure}, Arrival: ${flight.arrival}`}
                  </Popup>
                </Polyline>

            </React.Fragment>

            );
          })
        ))}
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


    </div>
  );
}

export default App;
