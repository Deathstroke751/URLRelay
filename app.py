from flask import Flask, jsonify, request
import requests
from flask_cors import CORS  # Import CORS from Flask-CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route('/')
def index():
    return jsonify({"version": "1.1", "message": "Flask Relay Program is working!"}), 200


@app.route('/relay', methods=['GET', 'POST'])
def relay():
    _args = request.args.to_dict()
    link = request.args.get(
        'link') if request.method == 'GET' else request.form.get('link')
    if not link:
        return jsonify(error="Link parameter is missing"), 400
    # Iterate through the dictionary and construct the URL string
    for key, value in _args.items():
        if key == 'link':
            link = value
        else:
            link += f"&{key}={value}"

    try:
        if request.method == 'GET':
            response = requests.get(link)
        else:
            response = requests.post(link, data=request.form)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify(error=str(e)), 500

    content_type = response.headers.get('Content-Type', '')
    if 'application/json' in content_type:
        return jsonify(response.json())
    else:
        return response.text


if __name__ == '__main__':
    app.run(debug=True)
