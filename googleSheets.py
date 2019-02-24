'''
This program reads from a google sheets spreadsheet I setup
a long time ago using IFTTT to record the closing prices of 
Tesla and Amazon stock. It takes the ticker, price, and date
from the spreadsheet and populates two dictionaries with
the data for each of the two stocks. It then finds out which 
of the two stocks the user would like to see data for and
graphs the entire data set for that stock.

NOTE: First half or so of main() function was not written
by me. It is from the example provided by Google on how to
use their Sheets API.

TODO:
1) Make graph look nicer (e.g. gridlines, colors, etc.)
2) MAYBE try and get some more data. Don't spend too much time on that.

'''

###### IMPORTS ######

import pickle
import os.path
import matplotlib.pyplot as plt

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


###### GLOBAL DECLARATIONS ######

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '19ctqz8n-LmjEzvVPwyyfIoJ9V53UhxnxNVPqe_ydctU'
RANGE_NAME = 'A2:E'

# dictionaries containing 'date': stock_price as 'key': value pairs
tsla_dict = {}
amzn_dict = {}


###### FUNCTIONS ######

def main():
    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=RANGE_NAME).execute()
    values = result.get('values', [])

    # makes dictionaries for amazon and tesla stock prices
    # uses 'date': price as the 'key': value pair
    if not values:
        print('No data found.')
    else:
        for row in values:
            if row[2] == 'TSLA':
                tsla_dict[row[0]] = row[3]
            else:
                amzn_dict[row[0]] = row[3]

def pricePlot(stockName, multiple=False):
    # Takes a a name of a stock and plots a line graph of the data

    stockDict = None
    stockDict2 = None
    if stockName == 'tesla':
        stockDict = tsla_dict
    elif stockName == 'amazon':
        stockDict = amzn_dict
    elif multiple == True:
        stockDict = amzn_dict
        stockDict2 = tsla_dict

    # Populates lists with the price and date data
    price_lst = []
    date_lst = []
    for key in stockDict:
        price_lst.append(float(stockDict[key])) 
    for key in stockDict:
        date_lst.append(key)
    
    price_lst2 = []
    if multiple == True:
        for key in stockDict2:
            price_lst2.append(float(stockDict2[key])) 

    # Gets 12 dates that are dynamically chosen by
    # the total amount of dates available
    x_axis_dates = []
    count = 0
    for i in range(12):
        x_axis_dates.append(date_lst[count])
        count += len(date_lst) // 12


    title_name = None
    if stockName == 'tesla':
        title_name = 'Tesla'
    elif stockName == 'amazon':
        title_name = 'Amazon'
    else:
        title_name = 'Amazon and Tesla'

    # Plots data based on whether there are multiple
    # sources of data or not. Also sets the subplot
    # settings to be appropriate for either 1 or 2
    # sets of data.
    title = title_name + " Stock Prices"
    plt.grid()
    if multiple == True:
        plt.plot(date_lst, price_lst, label = "Amazon")
        plt.plot(date_lst, price_lst2, label = "Tesla")
    else:
        plt.plot(date_lst, price_lst)
    plt.title(title)
    plt.xticks(x_axis_dates)
    if multiple == True:
        plt.subplots_adjust(left=0.08, bottom=0.05, right=0.95, top=0.90)
    else:
        plt.subplots_adjust(left=0.08, bottom=0.25, right=0.95,top=0.70)
    plt.legend()
    plt.show()


def getInput():
    # Asks user whether they would like to see stock info
    # for Amazon or Tesla.

    stock = None
    while True:
        stock = input("Would you like to see stock info for Tesla, Amazon, or both?: ")
        if stock.lower() == 'tesla' or stock.lower() == 'amazon' or stock.lower() == 'both':
            if stock.lower() == 'both':
                multiple = True
                break
            else:
                break
        else:
            print("Choose either 'Tesla', 'Amazon', or 'both.")
            print(" ")
    return stock.lower()


###### ACTIVATION ######

if __name__ == '__main__':
    main()
    stockName = getInput()
    if stockName == 'both':
        pricePlot(stockName, multiple=True)
    else:
        pricePlot(stockName)
    