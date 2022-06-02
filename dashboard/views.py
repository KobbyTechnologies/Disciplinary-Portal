from django.shortcuts import render, redirect
import requests
from requests import Session
from requests_ntlm import HttpNtlmAuth
import json
from django.conf import settings as config
import datetime
from datetime import date
import base64
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# Create your views here.


def dashboard(request):
    session = requests.Session()
    session.auth = config.AUTHS
    Access_Point = config.O_DATA.format("/QyEthicsDisciplinaryCases")
    todays_date = date.today()
    year = todays_date.year

    try:
        responses = session.get(Access_Point, timeout=10).json()
        cases = []
        closedCases = []
        loggedCases = []
        rejectCases = []
        lawOpen = []
        lawClosed = []
        Code = ""
        Name = ""
        Email = ""
        expertName = ""
        expertNo = ""
        expertEmail = ""
        for case in responses['value']:
            if request.session['types'] == 'Expert':
                try:
                    if case['Stage'] == 'Specialist' and case['Status'] == 'Specialist Acceptance' and case['Specialist_No_'] == request.session['expertNo']:
                        output_json = json.dumps(case)
                        cases.append(json.loads(output_json))
                    if case['Stage'] == 'Specialist' and case['Status'] == 'Logged' and case['Specialist_No_'] == request.session['expertNo']:
                        output_json = json.dumps(case)
                        loggedCases.append(json.loads(output_json))
                    if case['Status'] == "Disciplinary Admin Intermediate" and case['Specialist_No_'] == request.session['expertNo']:
                        output_json = json.dumps(case)
                        closedCases.append(json.loads(output_json))
                    if case['Status'] == "Specialist Rejected" and case['Specialist_No_'] == request.session['expertNo']:
                        output_json = json.dumps(case)
                        rejectCases.append(json.loads(output_json))
                    # Expert Details
                    expertName =request.session['expertName'] 
                    expertNo = request.session['expertNo']
                    expertEmail = request.session['expertEmail']
                except:
                    print("Not working")
            if request.session['types'] == 'Law Firm':      
                try:
                    if case['Law_Firm_Submitted']==False and case['Law_Firm_Accepted']==True and case['Appealed'] == True and case['Appeal_Resolved'] == False and case['Law_Firm_Code'] == request.session['LawFirmNo']:
                        output_json = json.dumps(case)
                        lawOpen.append(json.loads(output_json))
                    if case['Law_Firm_Submitted']==True and case['Status'] == 'Disciplinary Admin Intermediate' and case['Law_Firm_Code'] == request.session['LawFirmNo']:
                        output_json = json.dumps(case)
                        lawClosed.append(json.loads(output_json))
                    # Law firm Details
                    Code = request.session['LawFirmNo']
                    Name =request.session['Name'] 
                    Email =  request.session['Email']
                except:
                    print("Not working")
        count = len(cases)
        counterLogged = len(loggedCases)
        counterClosed = len(closedCases)
        counterReject = len(rejectCases)
        OpenLaw = len(lawOpen)
        closedLaw = len(lawClosed)
    except requests.exceptions.ConnectionError as e:
        print(e)
    types = request.session['types']  

    todays_date = datetime.datetime.now().strftime("%b. %d, %Y %A")
    ctx = {"today": todays_date, "year": year,
           "count": count, "counterLogged": counterLogged,
           "case": cases, "logged": loggedCases, "types": types,
           "counterClosed": counterClosed, 'closed': closedCases,
           'counterReject': counterReject, 'reject': rejectCases,
           "countLaw": OpenLaw, 'law': lawOpen, "closedLawCounter": closedLaw,
           "lawC": lawClosed,
           "Code":Code,"Name":Name,"Email":Email,
           "expertName":expertName,"expertNo":expertNo,"expertEmail":expertEmail}
    return render(request, 'main/dashboard.html', ctx)


