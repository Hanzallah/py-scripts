
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
    def __init__(self, name, sector, price, symbol, revenue, quoteType, prevClose) -> None:
        self.name = name
        self.sector = sector
        self.price = price
        self.symbol = symbol
        self.revenue = revenue
        self.quoteType = quoteType
        self.prevClose = prevClose
    

    def set_sector(self, sector) -> None:
        self.sector = sector
    
    def set_price(self, price) -> None:
        self.price = price
    
    def set_revenue(self, revenue) -> None:
        self.revenue = revenue

class StockHandler:
    def __init__(self, limit=5) -> None:
        load_dotenv()

        reddit = praw.Reddit(
            client_id=os.getenv('reddit_key'),
            client_secret=os.getenv('reddit_secret'),
            password=os.getenv('reddit_password'),
            user_agent=os.getenv('reddit_agent'),
            username=os.getenv('reddit_username'),
        )

        self.wsb_subreddit = reddit.subreddit('wallstreetbets')
        self.dbHandler = DatabaseHandler("stock_info.db", "Stock_Info")
        self.counter_dict = {}
        self.top_ticker_symbols = []
        self.limit = limit

    def run_top_stocks(self):
        Nouns = lambda pos:pos[:2] == "NN"
        reserved = ['WSB']

        for submissions in self.wsb_subreddit.hot(limit=self.limit):
            for top_level_comment in submissions.comments:
                if isinstance(top_level_comment, MoreComments):
                    continue
                
                stock_tickers = nltk.word_tokenize(top_level_comment.body)
                stock_ticker_list = list(set([
                    word for (word, pos) in nltk.pos_tag(stock_tickers) if Nouns(pos) and re.findall(r'[A-Z]+\b', word) and len(yf.Ticker(word).info) > 10 and not word.startswith("/u/") and word not in reserved
                ]))
                self.top_ticker_symbols += stock_ticker_list
                break
        
        self.counter_dict = dict(Counter(self.top_ticker_symbols))

        self.__record_stock_information__()

                
    def __record_stock_information__(self):
        top_limit = sorted(self.counter_dict, key=self.counter_dict.get, reverse=True)[:self.limit]
        print(top_limit)
        for ticker in top_limit:
            stock = self.__get_stock__(ticker)
            self.dbHandler.db_create()

            company_data_conn = self.dbHandler.db_fetch(stock)
            company_check = company_data_conn.fetchall()
            length_check = [i for i in company_check]

            if stock.quoteType == 'ETF':
                stock.set_sector('No sector (ETF)')
                stock.set_price(stock.prevClose)
                stock.set_revenue('N/A')
            
            if len(length_check) > 0:
                self.dbHandler.db_update(stock)
            else:
                self.dbHandler.db_save(stock)

    def __get_stock__(self, ticker):
        ticker_info = yf.Ticker(ticker)
        return Stock(
            ticker_info.info['shortName'], ticker_info.info['sector'], ticker_info.info['currentPrice'], 
            ticker_info.info['symbol'], ticker_info.info['totalRevenue'], 
            ticker_info.info['quoteType'], ticker_info.info['previousClose']
        )
    
class DatabaseHandler:
    def __init__(self, db_name, table_name) -> None:
        self.db_conn = sqlite3.connect(db_name)
        self.db_cursor = self.db_conn.cursor()
        self.table_name = table_name

    def db_create(self):
        self.db_cursor.execute(
            f"""CREATE TABLE IF NOT EXISTS {self.table_name}
            (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                Company_Name TEXT,
                Sector TEXT,
                Stock_Price,
                Symbol TEXT,
                Total_Revenue INTEGER
            );
            """
        )
        self.db_conn.commit()

    def db_save(self, stock: Stock):
        self.db_cursor.execute(
            f"""
            INSERT INTO {self.table_name}
            (
                Company_Name, Sector, Stock_Price, Symbol, Total_Revenue
            )
            VALUES ({stock.name}, {stock.sector}, {stock.price}, {stock.symbol}, {stock.revenue});
            """
        )
        self.db_conn.commit()

    def db_update(self, stock: Stock):
        self.db_cursor.execute(
            f"""
            UPDATE {self.table_name}
            SET Stock_Price = {stock.price}
            WHERE Symbol = '{stock.symbol}';
            """
        )
        self.db_conn.commit()
    
    def db_fetch(self, stock: Stock):
        return self.db_cursor.execute(
            f"""
            SELECT * FROM {self.table_name}
            WHERE Company_Name = '{stock.name}';
            """
        )
        

if __name__ == '__main__':
    stockHandler = StockHandler()
    stockHandler.run_top_stocks()