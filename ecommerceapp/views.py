from django.shortcuts import render,redirect
from ecommerceapp.models import Contact,Product,Orders,OrderUpdate
from django.contrib import messages
from math import ceil
from ecommerceapp import keys
from django.conf import settings
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
        subject = f'Order Confirmation - Order #{order.order_id}'
        
        # Parse items JSON safely
        try:
            if order.items_json and order.items_json.strip():
                items = json.loads(order.items_json)
                # Format of items_json is typically {"productID": [quantity, name, price]}
            else:
                items = {}
        except json.JSONDecodeError as e:
            items = {}
        
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
        
        # Render email templates
        try:
            html_message = render_to_string('email_order_confirmation.html', context)
            plain_message = strip_tags(html_message)
        except Exception as template_error:
            return False
        
        # Send email
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [order.email]
        
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
            connection.sendmail(from_email, recipient_list, message.as_string())
            connection.quit()
            
            return True
            
        except Exception as e:
            # Fallback to Django's send_mail
            try:
                result = send_mail(
                    subject, 
                    plain_message, 
                    from_email, 
                    recipient_list, 
                    html_message=html_message,
                    fail_silently=False
                )
                return result > 0
            except Exception as django_error:
                return False
    except Exception as outer_error:
        import traceback
        traceback.print_exc()
        return False

# Function to send order notification email to admin/shop owner
def send_admin_order_notification(order):
    try:
        subject = f'New Order #{order.order_id} Received'
        
        # Parse items JSON safely
        try:
            if order.items_json and order.items_json.strip():
                items = json.loads(order.items_json)
            else:
                items = {}
        except json.JSONDecodeError as e:
            items = {}
        
        # Create HTML context for email template
        context = {
            'order': order,
            'items': items,
            'name': order.name,
            'email': order.email,
            'phone': order.phone,
            'transaction_id': order.oid if order.oid else 'N/A',
            'amount': order.amount,
            'date': datetime.now().strftime("%B %d, %Y at %I:%M %p"),
            'address': f"{order.address1}, {order.address2 if order.address2 else ''}, {order.city}, {order.state} - {order.zip_code}"
        }
        
        # Render email templates
        try:
            html_message = render_to_string('email_admin_notification.html', context)
            plain_message = strip_tags(html_message)
        except Exception as template_error:
            return False
        
        # Send email
        from_email = settings.EMAIL_HOST_USER
        admin_email = settings.ADMIN_EMAIL if hasattr(settings, 'ADMIN_EMAIL') else settings.EMAIL_HOST_USER
        
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
            message["To"] = admin_email
            
            # Attach plain and HTML versions
            message.attach(MIMEText(plain_message, "plain"))
            message.attach(MIMEText(html_message, "html"))
            
            # Send email
            connection.sendmail(from_email, [admin_email], message.as_string())
            connection.quit()
            
            return True
            
        except Exception as e:
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
                return result > 0
            except Exception as django_error:
                return False
    except Exception as outer_error:
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
    try:
        # Get data from request
        data = json.loads(request.body)
        payment_method_id = data.get('payment_method_id')
        order_id = data.get('order_id')
        
        # Get the order
        order = Orders.objects.get(order_id=order_id)
        amount_cents = int(float(order.amount) * 100)  # Convert to cents
        
        # Create payment intent
        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency='usd',
            payment_method=payment_method_id,
            confirm=True,
            return_url=request.build_absolute_uri(f'/payment_success/{order_id}/'),
        )
        
        # Update order with payment ID
        order.oid = intent.id
        order.amountpaid = order.amount
        order.paymentstatus = 'PAID'
        order.save()
        
        # Create an order update
        update = OrderUpdate(order_id=order.order_id, update_desc="Your order has been placed successfully")
        update.save()
        
        # Send order confirmation emails
        customer_email_result = send_order_confirmation(order)
        admin_email_result = send_admin_order_notification(order)
        
        if not (customer_email_result and admin_email_result):
            # One or both emails failed, but payment was still successful
            pass
        
        return JsonResponse({'success': True, 'redirect_url': f'/payment_success/{order_id}/'})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

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



