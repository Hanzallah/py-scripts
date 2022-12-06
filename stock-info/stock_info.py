
import os
import re
import sqlite3
import praw
import nltk
import yfinance as yf
from dotenv import load_dotenv
from collections import Counter
from praw.models import MoreComments

class Stock:
    def __init__(self, name, sector, price, symbol, revenue) -> None:
        self.name = name
        self.sector = sector
        self.price = price
        self.symbol = symbol
        self.revenue = revenue

class StockHandler:
    def __init__(self) -> None:
        load_dotenv()

        reddit = praw.Reddit(
            client_id=os.getenv('reddit_key'),
            client_secret=os.getenv('reddit_secret'),
            password=os.getenv('reddit_password'),
            user_agent=os.getenv('reddit_agent'),
            username=os.getenv('reddit_username'),
        )

        self.wsb_subreddit = reddit.subreddit('wallstreetbets')
        self.counter_dict = {}
        self.top_ticker_symbols = []

    def get_top_stocks(self, limit):
        Nouns = lambda pos:pos[:2] == "NN"

        for submissions in self.wsb_subreddit.hot(limit):
            for top_level_comment in submissions.comments:
                if isinstance(top_level_comment, MoreComments):
                    continue
                
                stock_tickers = nltk.word_tokenize(top_level_comment.body)
                stock_ticker_list = list(set([
                    word for (word, pos) in nltk.pos_tag(stock_tickers) if Nouns(pos) and re.findall(r'[A-Z]+\b', word) and len(yf.Ticker(word).info) > 10 and not word.startswith("/u/")
                ]))
                self.top_ticker_symbols += stock_ticker_list
        
        self.counter_dict = dict(Counter(self.top_ticker_symbols))

        return self.counter_dict

                
    def record_stock_information():
        None

    def get_stock(ticker):
        ticker_info = yf.Ticker(ticker)
        return Stock(ticker_info.info['shortName'])
    
class DatabaseHandler:
    def __init__(self, db_name, table_name) -> None:
        self.db_conn = sqlite3.connect(db_name)
        self.db_cursor = self.db_conn.cursor()
        self.table_name = table_name

    def db_save_info(self, stock: Stock):
        self.db_cursor.execute(
            """
            INSERT INTO ?
            (
                Company_Name, Sector, Stock_Price, Symbol, Total_Revenue
            )
            VALUES (?, ?, ?, ?, ?);
            """, (
                stock.name, stock.sector, stock.price, stock.symbol, stock.revenue
            )
        )
        self.db_conn.commit()

    def db_create(self):
        self.db_cursor.execute(
            """"CREATE TABLE IF NOT EXISTS ?
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Company_Name TEXT,
                Sector TEXT,
                Stock_Price,
                Symbol TEXT,
                Total_Revenue INTEGER
            );
            """, (self.table_name)
        )
        self.db_conn.commit()

    def db_update(self, stock: Stock):
        self.db_cursor.execute(
            f"""
            UPDATE Stock_information
            SET Stock_Price = {stock.price}
            WHERE Symbol = '{stock.symbol}';
            """
        )
        self.db_conn.commit()
    
    def db_fetch(self, stock: Stock):
        self.db_cursor.execute(
            f"""
            SELECT * FROM Stock_information
            SET Stock_Price = {stock.price}
            WHERE Company_Name = '{stock.name}';
            """
        )
        self.db_conn.commit()

if __name__ == '__main__':
    stockHandler = StockHandler()