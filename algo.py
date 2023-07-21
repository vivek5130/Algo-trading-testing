import pandas as pd
import numpy as nm
import requests
import xlsxwriter
import math
from secret import gettoken
stocks= pd.read_csv('sp_500_stocks.csv')
iexcloudtoken = gettoken()

def save_csv(symbol, final_dataframe):
    filename = f"{symbol}.xlsx"
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    final_dataframe.to_excel(writer, sheet_name=symbol, index = False)

    background_color = '#0a0a23'
    font_color = '#ffffff'

    string_format = writer.book.add_format(
            {
                'font_color': font_color,
                'bg_color': background_color,
                'border': 1
            }
        )

    dollar_format = writer.book.add_format(
            {
                'num_format':'$0.00',
                'font_color': font_color,
                'bg_color': background_color,
                'border': 1
            }
        )

    integer_format = writer.book.add_format(
            {
                'num_format':'0',
                'font_color': font_color,
                'bg_color': background_color,
                'border': 1
            }
        )

    writer.sheets[symbol].set_column('B:B', #This tells the method to apply the format to column B
                        18, #This tells the method to apply a column width of 18 pixels
                        string_format #This applies the format 'string_format' to the column
                        )
    column_formats = { 
                        'A': ['Date', string_format],
                        'B': ['ClosePrice', dollar_format],
                    }

    for column in column_formats.keys():
        writer.sheets[symbol].set_column(f'{column}:{column}', 20, column_formats[column][1])
        writer.sheets[symbol].write(f'{column}1', column_formats[column][0], string_format)

    writer._save()

def fetch(symbol):
    # api_url = f"https://sandbox.iexapis.com/stable/stock/{symbol}/quote/?token={iexcloudtoken}"
    api_url = f"https://cloud.iexapis.com/stable/stock/{symbol}/quote?token={iexcloudtoken}"
    #endpoint api link + stable is to access latest stable version +  get quote for getting data + token for api access
    # https://cloud.iexapis.com/stable/stock/aapl/quote?token=YOUR_TOKEN_HERE
    data = requests.get(api_url).json()

    my_columns = ['Date', 'close']
    final_dataframe = pd.DataFrame(columns=my_columns)
    date = "20200101"
    date1 = "20090101"
    date2 = "20090221"
    date3 = "20150727"
    # histurl = f"https://api.iex.cloud/v1/data/CORE/CASH_FLOW/aapl?from=2022-02-18&to=2022-07-20&token={iexcloudtoken}"
    histurl = f"https://cloud.iexapis.com/stable/time-series/HISTORICAL_PRICES/{symbol}?from={date1}&to={date3}&token={iexcloudtoken}"
    # histurl = f"https://api.iex.cloud/v1/data/core/historical_prices/{symbol}?range=2m&token={iexcloudtoken}"
    histdata = requests.get(histurl).json()

    for stock in histdata[:]:
        final_dataframe = final_dataframe._append(
        pd.Series(
            [
            stock['priceDate'],
            stock['close'],
            
            ],
            index=my_columns
        ), 
        ignore_index= True
    )

    #Save it in csv file
    save_csv(symbol,final_dataframe)
