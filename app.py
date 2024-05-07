from flask import Flask, jsonify, request, session
import requests

app = Flask(__name__)


@app.route('/')
def index():
    return jsonify(message="Flask Relay Program is working!"), 200


@app.route('/relay', methods=['GET', 'POST'])
def relay():
    link = request.args.get(
        'link') if request.method == 'GET' else request.form.get('link')
    if not link:
        return jsonify(error="Link parameter is missing"), 400

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
