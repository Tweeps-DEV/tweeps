# Tweeps

Tweeps is a comprehensive food ordering platform with features for managing orders, customizing food items, and handling employee management. Built with NextJS for the frontend and Flask for the backend, it provides a seamless experience for users and administrators alike.

## Features

- **User Authentication**: Sign up and log in to manage orders.
- **Order Management**: Place orders with customizable toppings.
- **Order Tracking**: Track your order in real-time with a map view.
- **Admin Dashboard**: Manage employees and monitor orders from a dedicated admin panel.
- **Payment Integration**: Secure payment processing for orders.

## Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Usage](#usage)
4. [License](#license)

## Installation

### Prerequisites

- Python 3.x
- Node.js (v16 or later)
- Docker (optional, for containerized deployment)

### Backend Setup

1. **Navigate to the `backend` directory**:
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   - Create a `.env` file in the `backend` directory with necessary configuration (e.g., database URL, secret keys).

5. **Run the Flask application**:
   ```bash
   flask run
   ```

### Frontend Setup

1. **Navigate to the `frontend` directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Set up environment variables**:
   - Create a `.env` file in the `frontend` directory with necessary configuration (e.g., API URL).

4. **Start the React development server**:
   ```bash
   npm start
   ```

### Docker Setup (Optional)

To run the application using Docker:

1. **Build and start containers**:
   ```bash
   docker-compose up --build
   ```

## Configuration

### Backend Configuration

- Update the `.env` file in the `backend` directory to include:
  - `DATABASE_URL`: URL for the database connection.
  - `SECRET_KEY`: A secret key for Flask.
  - Other environment-specific configurations.

## Usage

### User Flow

1. **Sign Up/Log In**: Create a new account or log in to an existing one.
2. **Place Order**: Select items and customize with optional toppings.
3. **Track Order**: Use the track button to view your order on a map.
4. **Payment**: Complete the payment process securely.

### Admin Flow

1. **Access Admin Panel**: Navigate to `admin.tweeps.yourdomain.com` to access the admin dashboard.
2. **Manage Employees**: Add, update, or remove employees.
3. **Monitor Orders**: View and manage all incoming orders.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
