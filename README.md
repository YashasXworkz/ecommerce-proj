# E-commerce Shop

An e-commerce shopping website built with Django and PostgreSQL.

## Features

- User authentication and registration
- Product catalog with categories
- Shopping cart functionality
- Secure checkout with Stripe integration
- Order history and management
- Admin dashboard
- Responsive design
- Email notifications

## Tech Stack

- **Backend**: Django 4.1
- **Database**: PostgreSQL
- **Frontend**: HTML, CSS, JavaScript
- **Payment Processing**: Stripe
- **File Storage**: Cloudinary
- **Deployment**: Render (or any other platform)

## Setup

### Prerequisites

- Python 3.9+
- PostgreSQL 12+
- pip

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/e-commerce.git
   cd e-commerce
   ```

2. Create and activate a virtual environment
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # Linux/Mac
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install required packages
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables
   ```bash
   cp .env.example .env
   # Edit .env file with your own settings
   ```

5. Initialize the database
   ```bash
   python manage.py migrate
   ```

6. Create an admin user
   ```bash
   python manage.py createsuperuser
   ```

7. Start the development server
   ```bash
   python manage.py runserver
   ```