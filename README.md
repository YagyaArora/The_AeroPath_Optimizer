# Flight Route Optimizer

An interactive web application that helps users find the optimal flight routes based on their preferences (cost or time) with user authentication and booking capabilities.

## Features

- User authentication (login/signup)
- Interactive map with airport markers
- Route optimization based on cost or time
- Real-time route visualization
- Animated airplane markers
- Flight booking system
- User profile management
- Clean and intuitive UI

## Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 14+
- MySQL Server 8.0+

### Backend Setup

1. Clone the repository and navigate to the project directory

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Set up the database:
   - Create a new MySQL database named `flight_booking`
   - Update the `.env` file with your database credentials

5. Initialize the database schema:
```bash
python update_database.py
```

6. Run the backend server:
```bash
python app.py
```

The backend will be available at `http://localhost:5000`

### Frontend Setup

1. Navigate to the project directory in a new terminal

2. Install Node.js dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The frontend will be available at `http://localhost:3000`

## Usage

1. Select your source and destination airports from the dropdown menus
2. Choose your preference (cost or time)
3. Click "Find Route" to optimize and visualize the route
4. The optimal route will be displayed on the map with animated airplane markers

## Technologies Used

- **Frontend:**
  - React.js
  - React Router
  - React Context API
  - Leaflet.js
  - Bootstrap 5

- **Backend:**
  - Python with Flask
  - Flask-CORS
  - PyJWT for authentication
  - bcrypt for password hashing
  - MySQL Connector

- **Route Optimization:**
  - NetworkX
  - Geopy

- **Map Integration:**
  - Leaflet Routing Machine
  - OpenStreetMap

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```
# MySQL Configuration
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DB=flight_booking

# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development

# JWT Configuration
SECRET_KEY=your-secret-key-here-change-this-in-production
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user's profile

### Flights
- `GET /api/flights` - Get available flights
- `POST /api/flights/book` - Book a flight
- `GET /api/flights/bookings` - Get user's bookings

### Airports
- `GET /api/airports` - Get list of airports
- `GET /api/airports/search?q={query}` - Search airports

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
- UI Components: Custom styling with CSS
