import requests
from pprint import pprint
import datetime
import smtplib
import ssl
import time
from email.message import Message

data = {
    'state_id': '',
    'district_id': '',
    'date': '12-05-2021',
}

param = {
    'district_id': '378',
    'date': '11-05-2021',
    # 'vaccine': 'COVISHIELD'
}

head = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
}


def test():
    centers = requests.get('https://cdn-api.co-vin.in/api/v2/appointment/sessions/calendarByDistrict', params={'district_id': '278',
                                                                                                               'date': datetime.date.today().strftime("%d-%m-%Y")}, headers=head).json()['centers']
    for center in centers:
        for session in center['sessions']:
            print("sd")
            # if session['available_capacity'] != 0:
            #    available = True


def mail(email):
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "chingchongmadafakka@gmail.com"  # Enter your address
    receiver_email = email  # Enter receiver address
    password = "chingchongmf"

    m = Message()
    m['From'] = 'Ching'
    m['To'] = email
    m['X-Priority'] = '1'
    m['Subject'] = 'URGENT!'
    m.set_payload('VACCINE AVAILABLE BOOK SOON')

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, m.as_string())


def init_city(email):
    state_resp = requests.get(
        'https://api.demo.co-vin.in/api/v2/admin/location/states', headers=head)
    states = state_resp.json()['states']
    for state in states:
        print(state['state_id'], state['state_name'])

    state_id = input("\nSelect state: ")
    data['state_id'] = state_id

    city_resp = requests.get(
        'https://api.demo.co-vin.in/api/v2/admin/location/districts/'+state_id, headers=head)
    cities = city_resp.json()['districts']
    for city in cities:
        print(city['district_id'], city['district_name'])

    district_id = input("\nSelect city: ")
    data['district_id'] = district_id

    print("\nSeeking Slots. Will Notify as soon as the slots are available\n")

    while True:
        available = False

        try:
            centers_resp = requests.get('https://cdn-api.co-vin.in/api/v2/appointment/sessions/calendarByDistrict', params={'district_id': district_id,
                                                                                                                            'date': datetime.date.today().strftime("%d-%m-%Y")}, headers=head)
            print(centers_resp)
            centers = centers_resp.json()['centers']
            for center in centers:
                for session in center['sessions']:
                    # print("sd")
                    if session['available_capacity'] != 0:
                        available = True

            if available == True:
                print("Vaccine Slot Available. Book Fast")
                mail(email)


        except Exception as ex:
            print(ex.with_traceback)

        time.sleep(3)



def init_pin(email):
    pin = input("Enter PIN Code: ")

    print("\nSeeking Slots. Will Notify as soon as the slots are available\n")

    while True:
        available = False

        try:
            centers_resp = requests.get('https://cdn-api.co-vin.in/api/v2/appointment/sessions/calendarByPin', params={'pincode': pin,
                                                                                                                            'date': datetime.date.today().strftime("%d-%m-%Y")}, headers=head)
            print(centers_resp)
            centers = centers_resp.json()['centers']
            for center in centers:
                for session in center['sessions']:
                    # print("sd")
                    if session['available_capacity'] != 0:
                        available = True

            if available == True:
                print("Vaccine Slot Available. Book Fast")
                mail(email)


        except Exception as ex:
            print(ex.with_traceback)

        time.sleep(3)


if __name__ == "__main__":
    # test()
    email = input("Enter your email: ")

    print("1 -> Search By PIN")
    print("2 -> Search By City")
    switch = input("Enter : ")

    if switch == '1':
        init_pin(email)
    elif switch == '2':
        init_city(email)
    else:
        print("Enter a valid value")
