from flask import Flask, request, jsonify
import speech_recognition as sr
import pyttsx3
import requests
import wikipedia
import webbrowser
import datetime

# Initialize Flask app
app = Flask(__name__)

# Initialize the voice engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Speed of speech
engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)

NEWS_API_KEY = "c4692a2a30df4e919d1f52728cea4afb"  # Replace with your News API key

def speak(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

def get_covid_data():
    """Fetch COVID-19 statistics."""
    try:
        response = requests.get("https://api.covid19api.com/summary")
        data = response.json()
        global_cases = data['Global']['TotalConfirmed']
        return f"The total confirmed COVID-19 cases worldwide are {global_cases}."
    except Exception as e:
        return "Unable to fetch COVID-19 data at the moment."

def get_news(keyword=None):
    """Fetch and summarize news articles based on a keyword."""
    try:
        if keyword:
            url = f"https://newsapi.org/v2/everything?q={keyword}&sortBy=relevance&apiKey={NEWS_API_KEY}"
        else:
            url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}"
        
        response = requests.get(url)
        news_data = response.json()

        if news_data['status'] == "ok" and news_data['totalResults'] > 0:
            articles = news_data['articles'][:3]  # Fetch top 3 articles
            results = []
            for article in articles:
                title = article.get('title', 'No title available')
                description = article.get('description', 'No description available')
                results.append({"title": title, "description": description})
            return results
        else:
            return f"I couldn't find any news about {keyword}." if keyword else "I couldn't fetch the news right now."
    except Exception as e:
        return "There was an error while fetching the news."

def greet_user():
    """Generate a greeting based on the time of the day."""
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        greeting = "Good Morning!"
    elif 12 <= hour < 18:
        greeting = "Good Afternoon!"
    else:
        greeting = "Good Evening!"
    return f"{greeting} How can I assist you today?"

@app.route("/")
def home():
    return jsonify({"message": "Welcome to the Voice Assistant API!"})

@app.route("/greet", methods=["GET"])
def greet():
    """API endpoint to greet the user."""
    return jsonify({"response": greet_user()})

@app.route("/covid", methods=["GET"])
def covid():
    """API endpoint to get COVID-19 statistics."""
    return jsonify({"response": get_covid_data()})

@app.route("/news", methods=["GET"])
def news():
    """API endpoint to fetch news articles."""
    keyword = request.args.get("keyword")  # Pass keyword as a query parameter
    news_result = get_news(keyword)
    return jsonify({"response": news_result})

@app.route("/wikipedia", methods=["GET"])
def wiki():
    """API endpoint to search Wikipedia."""
    topic = request.args.get("topic")  # Pass topic as a query parameter
    if not topic:
        return jsonify({"error": "No topic provided."})
    try:
        summary = wikipedia.summary(topic, sentences=2)
        return jsonify({"response": summary})
    except wikipedia.exceptions.DisambiguationError:
        return jsonify({"error": "Multiple results found. Please be more specific."})
    except wikipedia.exceptions.PageError:
        return jsonify({"error": "No page found for this topic."})

@app.route("/time", methods=["GET"])
def current_time():
    """API endpoint to get the current time."""
    time = datetime.datetime.now().strftime("%H:%M")
    return jsonify({"response": f"The time is {time}."})

@app.route("/open", methods=["GET"])
def open_website():
    """API endpoint to open a website."""
    website = request.args.get("website")  # Pass website name as a query parameter
    if not website:
        return jsonify({"error": "No website provided."})
    if "youtube" in website.lower():
        webbrowser.open("https://youtube.com")
        return jsonify({"response": "Opening YouTube."})
    elif "google" in website.lower():
        webbrowser.open("https://google.com")
        return jsonify({"response": "Opening Google."})
    else:
        return jsonify({"error": "Website not recognized."})

@app.route("/exit", methods=["GET"])
def exit_app():
    """API endpoint to simulate exit command."""
    return jsonify({"response": "Goodbye! Have a great day."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