def FnExpertCaseAcceptance(request):
    interactCode = ''
    expertNo = request.session['expertNo']
    myResponse = ''
    comments = ''
    if request.method == 'POST':
        try:
            interactCode = request.POST.get('interactCode')
            myResponse = request.POST.get('myResponse')
            comments = request.POST.get('comments')
        except ValueError:
            messages.error(request, "Not sent. Invalid Input, Try Again!!")
            return redirect('dashboard')
        if not comments:
            comments = ''
        try:
            response = config.CLIENT.service.FnExpertCaseAcceptance(
                interactCode, expertNo, myResponse, comments)
            messages.success(request, "Successfully")
            print(response)
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('dashboard')


def caseDetails(request, pk):
    todays_dates = datetime.datetime.now().strftime("%b. %d, %Y %A")
    todays_date = date.today()
    year = todays_date.year
    session = requests.Session()
    session.auth = config.AUTHS
    Access_Point = config.O_DATA.format("/QyEthicsDisciplinaryCases")
    Access_Files = config.O_DATA.format("/QyDocumentAttachments")
    res = ''
    state = ''
    myFiles = []
    try:
        responses = session.get(Access_Point, timeout=10).json()
        resFiles = session.get(Access_Files, timeout=10).json()
        for case in responses['value']:
            if case['Interact_Code'] == pk and case['Status'] == 'Logged' and case['Specialist_No_'] == request.session['expertNo']:
                res = case
                state = 1
            if case['Interact_Code'] == pk and case['Status'] == "Disciplinary Admin Intermediate" and case['Appealed'] == False and case['Specialist_No_'] == request.session['expertNo']:
                res = case
                state = 2
            if case['Interact_Code'] == pk and case['Status'] == "Specialist Rejected" and case['Appealed'] == False and case['Specialist_No_'] == request.session['expertNo']:
                res = case
                state = 2
            if case['Interact_Code'] == pk and case['Status'] == "Specialist Rejected" and case['Appealed'] == False and case['Specialist_No_'] == request.session['expertNo']:
                res = case
                state = 2
            if case['Interact_Code'] == pk and case['Status'] == 'Specialist Acceptance' and case['Appealed'] == False and case['Specialist_No_'] == request.session['expertNo']:
                res = case
                state = 2
            # Law Firm
            if case['Interact_Code'] == pk and case['Appealed'] == True and case['Law_Firm_Code'] == request.session['LawFirmNo']:
                res = case
                state = 1
            if case['Interact_Code'] == pk and case['Appeal_Resolved'] == True and case['Law_Firm_Code'] == request.session['LawFirmNo']:
                res = case
                state = 2
        for files in resFiles['value']:
            if files['No_'] == pk and files['Table_ID'] == 52177806:
                output_json = json.dumps(files)
                myFiles.append(json.loads(output_json))
    except requests.exceptions.ConnectionError as e:
        print(e)
    print(state)
    # Expert Details
    expertName =request.session['expertName'] 
    expertNo = request.session['expertNo']
    expertEmail = request.session['expertEmail']
    types = request.session['types']
    ctx = {"today": todays_dates, "year": year,
           "res": res, "file": myFiles, "state": state, "types": types,
           "expertName":expertName,"expertNo":expertNo,"expertEmail":expertEmail}
    return render(request, 'open.html', ctx)


def FnExpertSaveComments(request, pk):
    interactCode = pk
    expertNo = request.session['expertNo']
    comments = ''
    if request.method == 'POST':
        try:
            comments = request.POST.get('comments')
        except ValueError:
            return redirect('caseDetails', pk=pk)
        try:
            response = config.CLIENT.service.FnExpertSaveComments(
                interactCode, expertNo, comments)
            messages.success(request, "Successfully Sent")
            print(response)
            return redirect('caseDetails', pk=pk)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('caseDetails', pk=pk)


def FnUploadAttachedDocument(request, pk):
    docNo = pk
    response = ""
    fileName = ""
    attachment = ""
    tableID = 52177806

    if request.method == "POST":
        try:
            attach = request.FILES.getlist('attachment')
        except Exception as e:
            return redirect('caseDetails', pk=pk)
        for files in attach:
            fileName = request.FILES['attachment'].name
            attachment = base64.b64encode(files.read())
            try:
                response = config.CLIENT.service.FnUploadAttachedDocument(
                    docNo, fileName, attachment, tableID)
                print(response)
            except Exception as e:
                messages.error(request, e)
                print(e)
        if response == True:
            messages.success(request, "Successfully Sent !!")
            return redirect('caseDetails', pk=pk)
        else:
            messages.error(request, "Not Sent !!")
            return redirect('caseDetails', pk=pk)

    return redirect('caseDetails', pk=pk)


