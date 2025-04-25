from django.shortcuts import render,redirect
from ecommerceapp.models import Contact,Product,Orders,OrderUpdate
from django.contrib import messages
from math import ceil
from ecommerceapp import keys
from django.conf import settings
MERCHANT_KEY=keys.MK
import json
from django.views.decorators.csrf import  csrf_exempt
import stripe
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import time
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from datetime import datetime

# Initialize Stripe with secret key
stripe.api_key = keys.STRIPE_SECRET_KEY

# Create your views here.
def index(request):

    allProds = []
    catprods = Product.objects.values('category','id')
    print(catprods)
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod= Product.objects.filter(category=cat)
        n=len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])

    params= {'allProds':allProds}

    return render(request,"index.html",params)

def contact(request):
    if request.method=="POST":
        name=request.POST.get("name")
        email=request.POST.get("email")
        desc=request.POST.get("desc")
        pnumber=request.POST.get("pnumber")
        myquery=Contact(name=name,email=email,desc=desc,phonenumber=pnumber)
        myquery.save()
        messages.info(request,"we will get back to you soon..")
        return render(request,"contact.html")


    return render(request,"contact.html")

def checkout(request):
    if not request.user.is_authenticated:
        messages.warning(request,"Login & Try Again")
        return redirect('/auth/login')

    if request.method=="POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amt')
        email = request.POST.get('email', '')
        address1 = request.POST.get('address1', '')
        address2 = request.POST.get('address2','')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        Order = Orders(items_json=items_json,name=name,amount=amount, email=email, address1=address1,address2=address2,city=city,state=state,zip_code=zip_code,phone=phone)
        print(amount)
        Order.save()
        update = OrderUpdate(order_id=Order.order_id,update_desc="the order has been placed")
        update.save()
        thank = True
        
        # Redirect to Stripe payment page
        return redirect(f'/stripe_payment/{Order.order_id}/')

    return render(request, 'checkout.html')

def profile(request):
    if not request.user.is_authenticated:
        messages.warning(request, "Login & Try Again")
        return redirect('/auth/login')

    # Get current user orders
    user_orders = Orders.objects.filter(email=request.user.email)

    context = {
        'orders': user_orders
    }

    return render(request, "profile.html", context)

