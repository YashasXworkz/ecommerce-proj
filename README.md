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

1. Clone the repository or download and extract the zip file to your preferred location.

2. Open a terminal or PowerShell and navigate to the project folder:
   ```
   # For Windows PowerShell users
   PS C:\Users\username\Downloads> cd E-commerce
   PS C:\Users\username\Downloads\E-commerce>
   ```

3. Navigate to the Django project directory:
   ```
   # Navigate to the inner ecommerce directory where manage.py is located
   PS C:\Users\username\Downloads\E-commerce> cd ecommerce
   PS C:\Users\username\Downloads\E-commerce\ecommerce>
   ```

4. Create a virtual environment in the inner ecommerce folder:
   ```
   # Make sure you're in the inner ecommerce directory
   PS C:\Users\username\Downloads\E-commerce\ecommerce> python -m venv .venv
   ```

5. Activate the virtual environment:
   ```
   # For Windows PowerShell
   PS C:\Users\username\Downloads\E-commerce\ecommerce> .venv\Scripts\activate
   
   # Your prompt should change to show (.venv) like this:
   (.venv) PS C:\Users\username\Downloads\E-commerce\ecommerce>
   
   # For macOS/Linux (bash/zsh)
   $ source .venv/bin/activate
   ```
   
   > **Note**: All subsequent commands should be run with the virtual environment activated. You'll know it's activated when you see (.venv) at the beginning of your command prompt.

6. Install dependencies:
   ```
   # Make sure you're in the inner ecommerce directory with the virtual environment activated
   (.venv) PS C:\Users\username\Downloads\E-commerce\ecommerce> pip install -r requirements.txt
   ```

7. Run database migrations:
   ```
   # Make sure the virtual environment is activated
   (.venv) PS C:\Users\username\Downloads\E-commerce\ecommerce> python manage.py makemigrations
   (.venv) PS C:\Users\username\Downloads\E-commerce\ecommerce> python manage.py migrate
   ```

8. Create a superuser:
   ```
   (.venv) PS C:\Users\username\Downloads\E-commerce\ecommerce> python manage.py createsuperuser
   ```

9. Run the development server:
   ```
   (.venv) PS C:\Users\username\Downloads\E-commerce\ecommerce> python manage.py runserver
   ```

10. Visit `http://127.0.0.1:8000/` in your browser
11. Admin panel is available at `http://127.0.0.1:8000/admin/`

## Troubleshooting

### Common Issues

1. **Directory Structure**:
   - `E-commerce` is the outer folder (parent directory)
   - `ecommerce` is the inner folder that contains:
     - `manage.py`
     - `.venv` virtual environment
     - All Django apps and project files
   - **All commands** should be run inside the inner `ecommerce` directory

2. **Database Migrations**: If you encounter database-related errors, ensure all migrations are applied:
   ```
   # Make sure you're in the inner 'ecommerce' directory with manage.py
   # And your virtual environment is activated (.venv)
   (.venv) PS C:\Users\username\Downloads\E-commerce\ecommerce> python manage.py makemigrations
   (.venv) PS C:\Users\username\Downloads\E-commerce\ecommerce> python manage.py migrate
   ```

3. **Static Files**: If static files aren't loading properly:
   ```
   # Make sure you're in the inner 'ecommerce' directory with manage.py
   # And your virtual environment is activated (.venv)
   (.venv) PS C:\Users\username\Downloads\E-commerce\ecommerce> python manage.py collectstatic
   ```

4. **Email Configuration**: The account activation system requires working email settings. If testing locally, you can:
   - Use Django's console email backend by setting `EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'` in settings.py
   - Check the console for activation links instead of actual emails

5. **Stripe Integration**: Make sure your Stripe API keys are correctly set in the environment variables

6. **Getting 404 Errors**: Ensure you're running the server from the correct directory (the inner 'ecommerce' folder that contains manage.py)

7. **Command Not Found**: If you get "command not found" errors, check that:
   - You've activated the virtual environment (you should see (.venv) in your prompt)
   - You're in the right directory (inside the inner 'ecommerce' folder with manage.py)

8. **PowerShell Execution Policy**: If you encounter permission errors running scripts in PowerShell:
   ```
   # Run PowerShell as Administrator and execute:
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

## Directory Structure

For clarity, here's the actual project structure:

```
E-commerce/                # Outer folder
│
├── templates/             # Some template files
│
└── ecommerce/             # Inner folder - RUN ALL COMMANDS HERE
    ├── .venv/             # Virtual environment (inside inner folder)
    ├── authcart/          # Authentication app
    ├── ecommerceapp/      # Main application
    ├── ecommerce/         # Project settings
    ├── static/            # Static files
    ├── templates/         # Template files
    ├── media/             # User uploaded content
    ├── requirements.txt   # Project dependencies
    └── manage.py          # Django management script - ALL COMMANDS USE THIS
```

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