import base64
import threading
from django.http import response
from django.shortcuts import redirect, render, HttpResponse
from django.conf import settings as config
import json
import requests
from requests import Session
from requests_ntlm import HttpNtlmAuth
import datetime
from datetime import date
from django.contrib import messages
from cryptography.fernet import Fernet
import string
import secrets
import enum
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
import threading
# Create your views here.


class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


def send_reset_email(email, resetCode, request):
    current_site = get_current_site(request)
    email_subject = 'Activate your account'
    email_body = render_to_string('activate.html', {
        'domain': current_site,
        'Secret': resetCode,
    })

    email = EmailMessage(subject=email_subject, body=email_body,
                         from_email=config.EMAIL_HOST_USER,
                         to=[email]
                         )

    EmailThread(email).start()


class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


def send_email(email, resetCode, request):
    current_site = get_current_site(request)
    email_subject = 'Activate your account'
    email_body = render_to_string('lawActivate.html', {
        'domain': current_site,
        'Secret': resetCode,
    })

    email = EmailMessage(subject=email_subject, body=email_body,
                         from_email=config.EMAIL_HOST_USER,
                         to=[email]
                         )

    EmailThread(email).start()


def login_request(request):
    todays_date = date.today()
    year = todays_date.year

    ctx = {"year": year}
    return render(request, 'login.html', ctx)


def lawLogin(request):
    todays_date = date.today()
    year = todays_date.year
    session = requests.Session()
    session.auth = config.AUTHS

    Access_Point = config.O_DATA.format("/QyLawFirms")
    username = ''
    Portal_Password = ""
    if request.method == 'POST':

        try:
            email = request.POST.get('email').strip()
            password = request.POST.get('password')
        except ValueError:
            messages.error(request, "Invalid credentials, try again")
            return redirect('lawLogin')
        try:
            response = session.get(Access_Point, timeout=10).json()
            for applicant in response['value']:
                if applicant['Email'] == email:
                    try:
                        Portal_Password = base64.urlsafe_b64decode(
                            applicant['Portal_Password'])
                        request.session['LawFirmNo'] = applicant['Code']
                        request.session['types'] = 'Advocate'
                    except Exception as e:
                        messages.error(request, e)
                        return redirect('lawLogin')
        except requests.exceptions.ConnectionError as e:
            print(e)

        cipher_suite = Fernet(config.ENCRYPT_KEY)
        try:
            decoded_text = cipher_suite.decrypt(
                Portal_Password).decode("ascii")
        except Exception as e:
            messages.error(request, e)
            return redirect('lawLogin')
        if decoded_text == password:
            return redirect('dashboard')
        else:
            messages.error(
                request, "Invalid Credentials")
            return redirect('lawLogin')
    return render(request, "lawLogin.html")


def FnLawFirmResetPassword(request):
    alphabet = string.ascii_letters + string.digits
    SecretCode = ''.join(secrets.choice(alphabet) for i in range(5))
    session = requests.Session()
    session.auth = config.AUTHS

    email = ""
    resetCode = SecretCode
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
        except ValueError:
            print("Invalid credentials, try again")
            return redirect('lawLogin')
        try:
            response = config.CLIENT.service.FnLawFirmResetPassword(
                email, resetCode)
            print(response)
            if response == True:
                send_email(email, resetCode, request)
                messages.success(
                    request, 'We sent you an email to verify your account')
                request.session['law_email'] = email
                return redirect('lawLogin')
        except requests.exceptions.ConnectionError as e:
            messages.error(
                request, e)
            print(e)
    return redirect('lawLogin')