# Function to send order confirmation email
def send_order_confirmation(order):
    try:
        print(f"Starting send_order_confirmation for order #{order.order_id}")
        
        # Check if order data exists
        print(f"Order details: Name={order.name}, Email={order.email}, Items JSON={order.items_json}")
        
        subject = f'Order Confirmation - Order #{order.order_id}'
        
        # Parse items JSON safely
        try:
            if order.items_json and order.items_json.strip():
                items = json.loads(order.items_json)
                print(f"Successfully parsed items_json: {items}")
                # Format of items_json is typically {"productID": [quantity, name, price]}
            else:
                items = {}
                print("Warning: Order has empty items_json")
        except json.JSONDecodeError as e:
            items = {}
            print(f"Warning: Could not parse items_json: {e}")
            print(f"Raw items_json: {order.items_json}")
        
        # Create HTML context for email template
        context = {
            'order': order,
            'items': items,
            'name': order.name,
            'transaction_id': order.oid if order.oid else 'N/A',
            'amount': order.amount,
            'date': datetime.now().strftime("%B %d, %Y at %I:%M %p"),
            'address': f"{order.address1}, {order.address2 if order.address2 else ''}, {order.city}, {order.state} - {order.zip_code}"
        }
        
        print("Rendering email template...")
        # Render email templates
        try:
            html_message = render_to_string('email_order_confirmation.html', context)
            plain_message = strip_tags(html_message)
            print("Email template rendered successfully")
        except Exception as template_error:
            print(f"Template rendering error: {template_error}")
            return False
        
        # Send email
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [order.email]
        
        print(f"Sending email from {from_email} to {recipient_list}")
        print(f"Email backend: {settings.EMAIL_BACKEND}")
        
        if hasattr(settings, 'EMAIL_FILE_PATH'):
            print(f"Email file path: {settings.EMAIL_FILE_PATH}")
        
        try:
            # Set up alternative SSL context to fix certification issues
            import ssl
            import smtplib
            from django.core.mail.backends.smtp import EmailBackend
            
            # Use a custom email backend with modified SSL context
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            # Create a connection directly
            connection = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
            connection.ehlo()
            connection.starttls(context=context)
            connection.ehlo()
            connection.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            
            # Create email message
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = from_email
            message["To"] = recipient_list[0]
            
            # Attach plain and HTML versions
            message.attach(MIMEText(plain_message, "plain"))
            message.attach(MIMEText(html_message, "html"))
            
            # Send email
            print("Sending email with direct SMTP connection...")
            connection.sendmail(from_email, recipient_list, message.as_string())
            connection.quit()
            
            print("Email sent successfully!")
            return True
            
        except Exception as e:
            print(f"Email sending failed with error: {str(e)}")
            print(f"Email settings: HOST={settings.EMAIL_HOST}, PORT={settings.EMAIL_PORT}, TLS={settings.EMAIL_USE_TLS}")
            
            # Fallback to Django's send_mail
            print("Trying Django's send_mail as fallback...")
            try:
                result = send_mail(
                    subject, 
                    plain_message, 
                    from_email, 
                    recipient_list, 
                    html_message=html_message,
                    fail_silently=False
                )
                print(f"Email sending result: {result}")
                return True
            except Exception as django_error:
                print(f"Django send_mail also failed: {str(django_error)}")
                return False
            
    except Exception as outer_error:
        print(f"Unexpected error in send_order_confirmation: {str(outer_error)}")
        import traceback
        traceback.print_exc()
        return False

# Function to send order notification email to admin/shop owner
def send_admin_order_notification(order):
    try:
        print(f"Sending admin notification for order #{order.order_id}")
        
        subject = f'New Order Notification - Order #{order.order_id}'
        
        # Parse items JSON safely
        try:
            if order.items_json and order.items_json.strip():
                items = json.loads(order.items_json)
                print(f"Successfully parsed items_json for admin notification")
            else:
                items = {}
                print("Warning: Order has empty items_json")
        except json.JSONDecodeError as e:
            items = {}
            print(f"Warning: Could not parse items_json: {e}")
        
        # Create HTML context for admin email template
        context = {
            'order': order,
            'items': items,
            'name': order.name,
            'transaction_id': order.oid if order.oid else 'N/A',
            'amount': order.amount,
            'date': datetime.now().strftime("%B %d, %Y at %I:%M %p"),
            'address': f"{order.address1}, {order.address2 if order.address2 else ''}, {order.city}, {order.state} - {order.zip_code}",
            'phone': order.phone,
            'customer_email': order.email
        }
        
        # Render admin email templates
        html_message = render_to_string('email_admin_notification.html', context)
        plain_message = strip_tags(html_message)
        
        # Send email to admin/shop owner
        admin_email = settings.EMAIL_HOST_USER  # Shop owner's email
        
        # Use a different from_email to make it clear it's a notification
        from_email = f"Shop Notification <{settings.EMAIL_HOST_USER}>"
        
        print(f"Sending admin notification from {from_email} to {admin_email}")
        
        try:
            # Call the send email function directly to ensure message delivery
            import ssl
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            # Create a connection directly
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            connection = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
            connection.ehlo()
            connection.starttls(context=context)
            connection.ehlo()
            connection.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            
            # Create email message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = from_email
            message["To"] = admin_email
            
            # Attach plain and HTML versions
            message.attach(MIMEText(plain_message, "plain"))
            message.attach(MIMEText(html_message, "html"))
            
            # Send email - use bcc for the shop owner email to ensure receipt
            connection.sendmail(
                from_email,
                [admin_email],  # TO recipients
                message.as_string()
            )
            connection.quit()
            
            print("Admin notification email sent successfully!")
            return True
            
        except Exception as e:
            print(f"Admin notification email failed: {str(e)}")
            
            # Fallback to Django's send_mail
            try:
                result = send_mail(
                    subject, 
                    plain_message, 
                    from_email, 
                    [admin_email], 
                    html_message=html_message,
                    fail_silently=False
                )
                print(f"Admin notification email sending result: {result}")
                return result > 0
            except Exception as django_error:
                print(f"Django send_mail also failed: {str(django_error)}")
                return False
            
    except Exception as outer_error:
        print(f"Unexpected error in send_admin_order_notification: {str(outer_error)}")
        import traceback
        traceback.print_exc()
        return False

