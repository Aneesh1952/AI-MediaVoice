from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
from gtts import gTTS
import os
import requests
import wikipedia
import webbrowser
import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

NEWS_API_KEY = "c4692a2a30df4e919d1f52728cea4afb"  # Replace with your News API key

def speak(text):
    """Convert text to speech using gTTS and save as audio file."""
    tts = gTTS(text=text, lang='en')
    tts.save("response.mp3")
    os.system("mpg123 response.mp3")  # Replace with a library like `playsound` if needed

@app.route("/covid", methods=["GET"])
def get_covid_data():
    """Fetch COVID-19 statistics."""
    try:
        response = requests.get("https://api.covid19api.com/summary")
        data = response.json()
        global_cases = data['Global']['TotalConfirmed']
        message = f"The total confirmed COVID-19 cases worldwide are {global_cases}."
        return jsonify({"message": message})
    except Exception as e:
        return jsonify({"error": "Unable to fetch COVID-19 data at the moment."})

@app.route("/news", methods=["GET"])
def get_news():
    """Fetch and summarize news articles based on a keyword."""
    keyword = request.args.get('keyword')
    try:
        if keyword:
            url = f"https://newsapi.org/v2/everything?q={keyword}&sortBy=relevance&apiKey={NEWS_API_KEY}"
        else:
            url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}"
        
        response = requests.get(url)
        news_data = response.json()

        if news_data['status'] == "ok" and news_data['totalResults'] > 0:
            articles = news_data['articles'][:3]
            message = " ".join([f"News {i + 1}: {article.get('title', 'No title')}" for i, article in enumerate(articles)])
            return jsonify({"message": message})
        else:
            return jsonify({"message": "No news found."})
    except Exception as e:
        return jsonify({"error": "There was an error fetching the news."})

@app.route("/time", methods=["GET"])
def get_time():
    """Fetch the current time."""
    current_time = datetime.datetime.now().strftime("%H:%M")
    return jsonify({"message": f"The time is {current_time}."})

@app.route("/wikipedia", methods=["POST"])
def search_wikipedia():
    """Search Wikipedia for a topic."""
    data = request.json
    topic = data.get("topic", "")
    try:
        summary = wikipedia.summary(topic, sentences=2)
        return jsonify({"message": summary})
    except wikipedia.exceptions.DisambiguationError:
        return jsonify({"error": "Multiple results found. Be more specific."})
    except wikipedia.exceptions.PageError:
        return jsonify({"error": "No page found for this topic."})

@app.route("/open", methods=["POST"])
def open_website():
    """Open a website."""
    data = request.json
    website = data.get("website", "")
    if website == "youtube":
        webbrowser.open("https://youtube.com")
        return jsonify({"message": "Opening YouTube."})
    elif website == "google":
        webbrowser.open("https://google.com")
        return jsonify({"message": "Opening Google."})
    else:
        return jsonify({"error": "Specify a valid website."})

@app.route("/")
def home():
    return jsonify({"message": "Welcome to the Voice Assistant API!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