def backtest(symbol):
    #used csv file instead of api by keeping in mind of free trials provided by IEX CLOUD 
    # Read historical price data from a CSV file
    # dfxl  = pd.read_excel('amazon.xlsx')
    # dfxl.to_csv ("amazon.csv", index = None, header=True)
    # df = pd.DataFrame(pd.read_csv("recommended_trades.csv"))
    filename = f"{symbol}.csv"
    df = pd.DataFrame(pd.read_csv(filename))

    move20 = 29
    move50 = 0
    #preprocessing and calculating mean price of first 50 days
    sum20 = df.iloc[30:50,[1]].sum(axis=0).values[0]/20
    sum50 = df.iloc[0:50,[1]].sum(axis=0).values[0]/50
    col = ['date','curprice','mv20','mv50', 'indicator','next day price','profit/loss']
    newframe = pd.DataFrame(columns=col)

    #20 50 mvavg
    success=0

    for i in range(200,len(df)-1):
        if(sum20>=sum50):
            pr = 'buy'
        else:
            pr = 'sell'
        if((pr == 'buy' and df.iloc[[i],[1]].values[0][0]<= df.iloc[[i+1],[1]].values[0][0]) or( pr == 'sell' and df.iloc[[i],[1]].values[0][0]>= df.iloc[[i+1],[1]].values[0][0])):
            profit = "Gain"
            success +=1
        else:
            profit = "Loss"
        newframe = newframe._append(
            pd.Series(
            [
            
            df.iloc[[i],[0]].values[0][0],
            df.iloc[[i],[1]].values[0][0],
            sum20,
            sum50,
            pr,
            df.iloc[[i+1],[1]].values[0][0],
            profit
            
            ],
            index=col
        ), 
            ignore_index = True,
        )
        
        move50+=1 
        move20+=1
        sum20 += df.iloc[[i],[1]].values[0][0]/20
        sum20 = abs(sum20 - df.iloc[[move20],[1]].values[0][0]/20)
        sum50 = abs(sum50 - df.iloc[[move50],[1]].values[0][0]/50)
        sum50 += df.iloc[[i],[1]].values[0][0]/50
    print(newframe)
    print(success)
    print("sucess rate: ",(success/(len(df)-1))*100)

    #50 200 mvavg

    # sum50 = df.iloc[149:199,[1]].sum(axis=0).values[0]/50
    # sum200 = df.iloc[0:199,[1]].sum(axis=0).values[0]/200
    # move200 = 0
    # move50 = 149
    # for i in range(200,len(df)-1):
    #     if(sum50>sum200):
    #         pr = 'buy'
    #     else:
    #         pr = 'sell'
    #     newframe = newframe._append(
    #         pd.Series(
    #         [
            
    #         df.iloc[[i],[0]].values[0][0],
    #         df.iloc[[i],[1]].values[0][0],
    #         sum50,
    #         sum200,
    #         pr,
    #         df.iloc[[i+1],[1]].values[0][0],
            
    #         ],
    #         index=col
    #     ), 
    #         ignore_index = True,
    #     )
    #     move50+=1 
    #     move200+=1
    #     sum50 += df.iloc[[i],[1]].values[0][0]/50
    #     sum50 -= df.iloc[[move50],[1]].values[0][0]/50
    #     sum200 -= df.iloc[[move200],[1]].values[0][0]/200
    #     sum200 += df.iloc[[i],[1]].values[0][0]/200

    # print(newframe)

    newfile = f"{symbol}.xlsx"
    sheetname = f"{symbol}test"
    writer = pd.ExcelWriter(newfile, engine='xlsxwriter')
    newframe.to_excel(writer, sheet_name= sheetname, index = False)

    background_color = '#FFFFFF'
    font_color = '#000000'



    string_format = writer.book.add_format(
            {
                'font_color': font_color,
                'bg_color': background_color,
                'border': 1
            }
        )

    dollar_format = writer.book.add_format(
            {
                'num_format':'$0.00',
                'font_color': font_color,
                'bg_color': background_color,
                'border': 1
            }
        )

    integer_format = writer.book.add_format(
            {
                'num_format':'0',
                'font_color': font_color,
                'bg_color': background_color,
                'border': 1
            }
        )

    writer.sheets[sheetname].set_column('B:B', #This tells the method to apply the format to column B
                        18, #This tells the method to apply a column width of 18 pixels
                        string_format #This applies the format 'string_format' to the column
                        )
    column_formats = { 
                        'A': ['Date', string_format],
                        'B': ['currprice', dollar_format],
                        'C': ['mv20', dollar_format],
                        'D': ['mv50', dollar_format],
                        'E': ['Indication', string_format],
                        'F': ['Nextdayprice', dollar_format],
                        'G': ['Profit/loss', string_format],
                    }

    for column in column_formats.keys():
        writer.sheets[sheetname].set_column(f'{column}:{column}', 20, column_formats[column][1])
        writer.sheets[sheetname].write(f'{column}1', column_formats[column][0], string_format)

    writer._save()






# Give different symbol for back testing
print("Enter the symbol you want to test")
print("For example")
print(" 'AMZN ' OR 'AAPL'  .....")
symbol = input()
print("Do you have data present or do you want to fetch it from the api")
print("Enter 1 to fetch data")
print("Entre 2 to if already data is present in csv file and want to backtest")
print("Enter 3 to exit")

while 1:
    val = input()
    if val == "1":
        fetch(symbol)
    elif val == "2":
        backtest(symbol)
    elif val == "3":
        exit
    else:
        print("Invalid input")

            
