from inventory.models import Contact_us,Stock
from django.shortcuts import render,redirect,HttpResponse
from django.conf import settings
from django.core.mail import send_mail

def CONTACT_US(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        contact = Contact_us(
            name=name,
            email=email,
            subject=subject,
            message=message,
        )

        # Define the email subject, message, and sender
        email_subject = subject
        email_message = f"From: {name} <{email}>\n\nMessage:\n{message}"
        email_from = settings.EMAIL_HOST_USER

        try:
            # Send the email
            send_mail(
                subject=email_subject,
                message=email_message,
                from_email=email_from,
                recipient_list=['Hammodehyaser79@gmail.com'],  
                fail_silently=False,
            )
            contact.save()  # Save to the database if email was sent successfully
            return redirect('e_commerce:home')
        
        except Exception as e:
            print(f"Error sending email: {e}")  # For debugging
            return redirect('e_commerce:contact')
    return render(request,'main/contact.html')


def SEARCH(request):
    query = request.GET.get('query')
    product = Stock.objects.filter(name__icontains=query)
    context = {
        'product': product
    }
    return render(request, 'main/search.html', context)