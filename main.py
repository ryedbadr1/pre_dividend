# -*- coding: utf-8 -*-
"""
Make sure that you have the following dependancies installed:
    robin_stocks
    requests
    BeautifulSoup
    random
"""

import robin_stocks as rs
# To install this dependancy: pip install robin_stocks
# Documentation found at: https://github.com/jmfernandes/robin_stocks/blob/master/Robinhood.rst
# More documentation: https://www.robin-stocks.com/en/latest/robinhood.html
# Note: documentation is a bit outdated, if you get an error while trying to use one of the functions and can't figure out why then let me know
import sys
import os


"""
Don't worry about the path insert and library that follows.
This just imports some of the starter code that I give you.
"""
sys.path.insert(1, os.path.abspath(os.path.dirname(sys.argv[0]))+str("\\userincludes"))
import login as log
import validstocks as vs
from bs4 import BeautifulSoup
import requests
import requests.exceptions
from datetime import datetime, timedelta, date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import time
import pymongo
# DO NOT REMOVE ANY CODE BEFORE THIS POINT

""" The trading algorithm fully layed out:
    
    - Get list of stocks that are 1 week off of ex-dividend date and initialize vs.ValidStock
    - Store all vs.ValidStock's as an array
    - Get user buying power from Robinhood and store in a variable
    - Loop through the array and erase any stocks that the user can't afford
    - Re-order the array starting from highest dividend to lowest dividend
    - Buy stocks
        - Start with 1 stock of the fisrt index then 1 of the next all the way until buying power reaches the variable min_buying_power
        - We can meet again if you need clarification on this
    - Store all bought stocks in database along with date bought (maybe MongoDB) => we can discuss this when you get here
    - Check database every day and sell stocks right before ex-dividend or if the stock has increased more than ceiling% in value
        - Ceiling is a variable
    - Database checking for selling should occur every day, buying algorithm should occur once per week.
    - Delete stock from database after it is sold
    
    PARAMETERS TO FOLLOW:
        - Do not make more than 3 day trades per week (should not have to anyways)
        - Do not go under min_buying_power (rather have a balance of 21 rather than 19 if min_buying_power is set to 20)
        - Sell the stock early if it loses over 10% of its value (create stop loss)
    
    - If at any point you are confused about a step you can call/text 630-383-9281 or email ryedbadr1@gmail.com
"""

def stockscrape():
    # Load date one week from today
    weekaway = date.today() + timedelta(weeks = 1)

    # Run firefox in the background without opening the application
    options = Options()
    options.add_argument('-headless')
    driver = webdriver.Firefox(options=options)


    # Navigate to the dividend calendar page
    driver.get('https://www.investing.com/dividends-calendar/')

    # Click the "Next Week" tab
    next_week_tab = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "timeFrame_nextWeek")))
    driver.execute_script("arguments[0].click();", next_week_tab)

    #Scroll to the bottom to the page to let all stocks load in the table
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait for "Next Week" tab to load so we can pull data
    time.sleep(3)

    # Wait for the dividend table to load and grab html content
    table = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "dividendsCalendarData")))
    table_html = table.get_attribute('innerHTML')

    # Create a BeautifulSoup object from the HTML content
    soup = BeautifulSoup(table_html, 'html.parser')

    # Find all rows in the table
    rows = soup.find_all('tr')

    # Login to Robinhood account to retrieve latest prices and buying power
    log.login()

    # Loop through the rows and extract the information into a vs.ValidStock object, store in a list
    validstocks = []
    for row in rows[3:]:
        if row.has_attr('tablesorterdivider'):
            continue
        cols = row.find_all('td')
        s = cols[1].text
        ticker = s[s.find("(")+1:s.find(")")]
        if cols[2].text == weekaway.strftime("%b %d, %Y"):
            price = rs.robinhood.stocks.get_latest_price(ticker, priceType='ask_price', includeExtendedHours=True)
            if price[0] is not None:
                stock = vs.ValidStock(ticker, float(price[0]), float(cols[3].text))
                validstocks.append(stock)
    driver.quit()
    return validstocks


def affordable_stock(validstocks):
    #Load users buying power
    buyingpower = float(rs.robinhood.profiles.load_account_profile()["buying_power"])

    # Create a new list of all the stocks the user can afford
    for stock in validstocks:
        if stock.price > buyingpower:
            validstocks.remove(stock)
    return validstocks


def div_sort(validstocks):
    # Sort the list in order from highest to lowest dividend (insertion sort)
    for i in range(1, len(validstocks)):
        value_to_sort = validstocks[i]
        while validstocks[i - 1].dividend < value_to_sort.dividend and i > 0:
            validstocks[i], validstocks[i - 1] = validstocks[i - 1], validstocks[i]
            i = i - 1
    return validstocks
    
'''
Creating Database
'''

connection_string = "mongodb+srv://prediv:prediv@cluster0.exonjyg.mongodb.net/?retryWrites=true&w=majority"
client = pymongo.MongoClient(connection_string)

db = client["prediv"]
collection = db["stocks"]

post = {"ex:stock": "AAPL", "price": 200}
collection.insert_one(post)

'''
Buy stocks
'''
# Minimum buying power
#min_buying_power = 20

# If the stock price is greater than our min_buying_power, do not buy, otherwise, purchase the stock at market price
# Stock price might change in the few seconds it takes to get from here to when we modified the list based on the price of the stock, just fyi
'''
min_buying_power = 15
for stock in validstocks:
    buyingpower = float(rs.robinhood.profiles.load_account_profile()["buying_power"])
    if (buyingpower - stock.price) < min_buying_power:
        pass
    else:
        rs.robinhood.orders.order_buy_market(validstocks.name)
    #myDoc = {"Ticker": stock.name, "Price": stock.price, "Date": date.today()}
    #collection.insert_one(myDoc)

'''


'''
# These variables are subject to change
ceiling = 15


# Example of how to initialize a stock in a class
# Note: you can edit this class in validstocks.py if you see fit (/userincludes/validstocks.py)
test_stock = vs.ValidStock("APPL", 153.48, 0.59)


# Log into a robinhood account
# log.login(string email, string password)
# If called with no parameters, it logs into my account

log.login()

#gets balance left in account (money left that is not invested)
#use to test if you are logged in correctly

#print(rs.robinhood.profiles.load_account_profile()["buying_power"])

'''

# Logout: keep at the end of the program
# rs.robinhood.authentication.logout()


