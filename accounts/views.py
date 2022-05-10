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
# Create your views here.


def login_request(request):
    todays_date = date.today()
    year = todays_date.year
    session = requests.Session()
    session.auth = config.AUTHS

    Access_Point = config.O_DATA.format("/QyApplicants")
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
                if applicant['E_Mail'] == email:
                    try:
                        Portal_Password = base64.urlsafe_b64decode(
                            applicant['Portal_Password'])
                        if email == 'emaeba@kobbys.co.ke':
                            request.session['types'] = 'Specialist'
                        if email == 'emaeba@kobby.co.ke':
                            request.session['types'] = 'Advocate'
                        request.session['No_'] = applicant['No_']
                        request.session['E_Mail'] = applicant['E_Mail']
                        applicant_no = request.session['No_']
                        mail = request.session['E_Mail']
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
    ctx = {"year": year, "username": username}
    return render(request, 'login.html', ctx)


# def register_request(request):
#     todays_date = date.today()
#     year = todays_date.year
#     email = ''
#     password = ''
#     confirm_password = ''

#     if request.method == 'POST':
#         try:
#             email = request.POST.get('email').strip()
#             my_password = str(request.POST.get('password'))
#             confirm_password = str(
#                 request.POST.get('confirm_password')).strip()
#         except ValueError:
#             messages.error(request, "Invalid credentials, try again")
#             return redirect('register')
#         if len(my_password) < 6:
#             messages.error(request, "Password should be at least 6 characters")
#             return redirect('register')
#         if my_password != confirm_password:
#             messages.error(request, "Password mismatch")
#             return redirect('register')
#         cipher_suite = Fernet(config.ENCRYPT_KEY)

#         encrypted_text = cipher_suite.encrypt(my_password.encode('ascii'))
#         password = base64.urlsafe_b64encode(encrypted_text).decode("ascii")

#         try:
#             response = config.CLIENT.service.FnApplicantRegister(
#                 email, password)
#             messages.success(
#                 request, "Account successfully created, you can now login")
#             print(response)
#             return redirect('login')
#         except Exception as e:
#             messages.error(request, e)
#             print(e)
#     ctx = {"year": year}
#     return render(request, "register.html", ctx)


def lawLogin(request):
    return render(request, "lawLogin.html")


def FnLawFirmChangePassword(request):
    alphabet = string.ascii_letters + string.digits
    SecretCode = ''.join(secrets.choice(alphabet) for i in range(5))
    session = requests.Session()
    session.auth = config.AUTHS

    email = ""
    resetCode = SecretCode
    password = ''
    confirm_password = ''
    Access_Point = config.O_DATA.format("/QyLawFirms")
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirm_password = request.POST.get('password2')
        except ValueError:
            print("Invalid credentials, try again")
            return redirect('lawLogin')
        if len(password) < 6:
            messages.error(request, "Password should be at least 6 characters")
            return redirect('lawLogin')
        if password != confirm_password:
            messages.error(request, "Password mismatch")
            return redirect('lawLogin')
        try:
            response = session.get(Access_Point, timeout=10).json()
            for applicant in response['value']:
                if applicant['Email'] == email:
                    cipher_suite = Fernet(config.ENCRYPT_KEY)
                    try:
                        encrypted_text = cipher_suite.encrypt(
                            password.encode('ascii'))
                        password = base64.urlsafe_b64encode(
                            encrypted_text).decode("ascii")
                        response = config.CLIENT.service.FnLawFirmChangePassword(
                            email, resetCode, password)
                        print(response)
                        messages.success(
                            request, "Reset was successful, now login")
                        return redirect('lawLogin')
                    except Exception as e:
                        messages.error(request, e)
                        return redirect('lawLogin')
        except requests.exceptions.ConnectionError as e:
            messages.error(
                request, e)
            print(e)
    return redirect('lawLogin')


def FnExpertChangePassword(request):
    alphabet = string.ascii_letters + string.digits
    SecretCode = ''.join(secrets.choice(alphabet) for i in range(5))
    session = requests.Session()
    session.auth = config.AUTHS

    email = ""
    resetCode = SecretCode
    password = ''
    confirm_password = ''
    Access_Point = config.O_DATA.format("/QyExperts")
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirm_password = request.POST.get('password2')
        except ValueError:
            print("Invalid credentials, try again")
            return redirect('login')
        if len(password) < 6:
            messages.error(request, "Password should be at least 6 characters")
            return redirect('login')
        if password != confirm_password:
            messages.error(request, "Password mismatch")
            return redirect('login')
        try:
            response = session.get(Access_Point, timeout=10).json()
            for applicant in response['value']:
                if applicant['Email'] == email:
                    cipher_suite = Fernet(config.ENCRYPT_KEY)
                    try:
                        encrypted_text = cipher_suite.encrypt(
                            password.encode('ascii'))
                        password = base64.urlsafe_b64encode(
                            encrypted_text).decode("ascii")
                        response = config.CLIENT.service.FnExpertChangePassword(
                            email, resetCode, password)
                        print(response)
                        messages.success(
                            request, "Reset was successful, now login")
                        return redirect('login')
                    except Exception as e:
                        messages.error(request, e)
                        return redirect('login')
        except requests.exceptions.ConnectionError as e:
            messages.error(
                request, e)
            print(e)
    return redirect('login')
