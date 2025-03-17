from flask import Flask, request, jsonify
from transformers import pipeline
import pandas as pd
import plotly.express as px

app = Flask(__name__)

# Load sentiment analysis pipeline
sentiment_analyzer = pipeline("sentiment-analysis")

# Store reviews and sentiments for insights
reviews_data = []

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
    reviews_data.append({'review': review, 'sentiment': sentiment, 'confidence': confidence})
    
    return jsonify({'sentiment': sentiment, 'confidence': confidence})

from flask import render_template

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/insights', methods=['GET'])
def insights():
    if not reviews_data:
        return jsonify({'error': 'No reviews analyzed yet'}), 400
    
    # Create a DataFrame for visualization
    df = pd.DataFrame(reviews_data)
    sentiment_counts = df['sentiment'].value_counts().reset_index()
    sentiment_counts.columns = ['Sentiment', 'Count']
    
    # Create a bar chart
    fig = px.bar(sentiment_counts, x='Sentiment', y='Count', title='Sentiment Distribution')
    chart_html = fig.to_html(full_html=False)
    
    return chart_html

if __name__ == '__main__':
    app.run(debug=True)