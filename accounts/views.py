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
import re
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
                        if email == 'emaeba@kobby.co.ke':
                            request.session['types'] = 'Specialist'
                        if email == 'emaeba@kobbsy.co.ke':
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


def register_request(request):
    todays_date = date.today()
    year = todays_date.year
    email = ''
    password = ''
    confirm_password = ''

    if request.method == 'POST':
        try:
            email = request.POST.get('email').strip()
            my_password = str(request.POST.get('password'))
            confirm_password = str(
                request.POST.get('confirm_password')).strip()
        except ValueError:
            messages.error(request, "Invalid credentials, try again")
            return redirect('register')
        if len(my_password) < 6:
            messages.error(request, "Password should be at least 6 characters")
            return redirect('register')
        if my_password != confirm_password:
            messages.error(request, "Password mismatch")
            return redirect('register')
        cipher_suite = Fernet(config.ENCRYPT_KEY)

        encrypted_text = cipher_suite.encrypt(my_password.encode('ascii'))
        password = base64.urlsafe_b64encode(encrypted_text).decode("ascii")

        try:
            response = config.CLIENT.service.FnApplicantRegister(
                email, password)
            messages.success(
                request, "Account successfully created, you can now login")
            print(response)
            return redirect('login')
        except Exception as e:
            messages.error(request, e)
            print(e)
    ctx = {"year": year}
    return render(request, "register.html", ctx)
