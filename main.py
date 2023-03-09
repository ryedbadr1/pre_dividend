# -*- coding: utf-8 -*-
import certifi
import robin_stocks as rs
# To install this dependancy: pip install robin_stocks
# Documentation found at: https://github.com/jmfernandes/robin_stocks/blob/master/Robinhood.rst
# More documentation: https://www.robin-stocks.com/en/latest/robinhood.html
# Note: documentation is a bit outdated, if you get an error while trying to use one of the functions and can't figure out why then let me know
import sys
import os
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
    - Database checking for selling should occur every day, buying algorithm should occur every day.
    - Delete stock from database after it is sold
    
    PARAMETERS TO FOLLOW:
        - Do not make more than 3 day trades per week (should not have to anyways)
        - Do not go under min_buying_power (rather have a balance of 21 rather than 19 if min_buying_power is set to 20)
        - Sell the stock early if it loses over 10% of its value (create stop loss)
    
    - If at any point you are confused about a step you can call/text 630-383-9281 or email ryedbadr1@gmail.com
"""

def stock_scrape():
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
    time.sleep(5)

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


def affordable_stocks(validstocks):
    buyingpower = float(rs.robinhood.profiles.load_account_profile()["buying_power"])

    for stock in validstocks:
        if stock.price > buyingpower:
            validstocks.remove(stock)
    return validstocks


def divSort(validstocks):
    for i in range(1, len(validstocks)):
        value_to_sort = validstocks[i]
        while validstocks[i - 1].dividend < value_to_sort.dividend and i > 0:
            validstocks[i], validstocks[i - 1] = validstocks[i - 1], validstocks[i]
            i = i - 1
    return validstocks
    
'''
Creating Database
'''

def database():
    connection = "mongodb+srv://prediv:prediv@cluster0.exonjyg.mongodb.net/?retryWrites=true&w=majority"
    client = pymongo.MongoClient(connection, tlsCAFile=certifi.where())
    return client["prediv"]

'''
Buy stocks
'''

# Stock price might change in the few seconds it takes to get from here to when we modified the list based on the price of the stock, just fyi
# perhaps we should add a trailing stop loss instead of just 10%?
def buy_stocks(validstocks):
    db = database()
    collection = db["stocks"]
    date_today = str(date.today())
    min_buying_power = 15

    while True:
        all_stocks_bought = all(buyingpower - stock.price < min_buying_power for stock in validstocks)

        for stock in validstocks:
            buyingpower = float(rs.robinhood.profiles.load_account_profile()["buying_power"])
            if (buyingpower - stock.price) < min_buying_power:
                pass

            else:
                rs.robinhood.orders.order_buy_market(validstocks.name, 1)
                post = {"Ticker": stock.name, "Price": stock.price, "Date": date_today}
                collection.insert_one(post)
                
        if all_stocks_bought is True:
            break

'''
Selling Stocks
'''

def sell_stocks():
    week_ago = str(date.today() - timedelta(weeks = 1))
    today = str(date.today())
    db = database()
    collection = db["stocks"]
    week_ago_stocks = collection.find(
        {"Date": week_ago},
        {"Ticker":1, '_id':0}
    )

    for stock in week_ago_stocks:
        rs.robinhood.orders.order_sell_market(stock["Ticker"], 1)
        collection.delete_one(stock)

    ceiling = 10
    stop_loss = -10
    count = 0

    all_stocks = collection.find({})

    for stock in all_stocks:
        newprice = rs.robinhood.stocks.get_latest_price(stock["Ticker"], priceType=None, includeExtendedHours=True)
        oldprice = stock["Price"]
        percent_change = ((newprice - oldprice) / oldprice) * 100

        if stock["Date"] == today & ((percent_change >= ceiling) | (percent_change <= stop_loss)):
            rs.robinhood.orders.order_sell_market(stock["Ticker"], 1)
            collection.delete_one(stock)
            count += 1
            if count == 3:
                sys.exit()

        elif percent_change >= ceiling:
            rs.robinhood.orders.order_sell_market(stock["Ticker"], 1)
            collection.delete_one(stock)

        elif percent_change <= stop_loss:
            rs.robinhood.orders.order_sell_market(stock["Ticker"], 1)
            collection.delete_one(stock)


def runProgram():
    sell_stocks(buy_stocks(database(divSort(affordable_stocks(stock_scrape())))))
    
# Logout: keep at the end of the program
# rs.robinhood.authentication.logout()