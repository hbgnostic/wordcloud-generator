from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from collections import Counter
import re
import os

app = Flask(__name__, static_url_path='', static_folder='static')
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5000", "allow_headers": ["Content-Type"]}})

@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

@app.route('/generate', methods=['POST', 'OPTIONS'])
def generate_wordcloud():
    if request.method == "OPTIONS":
        return jsonify({"message": "OK"}), 200

    url = request.json.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    print(f"Received URL: {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()
        print(f"Fetched URL: {url}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return jsonify({"error": str(e)}), 400

    soup = BeautifulSoup(response.text, 'html.parser')
    text = soup.get_text()
    words = re.findall(r'\w+', text.lower())
    word_count = Counter(words)

    stop_words = set([
        'the', 'a', 'an', 'in', 'to', 'for', 'of', 'and', 'is', 'are',
        'would', 'then', 'with', 'that', 'this', 'on', 'at', 'be', 'as',
        'by', 'from', 'it', 'was', 'were', 'has', 'have', 'had', 'but',
        'or', 'if', 'he', 'she', 'they', 'them', 'their', 'his', 'her'
    ])

    filtered_word_count = {word: count for word, count in word_count.items()
                           if word not in stop_words and len(word) > 3}

    top_words = sorted(filtered_word_count.items(), key=lambda x: x[1], reverse=True)[:100]

    print(f"Top words: {top_words[:10]}")  # Print the top 10 words for debugging

    return jsonify(top_words)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://127.0.0.1:5000')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5000)

