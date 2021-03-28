import pyrebase
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from django.conf import settings
from django.contrib import auth
from cv2 import cv2
import numpy as np
from pyzbar.pyzbar import decode
from user.aadhaar import AadhaarSecureQr
import requests
import urllib.parse
import math
import smtplib
import calendar
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders
import os
import datetime


config = {
    "apiKey": "AIzaSyAJFs-5kd1E6wwe8B3q-zbKIt6nEYVA-2Y",
    'authDomain': "tech-knights-d8093.firebaseapp.com",
    'databaseURL': "https://tech-knights-d8093-default-rtdb.firebaseio.com",
    'projectId': "tech-knights-d8093",
    'storageBucket': "tech-knights-d8093.appspot.com",
    'messagingSenderId': "1091367485814",
    "appId": "1:1091367485814:web:ade4ee3b02b49914ac3a57",
    'measurementId': "G-396WEKR0DZ"
}

firebase = pyrebase.initialize_app(config)
authe = firebase.auth()
database = firebase.database()
storage = firebase.storage()


def homepage(request):
    return render(request, "as.html")


def steps(request):
    return render(request, "steps.html")


def aadharveri(request):
    if request.method == "POST":
        file = request.FILES['file']

        i = file.name.rindex(".")
        exten = file.name[i:]
        newname = "x" + exten
        file_save = default_storage.save(newname, file)

        try:
            img = cv2.imread('/home/vismith24/ASF/ASF/media/'+newname)
            for barcode in decode(img):
                x = barcode.data
            obj = AadhaarSecureQr(int(x.decode(encoding='UTF-8')))
            data = obj.decodeddata()
            name = data["name"]
            g = data["gender"]
            digit = data["adhaar_last_4_digit"]
            x = {"name": name, "g": g, "digi": digit}
            return render(request, "signup2.html", x)
        except:
            print("Not valid")
    return render(request, "signup1.html")


def info(request):
    if request.method == "POST":
        name = request.POST.get("name")
        print(name)
        email = request.POST.get("email")
        password = request.POST.get("password")
        phone = request.POST.get("prn")
        role = request.POST.get("role")
        birthdate = request.POST.get("birthday")
        apartment = request.POST.get("apartment")
        street = request.POST.get("street")
        area = request.POST.get("area")
        city = request.POST.get("city")
        pincode = request.POST.get("pincode")

        address = street + ", " + area + ", " + city + ", " + pincode
        url = 'https://nominatim.openstreetmap.org/search/' + \
            urllib.parse.quote(address) + '?format=json'
        response = requests.get(url).json()
        lat1 = float(response[0]["lat"])
        lon1 = float(response[0]["lon"])

        user = authe.create_user_with_email_and_password(email, password)
        uid = user['localId']
        request.session['member_id'] = uid

        data = {"Name": name,
                "Email": email,
                "PhoneNo": phone,
                "birthdate": birthdate,
                "apartment": apartment,
                "street": street,
                "area": area,
                "city": city,
                "pincode": pincode,
                "geo": [lat1, lon1]
                }
        database.child(role).child(uid).set(data)
        database.child("xyz").child(uid).set({"role": role})
        return redirect("home")
    return render(request, "signup2.html")


def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = firebase.auth().sign_in_with_email_and_password(email, password)
        uid = user['localId']
        request.session['member_id'] = uid
        return redirect("home")
    return render(request, "login.html")


def meet(request):
    if request.method == "POST":
        y = database.child("xyz").child(request.session['member_id']).get()
        for user in y.each():
            # print(user.val())
            request.session["role"] = user.val()
        # print(request.session["role"])

        if request.session["role"] == "USER":
            user = database.child("USER").child(
                request.session['member_id']).get().val()
            lst = list(user.items())
            name = lst[1][1]
            phoneNo = lst[2][1]
            mail = lst[0][1]
            geo = lst[7][1]
            print("geo1", geo)

            rad = 6000
            R = 6371e3

            maxLat = geo[0] + math.degrees(rad/R)
            minLat = geo[0] - math.degrees(rad/R)
            minLon = geo[1] - \
                math.degrees(math.asin(rad/R) / math.cos(math.radians(geo[0])))
            maxLon = geo[1] + \
                math.degrees(math.asin(rad/R) / math.cos(math.radians(geo[0])))

            x1 = math.radians(geo[0])
            z = []

            vols = database.child("VOLUNTEER").get()
            a = list(database.child("VOLUNTEER").shallow().get().val())
            print(a)
            b = 0
            for vol in vols.each():
                print(vol.val())
                geo2 = (vol.val())["geo"]
                if (maxLat >= geo2[0] >= minLat) and (maxLon >= geo2[1] >= minLon):
                    x2 = math.radians(geo2[0])
                    x = math.radians(geo2[1] - geo[1])
                    d = math.acos(math.sin(x1) * math.sin(x2) +
                                  math.cos(x1)*math.cos(x2) * math.cos(x)) * R
                    z.append([d, (vol.val())["Name"], (vol.val())
                              ["Email"], (vol.val())["PhoneNo"], a[b]])
                b += 1
        return render(request, "meet.html", {"z": z, "mail": mail})
    return redirect("home")


