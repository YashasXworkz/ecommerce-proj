import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get Stripe API keys from environment variables
STRIPE_PUBLISHABLE_KEY = os.getenv('STRIPE_PUBLISHABLE_KEY', 'pk_test_your_default_key')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', 'sk_test_your_default_key')
