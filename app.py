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
openai.api_key = ""

# Initialize News API
newsapi = NewsApiClient(api_key="3982781f3a644c7892bcdef212ff5b6f")


# Function to fetch stock data
def fetch_stock_data(ticker, start_date, end_date):
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    return stock_data


def plot_stock_data():
    ticker = ticker_entry.get()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)  # Last 6 months
    stock_data = fetch_stock_data(
        ticker, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
    )
    stock_data["Close"].plot()
    plt.title(f"{ticker} Stock Price")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.show()


# Function to perform sentiment analysis using GPT-3.5 Turbo
total_analyzed = 0


def analyze_sentiment(text):
    global total_analyzed
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": f"""
          Please analyze the sentiment of the following text: '{text}'. Provide a numerical sentiment score between -1 (very negative) and 1 (very positive). 
          The Score you give should be coorilated to if the article is good or bad new's for the company's stock. If it is unclear you should make a best guess.
          You should not take into account the tone.
          Only response in a number and a short text of explanation after the number with ":" as a separator.
          """,
            }
        ],
    )
    sentiment_response = response["choices"][0]["message"]["content"]
    print(f"Analyzing News: {total_analyzed}")
    total_analyzed += 1
    return sentiment_response  # This will now return the score and the short text


# Function to open URL
def open_url(url):
    webbrowser.open(url)


# Fetch news articles
def fetch_news(ticker):
    news = newsapi.get_everything(
        q=ticker, language="en", sort_by="publishedAt", page_size=10
    )
    articles = [
        (article["title"], article["content"], article["url"])
        for article in news["articles"]
    ]
    print("Articles Fetched")
    return articles


def show_description(description):
    new_window = tk.Toplevel(root)
    new_window.title("Description")
    tk.Label(new_window, text=description, wraplength=400).pack()


# Main function to execute trading strategy
def execute_strategy():
    ticker = ticker_entry.get()
    news_data = fetch_news(ticker)
    sentiment_data = [analyze_sentiment(article[1]) for article in news_data]
    sentiment_scores = [float(data.split(":")[0]) for data in sentiment_data]
    sentiment_descriptions = [
        data.split(":")[1] for data in sentiment_data
    ]  # Extracting the short text explanation
    average_sentiment = np.mean(sentiment_scores)
    result_label.config(text=f"Average Sentiment Score: {round(average_sentiment,3)}")

    for i, (title, content, url) in enumerate(news_data):
        ttk.Label(frame, text=f"Article {i+1}: {title}").grid(
            row=3 + i, column=0, sticky=tk.W
        )
        ttk.Label(frame, text=f"Score: {sentiment_scores[i]}").grid(row=3 + i, column=1)
        ttk.Button(frame, text="Open Link", command=lambda url=url: open_url(url)).grid(
            row=3 + i, column=2
        )
        ttk.Button(
            frame,
            text="Show Description",
            command=lambda description=sentiment_descriptions[i]: show_description(
                description
            ),
        ).grid(row=3 + i, column=3)


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
plot_button.grid(row=2, column=3)  # Moved to avoid overlap

root.mainloop()