def home(request):
    return render(request, "home.html")


def aboutus(request):
    return render(request, "aboutus.html")


def vnear(request):
    print("xyz")
    y = database.child("xyz").child(request.session['member_id']).get()
    for user in y.each():
        request.session["role"] = user.val()
    print(request.session["role"])
    if request.session["role"] == "USER":
        user = database.child("USER").child(
            request.session['member_id']).get().val()
        lst = list(user.items())
        name = lst[1][1]
        phoneNo = lst[2][1]
        mail = lst[0][1]
        geo = lst[7][1]
        print("geo1", geo)
        rad = 12000
        R = 6371e3

        maxLat = geo[0] + math.degrees(rad/R)
        minLat = geo[0] - math.degrees(rad/R)
        minLon = geo[1] - \
            math.degrees(math.asin(rad/R) / math.cos(math.radians(geo[0])))
        maxLon = geo[1] + \
            math.degrees(math.asin(rad/R) / math.cos(math.radians(geo[0])))

        x1 = math.radians(geo[0])
        z = []
        vols = database.child("VOLUNTEER").get()
        for vol in vols.each():
            geo2 = (vol.val())["geo"]
            if (maxLat >= geo2[0] >= minLat) and (maxLon >= geo2[1] >= minLon):
                    # print(x[0]," x1",x[1], "x2", x[2])
                x2 = math.radians(geo2[0])  # * math.pi/180
                x = math.radians(geo2[1] - geo[1])  # * math.pi/180
                d = math.acos(math.sin(x1) * math.sin(x2) +
                              math.cos(x1)*math.cos(x2) * math.cos(x)) * R
                # print(d)
                z.append([d, (vol.val())["Name"], (vol.val())["PhoneNo"]])

        sorted(z, key=lambda x: x[0])
        print(z)
        return render(request, "listofvol.html", {"z": z})


def events(request):
    year = []
    time = []
    dates = []
    month = []
    contact = []
    name = []
    eml = "adappavinisha@gmail.com"  # eml from session

    data_in_database = database.child("Events").child("Data").get()
    for item in data_in_database.each():
        if item.val()['Email_Fro'] == eml or item.val()['Email_To'] == eml:
            year.append(item.val()['Year'])
            time.append(item.val()['Time'])
            dates.append(item.val()['Dates'])
            month.append(item.val()['Month'])
            contact.append(item.val()['Phone'])
            name.append(item.val()['Name'])

    combi = zip(year, time, dates, month, contact, name)
    print(year, time, dates, month, contact, name)
    return render(request, 'events.html', {'combi': combi, "length": [i for i in range(len(list(combi)))], "year": year, "time": time, "dates": dates, "month": month, "contact": contact, "name": name})


