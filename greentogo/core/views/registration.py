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
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.create_stripe_customer()
            user.email = form.cleaned_data.get('email')
            current_site = get_current_site(request)
            mail_subject = 'Welcome to GreenToGo!'
            communityBoxesCheckedIn = int((LocationTag.objects.all()).count()/2) + 100
            print(communityBoxesCheckedIn)
            welcome_message = render_to_string('registration/welcome_message.html', {
                'user': user,
                'communityBoxesCheckedIn': communityBoxesCheckedIn,
                'domain': current_site.domain,
            })
            print(welcome_message)
            user.save()
            to_email = form.cleaned_data.get('email')
            print(to_email)
            email = EmailMessage(
                        subject=mail_subject, body=welcome_message, from_email='greentogo@app.durhamgreentogo.com', to=[to_email],
            )
            print(email)
            email.send()
            # send_mail(
            #     mail_subject,
            #     welcome_message,
            #     'greentogo@app.durhamgreentogo.com',
            #     [to_email],
            #     fail_silently=False,
            # )
            new_user = authenticate(username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password1'],
                                    )
            login(request, new_user)
            messages.add_message(request, messages.INFO, "Your account has been registered successfully, {username}! Now you just need a subscription in order to start using GreenToGo. Your email address is {email}. If this is incorrect, change your email in 'My Settings'".format(username=form.cleaned_data['username'], email=form.cleaned_data['email']))
            return redirect('/subscriptions/new/', {'newly_registered_user':{
                'new':True,
                'username':form.cleaned_data['username'],
                'email':form.cleaned_data['email']
            }})
            # return render(request, 'core/add_subscription.html', {'newly_registered_user':{
            #     'new':True,
            #     'username':form.cleaned_data['username'],
            #     'email':form.cleaned_data['email']
            # }})
    else:
        form = UserSignupForm()
    return render(request, "registration/registration_form.html", {'form':form})