# Stripe Payment Views
def stripe_payment(request, order_id):
    """
    View for processing payment via Stripe
    """
    if not request.user.is_authenticated:
        messages.warning(request, "Login & Try Again")
        return redirect('/auth/login')
    
    try:
        # Get order details
        order = Orders.objects.get(order_id=order_id)
        
        # Ensure order belongs to the logged-in user
        if order.email != request.user.email:
            messages.warning(request, "Access Denied")
            return redirect('/')
        
        # Create context with order details
        context = {
            'order_id': order_id,
            'amount': order.amount,
            'STRIPE_PUBLISHABLE_KEY': keys.STRIPE_PUBLISHABLE_KEY
        }
        
        return render(request, "stripe_payment.html", context)
    except Orders.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('/')

@require_POST
@csrf_exempt
def process_stripe_payment(request):
    data = json.loads(request.body)
    payment_method_id = data.get('payment_method_id')
    order_id = data.get('order_id')
    amount = data.get('amount')
    
    try:
        # Get the order
        order = Orders.objects.get(order_id=order_id)
        
        # Convert amount to cents (Stripe requires amount in smallest currency unit)
        amount_in_cents = int(float(order.amount) * 100)
        
        # Create payment intent with Stripe
        intent = stripe.PaymentIntent.create(
            amount=amount_in_cents,
            currency='inr',
            payment_method=payment_method_id,
            confirm=True,
            return_url='http://127.0.0.1:8000/payment_success/' + str(order_id) + '/',
        )
        
        # Update order status
        order.oid = intent.id
        order.amountpaid = order.amount
        order.paymentstatus = "PAID"
        order.save()
        
        # Create order update
        update = OrderUpdate(order_id=order.order_id, update_desc="Payment received, order confirmed")
        update.save()
        
        print("Order successfully processed. Starting email notifications...")
        
        # Send order confirmation email to the customer
        customer_email_result = send_order_confirmation(order)
        print(f"Customer email notification result: {customer_email_result}")
        
        # Send order notification email to the admin/shop owner
        admin_email_result = send_admin_order_notification(order)
        print(f"Admin email notification result: {admin_email_result}")
        
        if not customer_email_result or not admin_email_result:
            print("WARNING: One or both email notifications failed. Order was still processed successfully.")
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        print(f"Error processing payment: {str(e)}")
        return JsonResponse({'error': str(e)})

def payment_success(request, order_id):
    if not request.user.is_authenticated:
        messages.warning(request, "Login & Try Again")
        return redirect('/auth/login')
        
    try:
        # Get the order
        order = Orders.objects.get(order_id=order_id)
        
        # Ensure order belongs to the logged-in user
        if order.email != request.user.email:
            messages.warning(request, "Access Denied")
            return redirect('/')
            
        context = {
            'order_id': order_id,
            'amount': order.amount,
            'transaction_id': order.oid,
            'email': order.email
        }
        
        return render(request, 'payment_success.html', context)
        
    except Orders.DoesNotExist:
        messages.error(request, "Order not found")
        return redirect('/')



