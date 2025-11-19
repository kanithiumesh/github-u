from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
TWILIO_ACCOUNT_SID = 'ACe6c05969bf31f5229b464ac6c13f1a35'
TWILIO_AUTH_TOKEN = 'af5765406d4caecd8d92d0a0442c9b35'
TWILIO_PHONE_NUMBER = '+19789337983'  # Must be a Twilio-provisioned SMS number
# Optional: use a Messaging Service instead of a raw phone number
MESSAGING_SERVICE_SID = ''  # e.g., 'MGxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
from flask import Flask, render_template, request
import random

app = Flask(__name__)

@app.route('/')


def home():
    return render_template('index.html')

otp_store = {}
@app.route('/send_otp', methods=['POST'])
def send_otp():
    contact = request.form.get('contact', '').strip()
    if not contact.startswith('+'):
        return "Invalid phone number format. Use E.164, e.g., +918012345678", 400
    if not MESSAGING_SERVICE_SID and contact == TWILIO_PHONE_NUMBER:
        return "Destination number cannot be the same as the Twilio 'from' number.", 400

    otp = str(random.randint(1000, 9999))
    otp_store[contact] = otp
    try:
        if MESSAGING_SERVICE_SID:
            message = client.messages.create(
                body=f'Your OTP is: {otp}',
                messaging_service_sid=MESSAGING_SERVICE_SID,
                to=contact,
            )
        else:
            message = client.messages.create(
                body=f'Your OTP is: {otp}',
                from_=TWILIO_PHONE_NUMBER,
                to=contact,
            )
        print("Twilio message SID:", message.sid)
    except TwilioRestException as tre:
        print("Twilio error:", tre.code, str(tre))
        return f"Failed to send OTP (Twilio {tre.code}). {str(tre)}", 502
    except Exception as twilio_error:
        print("Twilio send error:", twilio_error)
        return "Failed to send OTP. Check number, Twilio trial verification, and from number.", 502

    return render_template('verify.html', contact=contact)

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    contact = request.form.get('contact')
    entered_otp = request.form.get('otp')
    real_otp = otp_store.get(contact)

    if entered_otp == real_otp:
        return "OTP Verified Successfully!"
    else:
        return "Invalid OTP. Try again."

if __name__ == '__main__':
    app.run(debug=True)
