from flask import Flask, render_template, request, redirect, url_for

import requests

from requests.auth import HTTPBasicAuth

import json

app = Flask(__name__)

@app.route('/')
def index():
    vehicles = ["Truck", "Lorry", "Tractor"]
    return render_template('index.html', vehicles=vehicles)

# Configure M-PESA credentials
MPESA_CONSUMER_KEY = 'your_consumer_key'
MPESA_CONSUMER_SECRET = 'your_consumer_secret'
MPESA_SHORTCODE = 'your_shortcode'
MPESA_PASSKEY = 'your_passkey'
MPESA_CALLBACK_URL = 'https://your_callback_url'

def get_mpesa_access_token():
    url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    response = requests.get(url, auth=HTTPBasicAuth(MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET))
    json_response = response.json()
    return json_response['access_token']

def lipa_na_mpesa_online(phone_number, amount):
    access_token = get_mpesa_access_token()
    api_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
    headers = {'Authorization': 'Bearer {}'.format(access_token)}
    payload = {
        "BusinessShortCode": MPESA_SHORTCODE,
        "Password": generate_password(),
        "Timestamp": generate_timestamp(),
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": MPESA_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": MPESA_CALLBACK_URL,
        "AccountReference": "Garbage Collection",
        "TransactionDesc": "Payment for garbage collection services"
    }
    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()

def generate_password():
    import base64
    from datetime import datetime
    data_to_encode = MPESA_SHORTCODE + MPESA_PASSKEY + generate_timestamp()
    encoded_string = base64.b64encode(data_to_encode.encode())
    return encoded_string.decode('utf-8')

def generate_timestamp():
    from datetime import datetime
    return datetime.now().strftime('%Y%m%d%H%M%S')

@app.route('/')
def home():
    vehicles = ["Truck", "Lorry", "Tractor"]
    return render_template('index.html', vehicles=vehicles)

@app.route('/pay', methods=['POST'])
def pay():
    phone_number = request.form['phone_number']
    amount = request.form['amount']
    response = lipa_na_mpesa_online(phone_number, amount)
    return render_template('payment_status.html', response=response)

if __name__ == '__main__':
    app.run(debug=True)
