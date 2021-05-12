import ssl
import time
import hashlib
import smtplib
import datetime
import requests

from pprint import pprint
from email.message import Message
import re
from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg
import PySimpleGUI as sg


data = {
    'state_id': '',
    'district_id': '',
    'pin': ''
}

cases = {
    '1': {'url': 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/calendarByDistrict', 'params': {'district_id': '',
                                                                                                        'date': datetime.date.today().strftime("%d-%m-%Y")}},
    '2': {'url': 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/calendarByPin', 'params': {'pincode': '',
                                                                                                   'date': datetime.date.today().strftime("%d-%m-%Y")}}
}

head = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
}


def test():
    string = 'jayesh'
    print(hashlib.sha256(string.encode()).hexdigest())


def get_city_code():
    state_resp = requests.get(
        'https://api.demo.co-vin.in/api/v2/admin/location/states', headers=head)
    states = state_resp.json()['states']

    for state in states:
        print(state['state_id'], state['state_name'])

    state_id = input("\nSelect state code: ")
    data['state_id'] = state_id

    city_resp = requests.get(
        'https://api.demo.co-vin.in/api/v2/admin/location/districts/'+state_id, headers=head)
    cities = city_resp.json()['districts']
    for city in cities:
        print(city['district_id'], city['district_name'])

    district_id = input("\nSelect city code: ")
    data['district_id'] = district_id
    cases['1']['params']['district_id'] = district_id

    return district_id


def login(mobile):
    mobiledata = {
        'mobile': mobile,
        'secret': "U2FsdGVkX18oMx2/93IvSXwHjB2227hFgh0uF09S/7bmvn5EJSIu5PsuQUKMSL+t6xMkqVANHqFfyF3+8Stq1A=="
    }

    try:
        txn_resp = requests.post(
            'https://cdn-api.co-vin.in/api/v2/auth/generateMobileOTP', json=mobiledata, headers=head)
        # print(resp)
        txn_id = txn_resp.json()['txnId']
        print("txn: ", txn_id)

        otp = input("\nEnter Otp : ")

        try:

            headerr = {
                'accept': 'application/json, text/plain',
                'content-type': 'application/json',
                'dnt': '1',
                'origin': 'https://selfregistration.cowin.gov.in',
                'referer': 'https://selfregistration.cowin.gov.in/',
                'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
            }

            login_resp = requests.post('https://cdn-api.co-vin.in/api/v2/auth/validateMobileOtp', json={
                                       'otp': hashlib.sha256(otp.encode()).hexdigest(), 'txnId': txn_id}, headers=headerr)
            print(login_resp)

            if login_resp.status_code == 200:
                print('\n\nLogin Successful !\n', login_resp.json())
                token = login_resp.json()['token']
                return token
            else:
                print("Error")
                exit()

        except Exception as e:
            print(e.with_traceback())
            print("Please Try Again")
            exit()

    except Exception as ex:
        print(ex)
        print("Please Try Again")
        exit()


def get_benif(token):
    headr = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
        'Authorization': 'Bearer '+token
    }

    try:
        benif_response = requests.get(
            'https://cdn-api.co-vin.in/api/v2/appointment/beneficiaries', headers=headr)

        if benif_response.status_code == 200:
            # print(benif_response.headers)
            # pprint(benif_response.json())
            print(benif_response)
            beneficiaries = benif_response.json()

            for i in range(len(list(beneficiaries['beneficiaries']))):
                print(i, '-> ', beneficiaries['beneficiaries'][i]['name'],
                      beneficiaries['beneficiaries'][i]['beneficiary_reference_id'])

            index = int(input('Select Person by Index : '))

            print(list(range(len(list(beneficiaries['beneficiaries'])))))

            if index in list(range(len(list(beneficiaries['beneficiaries'])))):
                print(
                    'Returning ', beneficiaries['beneficiaries'][index]['beneficiary_reference_id'])
                return beneficiaries['beneficiaries'][index]['beneficiary_reference_id']

    except Exception as ex:
        print(ex.with_traceback())
        # print("Please Try Again")
        exit()


def get_captcha(token):
    captcha_headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
        'Authorization': 'Bearer '+token
    }

    try:
        print('\nGetting Captcha\n')
        cap_resp = requests.post(
            'https://cdn-api.co-vin.in/api/v2/auth/getRecaptcha', headers=captcha_headers)

        if cap_resp.status_code == 200:
            with open('captcha.svg', 'w') as f:
                f.write(
                    re.sub('(<path d=)(.*?)(fill=\"none\"/>)', '', cap_resp.json()['captcha']))

            drawing = svg2rlg('captcha.svg')
            renderPM.drawToFile(drawing, "captcha.png", fmt="PNG")

            layout = [[sg.Image('captcha.png')],
                      [sg.Text("Enter Captcha Below")],
                      [sg.Input()],
                      [sg.Button('Submit', bind_return_key=True)]]

            window = sg.Window('Enter Captcha', layout)
            event, values = window.read()
            window.close()
            return values[1]

        else:
            print(cap_resp)
            print(cap_resp.text)

    except Exception as ex:
        print(ex)
        # print("Please Try Again")
        exit()


