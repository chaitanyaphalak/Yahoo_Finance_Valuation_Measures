

import pandas as pd
from yahoofinancials import YahooFinancials
import requests
import bs4 as bs
import xlsxwriter
from datetime import datetime


tickers=["OMC","WPP","IPG","DNTUF","ACN","IT","HURN","BAH","FCN","PRFT","CTSH","VRTU","FLNT","MCHX","DMS","QUOT","PFSW","THRY","KBNT","MRIN","CREX","BLIN"]
all_df_1 = pd.DataFrame()
all_df_2 = pd.DataFrame()

def get_df_1(ticker):
    yahoo_financials = YahooFinancials(ticker)
    stats_1=yahoo_financials.get_key_statistics_data()
    df_1=pd.DataFrame(stats_1).loc[['enterpriseValue'],:].transpose()
    df_1['marketCap']= [yahoo_financials.get_market_cap()]

    return df_1

for ticker in tickers:
    df_1 = get_df_1(ticker)
    if len(all_df_1) ==0:
        all_df_1 = df_1
    else:
        all_df_1 = all_df_1.append(df_1)


###############################################################################
########Function to scrape data from yahoo finance statistics page ############
###############################################################################

def get_df_2(ticker):
    url = r'https://sg.finance.yahoo.com/quote/{0}/key-statistics?p={0}'.format(ticker)
    # Fake as a browser, otherwise Yahoo will block you
    headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    stats_2 = pd.read_html(requests.get(url, headers=headers).text)
    vMeasures = stats_2 [0]
    for df in stats_2 [1:]:
        vMeasures = vMeasures.append(df)
    df_2=vMeasures[2:9].set_index(0).T

    return df_2

###############################################################################
##############Create a Pandas DF for a list of tickers ########################
###############################################################################

for ticker in tickers:
    df_2 = get_df_2(ticker)
    if len(all_df_2) ==0:
        all_df_2 = df_2
    else:
        all_df_2 = all_df_2.append(df_2)









###############################################################################
############## Save DF in Excel & format the table ############################
###############################################################################


day=datetime.today().strftime('%Y-%m-%d')
stamp=pd.Timestamp('now').strftime('%B-%d-%Y %I:%M %p')

# TO DO #####  Speciry file direcory #####
#Customize file name
filename = "Yahoo Finance_" + day + ".xlsx"
writer = pd.ExcelWriter(filename, engine='xlsxwriter')

# Convert the dataframe to an XlsxWriter Excel object; Customize Sheet name and table location
all_df_1.to_excel(writer, sheet_name=day,startrow=3,startcol=1,index=False,header=False)
all_df_2.to_excel(writer, sheet_name=day,startrow=3,startcol=3,index=False,header=False)

# Get the xlsxwriter workbook and worksheet objects.
workbook  = writer.book

# Pre-define formatting
bold = workbook.add_format({'bold': True})
cell_format = workbook.add_format()
cell_format.set_align('left')
# TO DO #####  Set the column width and format. #####


# Add date and time stamp
worksheet = writer.sheets[day]
worksheet.write('B1', stamp, bold)

# Add column names
worksheet.write('B3', 'Market Cap', bold)
worksheet.write('C3', 'Enterprise Value', bold)
worksheet.write('D3', 'Trailing P/E', bold)
worksheet.write('E3', 'Forward P/E 1', bold)
worksheet.write('F3', 'PEG Ratio (5 yr expected)', bold)
worksheet.write('G3', 'Price/Sales (ttm)', bold)
worksheet.write('H3', 'Price/Book (mrq)', bold)
worksheet.write('I3', 'Enterprise Value/Revenue', bold)
worksheet.write('J3', 'Enterprise Value/EBITDA', bold)

row_number=3
for ticker in tickers:
    row_number += 1
    cell='A'+str(row_number)
    worksheet.write(cell,ticker, bold)


writer.save()
