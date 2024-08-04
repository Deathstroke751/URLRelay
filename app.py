from flask import Flask, jsonify, request
import requests
from urllib.parse import unquote
from flask_cors import CORS  # Import CORS from Flask-CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def _attempt_download(url: str, _token: str) -> None:
    """
    Attempt to download a small chunk of the file using requests.

    :param url: The URL of the file to download.
    :param headers: Headers to include in the request.
    """

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Upgrade-Insecure-Requests": "1",
        "Cookie": f"accountToken={_token}",
    }
    try:
        with requests.get(url, headers=headers, stream=True) as response:
            if response.status_code == 206:  # Partial content
                for chunk in response.iter_content(chunk_size=1024):
                    return True # We only need to download the first chunk                    
    except requests.RequestException as e:        
        return (False,e)
        

@app.route('/')
def index():
    return jsonify({"version": "1.3", "message": "Flask Relay Program is working!"}), 200

@app.route('/dw')
def dwld():
    dlink = request.args.get('link')
    token = request.args.get('token')    
    
    decoded_url = unquote(dlink)   
    
    
    _st = _attempt_download(decoded_url,token)
    if _st:
        return jsonify({"status": "OK", "message": "File download tested"}), 200
    else:
        reason = f"Failed to download from {link}"
        if isinstance(_st, tuple):
            reason += f": {_st[1]}"
        return jsonify(error=reason), 400


@app.route('/relay', methods=['GET', 'POST'])
def relay():
    link = request.args.get('link')
    # Iterate through the dictionary and construct the URL string
    _args = request.args.to_dict()
    for key, value in _args.items():
        if key == 'link':
            link = value
        else:
            link += f"&{key}={value}"
    if not link:
        return jsonify(error="Link parameter is missing"), 400

    try:
        if request.method == 'GET':
            response = requests.get(link)
        else:
            if request.headers['Content-Type'] == 'application/json':
                response = requests.post(link, json=request.json)
            else:
                response = requests.post(link, data=request.form)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return jsonify(error=str(e)), response.status_code

    content_type = response.headers.get('Content-Type', '')
    if 'application/json' in content_type:
        return jsonify(response.json())
    else:
        return response.text


if __name__ == '__main__':
    app.run(debug=True)
