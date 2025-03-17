from flask import Flask, request, jsonify, render_template
from transformers import pipeline
import pandas as pd
import plotly.express as px
from collections import defaultdict
from datetime import datetime

app = Flask(__name__)

# Load sentiment analysis pipeline
sentiment_analyzer = pipeline("sentiment-analysis")

# Store reviews and sentiments for insights
reviews_data = []

# Track sentiment trends
sentiment_trends = []

# Track top keywords
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
    
    # Get sentiment prediction
    result = sentiment_analyzer(review)
    sentiment = result[0]['label']
    confidence = result[0]['score']
    
    # Store the review and sentiment
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    reviews_data.append({'review': review, 'sentiment': sentiment, 'confidence': confidence, 'timestamp': timestamp})
    
    # Update sentiment trends
    sentiment_trends.append({'timestamp': timestamp, 'sentiment': sentiment})
    
    # Update top keywords
    for word in review.split():
        top_keywords[word.lower()] += 1
    
    return jsonify({'sentiment': sentiment, 'confidence': confidence})

@app.route('/insights', methods=['GET'])
def insights():
    if not reviews_data:
        return jsonify({'error': 'No reviews analyzed yet'}), 400
    
    # Sentiment Distribution
    df = pd.DataFrame(reviews_data)
    sentiment_counts = df['sentiment'].value_counts().reset_index()
    sentiment_counts.columns = ['Sentiment', 'Count']
    sentiment_chart = px.bar(sentiment_counts, x='Sentiment', y='Count', title='Sentiment Distribution')

    # Sentiment Trends
    trends_df = pd.DataFrame(sentiment_trends)
    trends_df['timestamp'] = pd.to_datetime(trends_df['timestamp'])
    trends_chart = px.line(trends_df, x='timestamp', y='sentiment', title='Sentiment Trends Over Time')

    # Top Keywords
    top_keywords_df = pd.DataFrame(top_keywords.items(), columns=['Word', 'Count'])
    top_keywords_df = top_keywords_df.sort_values(by='Count', ascending=False).head(10)
    keywords_chart = px.bar(top_keywords_df, x='Word', y='Count', title='Top Keywords')

    # Combine charts into HTML
    charts_html = f"""
    <div class="row">
        <div class="col-md-6">{sentiment_chart.to_html(full_html=False)}</div>
        <div class="col-md-6">{trends_chart.to_html(full_html=False)}</div>
    </div>
    <div class="row mt-4">
        <div class="col-md-12">{keywords_chart.to_html(full_html=False)}</div>
    </div>
    """
    
    return charts_html

if __name__ == '__main__':
    app.run(debug=True)