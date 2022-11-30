
import os
import sqlite3
import praw
import yfinance as yf
from dotenv import load_dotenv

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

    def get_top_stocks(self, limit):
        None
    
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

if __name__ == '__main__':
    StockHandler()