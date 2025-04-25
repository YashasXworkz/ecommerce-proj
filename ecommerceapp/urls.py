from django.urls import path
from ecommerceapp import views

urlpatterns = [
    path('',views.index,name="index"),
    path('contact',views.contact,name="contact"),
    path('checkout/', views.checkout, name="Checkout"),
    path('profile/', views.profile, name='Profile'),
    # Stripe payment routes
    path('stripe_payment/<int:order_id>/', views.stripe_payment, name='StripePayment'),
    path('process_stripe_payment/', views.process_stripe_payment, name='ProcessStripePayment'),
    path('payment_success/<int:order_id>/', views.payment_success, name='PaymentSuccess'),
]