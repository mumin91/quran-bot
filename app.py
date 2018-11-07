from flask import Flask, request
from decouple import config
import requests
from flaskext.mysql import MySQL


app = Flask(__name__)
mysql = MySQL()
ACCESS_TOKEN = config('ACCESS_TOKEN', default="")
VERIFY_TOKEN = config('VERIFY_TOKEN', default="")

app.config['MYSQL_DATABASE_USER'] = config('MYSQL_DATABASE_USER', default="")
app.config['MYSQL_DATABASE_PASSWORD'] = config('MYSQL_DATABASE_PASSWORD', default="")
app.config['MYSQL_DATABASE_DB'] = config('MYSQL_DATABASE_DB', default="")
app.config['MYSQL_DATABASE_HOST'] = config('MYSQL_DATABASE_HOST', default="")
mysql.init_app(app)


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
    cursor = mysql.get_db().cursor()
    data = request.json
    sender = data['entry'][0]['messaging'][0]['sender']['id']
    message = data['entry'][0]['messaging'][0]['message']['text']

    if message[0].isdigit(): #check if input starts with a digit
        data = message.split(":")
        sura = data[0]
        aya = data[1]
        cursor.execute("SELECT * from quran_text WHERE sura='" + sura + "' AND aya='" + aya + "'")
        cursor_json = convert_to_json(cursor)
        message = cursor_json[0]['text']
        reply(sender, message)
    else:
        message = "Something Wrong!! Tip: the input format should be like 3:222 where 3 is the sura number and 222 is aya number."
        reply(sender, message)

    return "ok"


def convert_to_json(result):
    """Convert SQL output into JSON object"""
    row_headers = [x[0] for x in result.description]  # this will extract row headers
    rv = result.fetchall()
    json_data = []
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))
    return json_data


if __name__ == '__main__':
    app.run(debug=True)