def schedule(session_id, phone):

    token = login(phone)

    benifId = get_benif(token)

    sched_headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
        'Authorization': 'Bearer '+token
    }

    print(benifId)

    schedule_details = {
        "dose": 1,
        "session_id": session_id,
        "slot": "FORENOON",
        "beneficiaries": [benifId
                          ],
        "captcha": ''
    }

    try:
        schedule_details['captcha'] = get_captcha(token)

        print('scheduling')
        pprint(schedule_details)
        print('Trying to schedule')

        schedule_response = requests.post(
            'https://cdn-api.co-vin.in/api/v2/appointment/schedule', json=schedule_details, headers=sched_headers)

        if schedule_response.status_code == 200:
            # print(benif_response.headers)
            # pprint(benif_response.json())
            print(schedule_response)
            print(schedule_response.text)
            sched = schedule_response.json()
            print(sched)

            print('Slot Booked Successfully !')

        else:
            print(schedule_response)
            print(schedule_response.text)

    except Exception as ex:
        print(ex)
        # print("Please Try Again")
        exit()


def cancel(phone, appo_id):

    token = login(phone)

    benifId = get_benif(token)

    cancel_headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
        'Authorization': 'Bearer '+token
    }

    print(benifId)

    cancel_details = {
        "appointment_id": appo_id,
        "beneficiariesToCancel": [
            benifId
        ]
    }

    try:
        #cancel_details['captcha'] = get_captcha(token)

        print('scheduling')
        pprint(cancel_details)
        print('Trying to schedule')

        cancel_response = requests.post(
            'https://cdn-api.co-vin.in/api/v2/appointment/cancel', json=cancel_details, headers=cancel_headers)

        if cancel_response.status_code == 200:
            # print(benif_response.headers)
            # pprint(benif_response.json())
            print(cancel_response)
            print(cancel_response.text)
            sched = cancel_response.json()
            print(sched)

            print('Slot Booked Successfully !')

        else:
            print(cancel_response)
            print(cancel_response.text)
            sched = cancel_response.json()
            print(sched)

    except Exception as ex:
        print(ex)
        # print("Please Try Again")
        exit()


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


def search(email, phone, case):

    preffered_pincodes = []

    if case == '1':
        district_id = get_city_code()
        preffered_pincodes = input(
            "Enter your Preffered Pincodes (Separate by space) : ").strip().split(' ')
    else:
        cases['2']['params']['pincode'] = input("Enter PIN Code: ")
        preffered_pincodes.append(cases['2']['params']['pincode'])

    print(data)

    print(preffered_pincodes)

    print("\nSeeking Slots. Will Notify as soon as the slots are available\n")

    while True:
        available_centers = []

        try:
            #print('url', cases[case]['url'])
            #print('params', cases[case]['params'])

            centers_resp = requests.get(
                cases[case]['url'], params=cases[case]['params'], headers=head)

            print(centers_resp)

            centers = centers_resp.json()['centers']
            for center in centers:
                # available = False
                for session in center['sessions']:
                    # print("sd")
                    #if (session['available_capacity'] != 0):
                    if (session['available_capacity'] != 0) and (str(center['pincode']) in preffered_pincodes):
                        print('yoooo')

                        # available = True
                        available_centers.append({"center_id": center['center_id'],
                                                  "name": center['name'],
                                                  "address": center['address'],
                                                  "state_name": center['state_name'],
                                                  "district_name": center['district_name'],
                                                  "block_name": center['block_name'],
                                                  "pincode": center['pincode'],
                                                  "fee_type": center['fee_type'],
                                                  "date": session['date'],
                                                  "vaccine": session['vaccine'],
                                                  "session_id": session['session_id'],
                                                  "min_age_limit": session['min_age_limit']})

            if len(available_centers) != 0:
                print("Vaccine Slot Available. Book Fast")

                # pprint(available_data)

                for i in range(len(available_centers)):
                    print('\nindex: ', i)
                    print(available_centers[i]['center_id'], available_centers[i]['name'],
                          available_centers[i]['block_name'], available_centers[i]['district_name'])
                    print('pin: ', available_centers[i]['pincode'])
                    print('date: ', available_centers[i]['date'])
                    print('vaccine: ', available_centers[i]['vaccine'])
                    print('age limit: ',
                          available_centers[i]['min_age_limit'], '+')
                    print(available_centers[i]['session_id'])

                index = int(input('Select the index to schedule : '))
                print()
                print('Scheduling ', available_centers[index]['session_id'])

                mail(email)

                schedule(available_centers[index]['session_id'], phone)

                break

        except Exception as e:
            #print('error: ', e)
            pass

        time.sleep(5)


def engine():
    email = input("Enter your email: ")
    phone = input("Enter your phone number: ")

    print("1 -> Search By City")
    print("2 -> Search By Pin")
    print('cases', list(cases.keys()))
    switch = input("Enter : ")

    if switch in list(cases.keys()):
        search(email, phone, switch)
    else:
        print("Enter a valid value")


if __name__ == "__main__":
    # test()
    engine()