# Change Law firm Password
def FnLawFirmChangePassword(request):
    session = requests.Session()
    session.auth = config.AUTHS

    email = request.session['law_email']
    resetCode = ""
    password = ""
    if request.method == 'POST':
        try:
            resetCode = request.POST.get('resetCode')
            password = request.POST.get('password')
            confirm_password = request.POST.get('password2')
        except ValueError:
            print("Invalid credentials, try again")
            return redirect('FnLawFirmChangePassword')
        if len(password) < 6:
            messages.error(request, "Password should be at least 6 characters")
            return redirect('FnLawFirmChangePassword')
        if password != confirm_password:
            messages.error(request, "Password mismatch")
            return redirect('FnLawFirmChangePassword')
        cipher_suite = Fernet(config.ENCRYPT_KEY)
        try:
            encrypted_text = cipher_suite.encrypt(password.encode('ascii'))
            password = base64.urlsafe_b64encode(encrypted_text).decode("ascii")
            response = config.CLIENT.service.FnLawFirmChangePassword(
                email, resetCode, password)
            print(response)
            if response == True:
                messages.success(
                    request, 'Account Activated Successfully.Login to Continue.')
                return redirect('lawLogin')
        except requests.exceptions.ConnectionError as e:
            messages.error(
                request, e)
            print(e)
            return redirect('FnLawFirmChangePassword')
    return render(request, 'lawReset.html')


# Function to reset expert password


def FnExpertResetPassword(request):
    alphabet = string.ascii_letters + string.digits
    SecretCode = ''.join(secrets.choice(alphabet) for i in range(5))
    session = requests.Session()
    session.auth = config.AUTHS

    email = ""
    resetCode = SecretCode
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
        except ValueError:
            print("Invalid credentials, try again")
            return redirect('login')
        try:
            response = config.CLIENT.service.FnExpertResetPassword(
                email, resetCode)
            print(response)
            if response == True:
                send_reset_email(email, resetCode, request)
                messages.success(
                    request, 'We sent you an email to verify your account')
                request.session['activation_email'] = email
                return redirect('login')
        except requests.exceptions.ConnectionError as e:
            messages.error(
                request, e)
            print(e)
    return redirect('login')
# function to change Expert Password


def FnExpertChangePassword(request):
    session = requests.Session()
    session.auth = config.AUTHS

    email = request.session['activation_email']
    print(email)
    resetCode = ""
    password = ""
    if request.method == 'POST':
        try:
            resetCode = request.POST.get('resetCode')
            password = request.POST.get('password')
            confirm_password = request.POST.get('password2')
        except ValueError:
            print("Invalid credentials, try again")
            return redirect('reset')
        if len(password) < 6:
            messages.error(request, "Password should be at least 6 characters")
            return redirect('reset')
        if password != confirm_password:
            messages.error(request, "Password mismatch")
            return redirect('reset')
        cipher_suite = Fernet(config.ENCRYPT_KEY)
        try:
            encrypted_text = cipher_suite.encrypt(password.encode('ascii'))
            password = base64.urlsafe_b64encode(encrypted_text).decode("ascii")
            response = config.CLIENT.service.FnExpertChangePassword(
                email, resetCode, password)
            print(response)
            if response == True:
                messages.success(
                    request, 'Account Activated Successfully.Login to Continue.')
                return redirect('login')
        except requests.exceptions.ConnectionError as e:
            messages.error(
                request, e)
            print(e)
            return redirect('reset')
    return render(request, "reset.html")

# Function to login expert


def expertLogin(request):
    todays_date = date.today()
    year = todays_date.year
    session = requests.Session()
    session.auth = config.AUTHS

    Access_Point = config.O_DATA.format("/QyExperts")
    username = ''
    Portal_Password = ""
    if request.method == 'POST':

        try:
            email = request.POST.get('email').strip()
            password = request.POST.get('password')
        except ValueError:
            messages.error(request, "Invalid credentials, try again")
            return redirect('login')
        try:
            response = session.get(Access_Point, timeout=10).json()
            for applicant in response['value']:
                if applicant['Email'] == email:
                    try:
                        Portal_Password = base64.urlsafe_b64decode(
                            applicant['Portal_Password'])
                        request.session['expertNo'] = applicant['No_']
                        print(request.session['expertNo'])
                        request.session['types'] = 'Specialist'
                    except Exception as e:
                        messages.error(request, e)
                        return redirect('login')
        except requests.exceptions.ConnectionError as e:
            print(e)

        cipher_suite = Fernet(config.ENCRYPT_KEY)
        try:
            decoded_text = cipher_suite.decrypt(
                Portal_Password).decode("ascii")
        except Exception as e:
            messages.error(request, e)
            return redirect('login')
        if decoded_text == password:
            return redirect('dashboard')
        else:
            messages.error(
                request, "Invalid Credentials")
            return redirect('login')
    return redirect('login')