def FnExpertSubmitCase(request, pk):
    interactCode = pk
    expertNo = request.session['expertNo']
    if request.method == "POST":
        try:
            response = config.CLIENT.service.FnExpertSubmitCase(
                interactCode, expertNo)
            print(response)
        except Exception as e:
            messages.error(request, e)
            print(e)
        if response == True:
            messages.success(request, "Submitted Successfully")
            return redirect('caseDetails', pk=pk)
        else:
            messages.error(request, "Not Sent")
            return redirect('caseDetails', pk=pk)
    return redirect('caseDetails', pk=pk)


# Law Firm


def lawDetails(request, pk):
    todays_dates = datetime.datetime.now().strftime("%b. %d, %Y %A")
    todays_date = date.today()
    year = todays_date.year
    session = requests.Session()
    session.auth = config.AUTHS
    Access_Point = config.O_DATA.format("/QyEthicsDisciplinaryCases")
    Access_Files = config.O_DATA.format("/QyDocumentAttachments")
    res = ''
    state = ''
    myFiles = []
    try:
        responses = session.get(Access_Point, timeout=10).json()
        resFiles = session.get(Access_Files, timeout=10).json()
        for case in responses['value']:
            # Law Firm
            if case['Interact_Code'] == pk and  case['Law_Firm_Submitted']==False and case['Law_Firm_Accepted']==True and case['Appealed'] == True and case['Appeal_Resolved'] == False and case['Law_Firm_Code'] == request.session['LawFirmNo']:
                res = case
                state = 1
            if case['Interact_Code'] == pk and case['Law_Firm_Submitted']==True and case['Status'] == 'Disciplinary Admin Intermediate' and case['Law_Firm_Code'] == request.session['LawFirmNo']:
                res = case
                state = 2
        for files in resFiles['value']:
            if files['No_'] == pk and files['Table_ID'] == 52177806:
                output_json = json.dumps(files)
                myFiles.append(json.loads(output_json))
    except requests.exceptions.ConnectionError as e:
        print(e)
    print(state)
    # Law firm Details
    Code = request.session['LawFirmNo']
    Name =request.session['Name'] 
    Email =  request.session['Email']
    types = request.session['types']
    ctx = {"today": todays_dates, "year": year,
           "res": res, "file": myFiles, "state": state, "types": types,
           "Code":Code,"Name":Name,"Email":Email,}
    return render(request, 'law.html', ctx)


def FnLawFirmSaveComments(request, pk):
    interactCode = pk
    lawFirmCode = request.session['LawFirmNo']
    comments = ''
    if request.method == 'POST':
        try:
            comments = request.POST.get('comments')
        except ValueError:
            return redirect('lawDetails', pk=pk)
        try:
            response = config.CLIENT.service.FnLawFirmSaveComments(
                interactCode, lawFirmCode, comments)
            messages.success(request, "Successfully Sent")
            print(response)
            return redirect('lawDetails', pk=pk)
        except Exception as e:
            messages.error(request, e)
            print(e)
    return redirect('lawDetails', pk=pk)


def FnLawFirmSubmitCase(request, pk):
    interactCode = pk
    lawFirmCode = request.session['LawFirmNo']
    response = ''
    if request.method == "POST":
        try:
            response = config.CLIENT.service.FnLawFirmSubmitCase(
                interactCode, lawFirmCode)
            print(response)
        except Exception as e:
            messages.error(request, e)
            print(e)
        if response == True:
            messages.success(request, "Submitted Successfully")
            return redirect('lawDetails', pk=pk)
        else:
            messages.error(request, "Not Sent")
            return redirect('lawDetails', pk=pk)
    return redirect('lawDetails', pk=pk)
