from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.template.defaultfilters import pluralize
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site

from core.models import Location, Subscription, LocationTag, User
from core.forms import UserSignupForm

def registration_form(request):
    if request.method == 'POST':
        print('It Was A Post')
        form = UserSignupForm(request.POST)
        if form.is_valid():
            print("form is valid")
            user = form.save(commit=False)
            user.is_active = True
            user.email = form.cleaned_data.get('email')
            current_site = get_current_site(request)
            mail_subject = 'Welcome to GreenToGo!'
            message = render_to_string('registration/welcome_message.html', {
                'user': user,
                'domain': current_site.domain,
            })
            print(message)
            print(user.email)
            print(user)
            print("stopping")
            # print(breakHere)
            user.save()
            print("still going")
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                        mail_subject, message, to=[to_email]
            )
            email.send()
            new_user = authenticate(username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password1'],
                                    )
            login(request, new_user)
            return render(request, 'core/add_subscription.html', {'newly_registered_user':{
                'new':True,
                'username':form.cleaned_data['username'],
                'email':form.cleaned_data['email']
            }})
    else:
        form = UserSignupForm()
    return render(request, "registration/registration_form.html", {'form':form})


def registration_complete(request):
    print("Heyo")
    print(request)
    activation_key = "123"
    # user = request.user
    # if not user.stripe_id:
    #     user.create_stripe_customer()
    # if request.method == "POST":
    #     location_code = request.POST.get('location_code').upper()
    #     try:
    #         location = Location.objects.get(code=location_code)
    #         return redirect(location.get_absolute_url())
    #     except Location.DoesNotExist:
    #         if location_code:
    #             messages.error(request, "There is no location that matches that code.")
    #         else:
    #             messages.error(request, "Please enter a code.")

    return render(request, "registration/registration_complete.html", {
        "activation_key": activation_key,
    })