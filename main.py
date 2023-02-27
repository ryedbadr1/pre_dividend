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

#test
"""
Don't worry about the path insert and library that follows.
This just imports some of the starter code that I give you.
"""
sys.path.insert(1, os.path.abspath(os.path.dirname(sys.argv[0]))+str("\\userincludes"))
import login as log
import validstocks as vs
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
# These variables are subject to change
min_buying_power = 20
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
print(rs.robinhood.profiles.load_account_profile()["buying_power"])

# Logout: keep at the end of the program
rs.robinhood.authentication.logout()


