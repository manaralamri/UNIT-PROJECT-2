from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from products.models import Product
from .models import Contact
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib import messages

# Create your views here.
def home_view(request:HttpRequest):
  products = Product.objects.all()[0:4]
  return render(request, "main/index.html", {'products':products})


def contact_view(request:HttpRequest):
    
    if request.method == "POST":
        contact = Contact(name=request.POST["name"], email=request.POST["email"], message=request.POST["message"])
        contact.save()

        #send confirmation email
        content_html = render_to_string("main/mail/confirmation.html")
        send_to = contact.email
        email_message = EmailMessage("confiramation", content_html, settings.EMAIL_HOST_USER, [send_to])
        email_message.content_subtype = "html"
        #email_message.connection = email_message.get_connection(True)
        email_message.send()

        messages.success(request, "Your message is received. Thank You.", "alert-success")

    return render(request, 'main/contact.html' )

