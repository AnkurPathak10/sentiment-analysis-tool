from flask import Flask, render_template, jsonify ,request
from flask_socketio import SocketIO, emit
from textblob import TextBlob
import pandas as pd
from collections import defaultdict
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app)

# Store reviews and sentiments for insights
reviews_data = []
sentiment_trends = []
top_keywords = defaultdict(int)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    review = data.get('review')
    if not review:
        return jsonify({'error': 'No review provided'}), 400
    
    # Get sentiment prediction using TextBlob
    blob = TextBlob(review)
    sentiment = blob.sentiment.polarity
    if sentiment > 0:
        sentiment_label = "POSITIVE"
    elif sentiment < 0:
        sentiment_label = "NEGATIVE"
    else:
        sentiment_label = "NEUTRAL"
    
    # Store the review and sentiment
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    reviews_data.append({'review': review, 'sentiment': sentiment_label, 'confidence': abs(sentiment), 'timestamp': timestamp})
    
    # Update sentiment trends
    sentiment_trends.append({'timestamp': timestamp, 'sentiment': sentiment_label})
    
    # Update top keywords
    for word in review.split():
        top_keywords[word.lower()] += 1
    
    return jsonify({'sentiment': sentiment_label, 'confidence': abs(sentiment)})

@app.route('/insights', methods=['GET'])
def insights():
    if not reviews_data:
        return jsonify({'error': 'No reviews analyzed yet'}), 400
    
    print("Reviews Data:", reviews_data)  # Debugging: Print reviews data
    print("Sentiment Trends:", sentiment_trends)  # Debugging: Print sentiment trends
    print("Top Keywords:", top_keywords)  # Debugging: Print top keywords
    
    # Sentiment Distribution
    df = pd.DataFrame(reviews_data)
    sentiment_counts = df['sentiment'].value_counts().reset_index()
    sentiment_counts.columns = ['Sentiment', 'Count']
    
    # Sentiment Trends
    trends_df = pd.DataFrame(sentiment_trends)
    trends_df['timestamp'] = pd.to_datetime(trends_df['timestamp'])
    
    # Top Keywords
    top_keywords_df = pd.DataFrame(top_keywords.items(), columns=['Word', 'Count'])
    top_keywords_df = top_keywords_df.sort_values(by='Count', ascending=False).head(10)
    
    # Render the insights template
    return render_template('insights.html', 
                           sentiment_counts=sentiment_counts.to_dict('records'),
                           trends_df=trends_df.to_dict('records'),
                           top_keywords_df=top_keywords_df.to_dict('records'))

@socketio.on('analyze_review')
def handle_analyze_review(review):
    if not review:
        return
    
    # Get sentiment prediction using TextBlob
    blob = TextBlob(review)
    sentiment = blob.sentiment.polarity
    if sentiment > 0:
        sentiment_label = "POSITIVE"
    elif sentiment < 0:
        sentiment_label = "NEGATIVE"
    else:
        sentiment_label = "NEUTRAL"
    
    # Emit the result to the client
    emit('sentiment_result', {
        'sentiment': sentiment_label,
        'confidence': abs(sentiment)
    })

import json

# Load movie database
with open('movies.json') as f:
    movies = json.load(f)

def recommend_movies(sentiment):
    return [movie['title'] for movie in movies if movie['sentiment'] == sentiment]

if __name__ == '__main__':
    socketio.run(app, debug=True)