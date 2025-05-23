const express = require('express');
const cors = require('cors');
const airports = require('airport-codes');

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());

// Sample airport data (in a real app, you'd use a proper database)
const sampleAirports = [
  { iata: 'DEL', name: 'Indira Gandhi International Airport', city: 'New Delhi', state: 'Delhi', country: 'India' },
  { iata: 'BOM', name: 'Chhatrapati Shivaji Maharaj International Airport', city: 'Mumbai', state: 'Maharashtra', country: 'India' },
  { iata: 'MAA', name: 'Chennai International Airport', city: 'Chennai', state: 'Tamil Nadu', country: 'India' },
  { iata: 'BLR', name: 'Kempegowda International Airport', city: 'Bengaluru', state: 'Karnataka', country: 'India' },
  { iata: 'HYD', name: 'Rajiv Gandhi International Airport', city: 'Hyderabad', state: 'Telangana', country: 'India' },
  { iata: 'CCU', name: 'Netaji Subhas Chandra Bose International Airport', city: 'Kolkata', state: 'West Bengal', country: 'India' },
  { iata: 'GOI', name: 'Dabolim Airport', city: 'Vasco da Gama', state: 'Goa', country: 'India' },
  { iata: 'COK', name: 'Cochin International Airport', city: 'Kochi', state: 'Kerala', country: 'India' },
  { iata: 'PNQ', name: 'Pune Airport', city: 'Pune', state: 'Maharashtra', country: 'India' },
  { iata: 'JAI', name: 'Jaipur International Airport', city: 'Jaipur', state: 'Rajasthan', country: 'India' },
];

// API endpoint to search airports
app.get('/api/airports', (req, res) => {
  try {
    const query = (req.query.q || '').toLowerCase();
    
    if (!query) {
      return res.json({ airports: [] });
    }

    // Filter airports based on query (iata, city, or name)
    const filteredAirports = sampleAirports.filter(airport => 
      airport.iata.toLowerCase().includes(query) ||
      airport.city.toLowerCase().includes(query) ||
      airport.name.toLowerCase().includes(query)
    );

    res.json({ airports: filteredAirports });
  } catch (error) {
    console.error('Error searching airports:', error);
    res.status(500).json({ error: 'Failed to search airports' });
  }
});

// Start the server
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
