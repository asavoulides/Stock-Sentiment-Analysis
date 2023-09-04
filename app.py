import openai
import yfinance as yf
import pandas as pd
import numpy as np
from newsapi import NewsApiClient
import tkinter as tk
from tkinter import ttk
import webbrowser
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta


# Initialize OpenAI API
openai.api_key = "YOUR API KEY"

# Initialize News API
newsapi = NewsApiClient(api_key="YOUR API KEY")


# Function to fetch stock data
def fetch_stock_data(ticker, start_date, end_date):
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    return stock_data


def plot_stock_data():
    ticker = ticker_entry.get()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)  # Last 6 months
    stock_data = fetch_stock_data(ticker, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    stock_data['Close'].plot()
    plt.title(f"{ticker} Stock Price")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.show()



# Function to perform sentiment analysis using GPT-3.5 Turbo
def analyze_sentiment(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": f"""
          Please analyze the sentiment of the following text: '{text}'. Provide a numerical sentiment score between -1 (very negative) and 1 (very positive). 
          Only response in a number, do not include any other text such as introductions or context to the answer. 
          For example,
          You would be told: "Stock beats investors expectations by 5% increase in revenue"
          and you would return: "1"
          """,
            }
        ],
    )
    sentiment_score = float(response["choices"][0]["message"]["content"])
    return sentiment_score

# Function to open URL
def open_url(url):
    webbrowser.open(url)

# Fetch news articles
def fetch_news(ticker):
    news = newsapi.get_everything(
        q=ticker, language="en", sort_by="relevancy", page_size=10
    )
    articles = [
        (article["title"], article["content"], article["url"])
        for article in news["articles"]
    ]
    return articles


# Main function to execute trading strategy
def execute_strategy():
    ticker = ticker_entry.get()
    news_data = fetch_news(ticker)
    sentiment_scores = [analyze_sentiment(article[1]) for article in news_data]
    average_sentiment = np.mean(sentiment_scores)
    result_label.config(text=f"Average Sentiment Score: {average_sentiment}")
    for i, (title, content, url) in enumerate(news_data):
            ttk.Label(frame, text=f"Article {i+1}: {title}").grid(row=3+i, column=0, sticky=tk.W)
            ttk.Label(frame, text=f"Score: {sentiment_scores[i]}").grid(row=3+i, column=1)
            ttk.Button(frame, text="Open Link", command=lambda url=url: open_url(url)).grid(row=3+i, column=2)

# GUI
root = tk.Tk()
root.title("Stock Sentiment Analysis")

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

ticker_label = ttk.Label(frame, text="Enter Stock Ticker:")
ticker_label.grid(row=0, column=0, sticky=tk.W)
ticker_entry = ttk.Entry(frame, width=15)
ticker_entry.grid(row=0, column=1)

result_label = ttk.Label(frame, text="")
result_label.grid(row=1, columnspan=3)

analyze_button = ttk.Button(frame, text="Analyze", command=execute_strategy)
analyze_button.grid(row=2, columnspan=3)

plot_button = ttk.Button(frame, text="Plot Stock Data", command=plot_stock_data)
plot_button.grid(row=2, column=2,columnspan=6)  # Moved to row 4 to avoid overlap

root.mainloop()