def schedule(request):
    COMMASPACE = ', '
    uid = request.POST.get('vol')
    a = database.child("VOLUNTEER").child(uid).get()
    vol = [x.val() for x in a.each()]
    name = vol[1]
    vmail = vol[0]
    contact_vol = vol[2]
    date = str(request.POST.get('Meetingtime'))
    phone = request.POST.get('phone')
    mail = request.POST.get("mail")
    print("date", date)
    year = date[0:4]
    month = date[5:7]
    dates = date[8:10]
    time = date[11:16]
    time1 = (int(date[11:13])) % 24
    time2 = (int(date[14:16])) % 24
    time = time1+time2
    print("time1", time1)
    print("time2", time2)
    print("time", time)
    month_text = calendar.month_abbr[int(month)]
    email_to = vmail
    email_fro = mail
    data = {
        "Name": name,
        "Year": year,
        "Month": month_text,
        "Dates": dates,
        "Time": time,
        "Phone": phone,
        "Email_To": email_to,
        "Email_Fro": email_fro
    }
    database.child("Events").child("Data").push(data)
    CRLF = "\r\n"
    login = "teamtechknights2021@gmail.com"
    password = "techknights"
    attendees = [email_fro, email_to]
    organizer = "ORGANIZER;CN=organiser:mailto:teamtechknights" + CRLF + " @gmail.com"
    fro = "Aapka Sahara Foundation"

    ddtstart = datetime.datetime.now()

    #dt = "2021-03-31T10:33"
    dt = date + ":00"

    dt = dt.replace('-', "")
    dt = dt.replace(':', "")
    dt = dt + "Z"
    # print(dt)

    dtstart = dt

    dtend2 = (int(dtstart[9:11]) + 2) % 24
    dtend3 = dtstart[0:9] + str(dtend2) + dtstart[11:]
    # print(dtend3)

    dtend = dtend3

    # print(dtend2)
    desc = "Companion/volunteer Contact info is :" + \
        str(contact_vol) + " and Sir/Madam Contact info is " + str(phone)
    contact = phone
    description = "Description: " + desc + CRLF

    dtstamp = datetime.datetime.now().strftime("%Y%m%dT%H%M%SZ")
    """dtstart = ddtstart.strftime("%Y%m%dT%H%M%SZ")
    dtend = dtend.strftime("%Y%m%dT%H%M%SZ")"""
    # print(dtend)

    desccription = description + CRLF
    attendee = ""
    Name = name
    for att in attendees:
        attendee += "ATTENDEE;CUTYPE=INDIVIDUAL;ROLE=REQ-    PARTICIPANT;PARTSTAT=ACCEPTED;RSVP=TRUE" + \
            CRLF + " ;CN=" + att + ";X-NUM-GUESTS=0:" + CRLF + " mailto:" + att + CRLF
    ical = "BEGIN:VCALENDAR" + CRLF + "PRODID:pyICSParser" + \
        CRLF + "VERSION:2.0" + CRLF + "CALSCALE:GREGORIAN" + CRLF
    ical += "METHOD:REQUEST" + CRLF + "BEGIN:VEVENT" + CRLF + "DTSTART:" + dtstart + \
        CRLF + "DTEND:" + dtend + CRLF + "DTSTAMP:" + dtstamp + CRLF + organizer + CRLF
    ical += "UID:FIXMEUID" + dtstamp + CRLF
    ical += attendee + "CREATED:" + dtstamp + CRLF + description + "LAST-MODIFIED:" + \
        dtstamp + CRLF + "LOCATION:" + CRLF + \
        "SEQUENCE:0" + CRLF + "STATUS:CONFIRMED" + CRLF
    ical += "SUMMARY:meeting with " + Name + CRLF + "TRANSP:OPAQUE" + \
        CRLF + "END:VEVENT" + CRLF + "END:VCALENDAR" + CRLF
    eml_body = "This is a meeting arranged for " + name + " and " + " Sir/Madam" + \
        " Companion/volunteer Contact info is : " + \
        str(contact_vol) + " and Sir/Madam Contact info is " + str(phone)
    eml_body_bin = "This is the email body in binary - two steps"
    msg = MIMEMultipart('mixed')
    msg['Reply-To'] = fro
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = "Aapka Sahara Foundation invite" + dtstart
    msg['From'] = fro
    msg['To'] = ",".join(attendees)

    part_email = MIMEText(eml_body, "html")
    part_cal = MIMEText(ical, 'calendar;method=REQUEST')
    msgAlternative = MIMEMultipart('alternative')
    msg.attach(msgAlternative)

    ical_atch = MIMEBase('application/ics', ' ;name="%s"' % ("invite.ics"))
    ical_atch.set_payload(ical)
    encoders.encode_base64(ical_atch)
    ical_atch.add_header('Content-Disposition',
                         'attachment; filename="%s"' % ("invite.ics"))

    eml_atch = MIMEText('', 'plain')
    eml_atch.add_header('Content-Transfer-Encoding', "")

    msgAlternative.attach(part_email)
    msgAlternative.attach(part_cal)

    mailServer = smtplib.SMTP('smtp.gmail.com', 587)
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(login, password)
    mailServer.sendmail(fro, attendees, msg.as_string())
    mailServer.close()

    return render(request, "home.html")
