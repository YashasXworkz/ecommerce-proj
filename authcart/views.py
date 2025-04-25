from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth.models import User
from django.views.generic import View
from django.contrib import messages
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from .utils import TokenGenerator,generate_token
from django.utils.encoding import force_bytes,force_str,DjangoUnicodeDecodeError
from django.core.mail import EmailMessage
from django.conf import settings


from django.contrib.auth import authenticate,login,logout
# Create your views here.
def signup(request):
    if request.method=="POST":
        email=request.POST['email']
        password=request.POST['pass1']
        confirm_password=request.POST['pass2']
        if password!=confirm_password:
            messages.warning(request,"Password is Not Matching")
            return render(request,'signup.html')                   
        try:
            if User.objects.get(username=email):
                # return HttpResponse("email already exist")
                messages.info(request,"Email is Taken")
                return render(request,'signup.html')
        except Exception as identifier:
            pass
        user = User.objects.create_user(email,email,password)
        user.is_active=False
        user.save()
        
        # Generate activation link
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = generate_token.make_token(user)
        activation_link = f"http://127.0.0.1:8000/auth/activate/{uid}/{token}"
        
        print(f"Debug - Activation Link: {activation_link}")
        print(f"Debug - User Email: {email}")
        
        # Don't add a message here, as it will show up both in activation page and after activation
        # messages.success(request, "Account created successfully! Use the activation link below.")
        
        # Pass the activation link directly to the template
        context = {
            'activation_link': activation_link,
            'user_email': email
        }
        
        return render(request, "activation_email_sent.html", context)
    return render(request,"signup.html")


class ActivateAccountView(View):
    def get(self,request,uidb64,token):
        try:
            uid=force_str(urlsafe_base64_decode(uidb64))
            user=User.objects.get(pk=uid)
        except Exception as identifier:
            user=None
        if user is not None and generate_token.check_token(user,token):
            user.is_active=True
            user.save()
            
            # Clear any existing messages first
            storage = messages.get_messages(request)
            for _ in storage:
                # Iterating through clears the messages
                pass
            
            # Then add our success message
            messages.success(request, "Account Activated Successfully")
            return redirect('/auth/login')
        return render(request,'activatefail.html')

def handlelogin(request):
    if request.method == "POST":
        # Get the email and password from the request
        email = request.POST['email']
        userpassword = request.POST['pass1']

        # Authenticate user based on the email
        try:
            from django.contrib.auth.models import User
            user_obj = User.objects.get(email=email)  # Get the user object using email
            username = user_obj.username  # Extract the username corresponding to the email
            myuser = authenticate(username=username, password=userpassword)  # Authenticate user

            if myuser is not None:
                login(request, myuser)
                messages.success(request, "Login successful")
                return redirect('/')
            else:
                messages.error(request, "Invalid Credentials")
                return redirect('/auth/login')
        except User.DoesNotExist:
            messages.error(request, "No user found with this email")
            return redirect('/auth/login')

    return render(request, "login.html")

def handlelogout(request):
    logout(request)
    messages.info(request,'Logout Success')
    return redirect('/auth/login')
    
# Debug route to test the activation_email_sent.html template
def test_activation_template(request):
    test_email = "test@example.com"
    test_link = "http://127.0.0.1:8000/auth/activate/test-uid/test-token"
    return render(request, "activation_email_sent.html", 
                 {'activation_link': test_link, 'user_email': test_email})
    