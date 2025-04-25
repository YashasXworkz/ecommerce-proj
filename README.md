# Shop Cart E-commerce Platform

A modern e-commerce platform built with Django, featuring product listings, cart management, checkout process, and Stripe payment integration.

## Features

- Responsive product catalog
- Shopping cart with quantity management
- User authentication system
- Secure checkout process
- Stripe payment integration
- Email notifications for orders

## Setup Instructions

### Prerequisites

- Python 3.8+
- pip

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd E-commerce
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv .venv
   # On Windows
   .venv\Scripts\activate
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Environment Variables:
   - Copy the example environment file:
     ```
     cp .env.example .env
     ```
   - Edit the `.env` file with your actual configuration

5. Run database migrations:
   ```
   python manage.py migrate
   ```

6. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

7. Run the development server:
   ```
   python manage.py runserver
   ```

8. Visit `http://127.0.0.1:8000/` in your browser

## Environment Variables

The application uses environment variables for configuration. These are loaded from a `.env` file in the root directory. Here are the important variables:

- `SECRET_KEY`: Django secret key
- `DEBUG`: Set to 'True' for development, 'False' for production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`: Email configuration
- `STRIPE_PUBLISHABLE_KEY`, `STRIPE_SECRET_KEY`: Stripe API keys

## Production Deployment

For production deployment:

1. Set `DEBUG=False` in your `.env` file
2. Configure proper `ALLOWED_HOSTS`
3. Use a production-ready database like PostgreSQL
4. Configure a web server like Nginx with Gunicorn
5. Enable HTTPS

## License

This project is licensed under the MIT License - see the LICENSE file for details. 