from flask import Flask, request
from decouple import config
import requests



app = Flask(__name__)

ACCESS_TOKEN = config('ACCESS_TOKEN', default="")
VERIFY_TOKEN = config('VERIFY_TOKEN', default="")


def reply(user_id, msg):
    """Send reply to the user"""
    data = {
        "recipient": {"id": user_id},
        "message": {"text": msg}
    }
    resp = requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" + ACCESS_TOKEN, json=data)
    print(resp.content)


@app.route('/', methods=['GET'])
def handle_verification():
    """Check verification"""
    if request.args['hub.verify_token'] == VERIFY_TOKEN:
        return request.args['hub.challenge']
    else:
        return "Invalid verification token"


@app.route('/', methods=['POST'])
def handle_incoming_messages():
    """Get input and prepare reply  output"""
    data = request.json
    sender = data['entry'][0]['messaging'][0]['sender']['id']
    message = data['entry'][0]['messaging'][0]['message']['text']
    reply(sender, message)
    return "ok"




if __name__ == '__main__':
    app.run(debug=True)