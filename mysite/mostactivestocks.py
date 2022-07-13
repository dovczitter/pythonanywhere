import pandas as pd
import json
import requests
import os
import cloudscraper

class MostActiveStocks:

    def __init__(self):
#        print('MostActiveStocks init')
        pass

    version='7.00'
    hostName=''
    serverPort=0
    headerLength=0

    MostActivesNameYahoo = 'YahooMostActives'
    MostActivesNameInvesting = 'InvestingMostActives'

    #
    # ================ classmethods ================
    #

    # ------------------------------------------------------------------------
    #                       configInit
    # ------------------------------------------------------------------------
    @classmethod
    def configInit(self):
        self.hostName=''
        self.serverPort=0
        with open('webserver.json') as f:
            data = json.load(f)
        if data.get('hostName'):
            self.hostName=data['hostName']
        if data.get('serverPort'):
            self.serverPort=data['serverPort']
        return

    #
    # ================ static methods ================
    #

    # ------------------------------------------------------------------------
    #                       getYahooHref
    # ------------------------------------------------------------------------
    @staticmethod
    def getYahooHref(symbol, htmlSrc):
        href = f'https://finance.yahoo.com/quote/{symbol}?p={symbol}'
        return href

    # ------------------------------------------------------------------------
    #                       getInvestingHref
    # ------------------------------------------------------------------------
    @staticmethod
    def getInvestingHref(symbol, htmlSrc):
        href = ''
        startPos = -1
        endPos = -1
        endPos = htmlSrc.find(f"'>{symbol}</a><span class")
        if endPos > 0:
            begStr = "href='/equities/" 
            startPos = htmlSrc.rindex(begStr, 0, endPos)
        if startPos >= 0:
            startPos = startPos + len(begStr)
        if startPos >= 0 and endPos >= 0 and startPos <= endPos:
            investSymbol = htmlSrc[startPos:endPos].strip()
            href = f'https://www.investing.com/equities/{investSymbol}'
        return href

    # ------------------------------------------------------------------------
    #                       getData
    # ------------------------------------------------------------------------
    @staticmethod
    def getData(market):
        url = MostActiveStocks.getUrl(market)
        htmlSrc = ''
        data = ''
        try:
            scraper = cloudscraper.create_scraper(browser={'browser': 'firefox','platform': 'windows','mobile': False})
            htmlSrc = scraper.get(url).text
            if '<?xml version=' in htmlSrc:
                xmlSrc = requests.get(url).text
                jsonResult = json.dumps(xmlSrc)
                jsonParsed = json.loads( jsonResult )
                data = jsonParsed
            else:
                df_list = pd.read_html(htmlSrc, flavor='html5lib')
                df = df_list[0]
                df.head()
                jsonResult = df.to_json(orient="values")
                jsonParsed = json.loads(jsonResult)
#                print(jsonParsed)
                data = jsonParsed
        except Exception as e:
            return e, data

        return htmlSrc, data

    # ------------------------------------------------------------------------
    #                       parseUrl
    # ------------------------------------------------------------------------
    @staticmethod
    def parseUrl(market, headerTag):
        url = MostActiveStocks.getUrl(market)
        htmlSrc = ''
        data = ''
        foundTag = False
        tables = pd.read_html(url)
        tables_len = len(tables)
        for i in range(tables_len):
            df = tables[i]
            jsonResult = df.to_json(orient="values")
            jsonParsed = json.loads(jsonResult)
            if foundTag:
                data = jsonParsed
                break
            tstr = str(df)
            if tstr.find(headerTag) != -1: 
                foundTag = True
                continue

        return htmlSrc, data
 
    # ------------------------------------------------------------------------
    #                       getHeading
    # ------------------------------------------------------------------------
    @staticmethod
    def getHeading(market):

        headings = []
        mas_dict = {}
        fx_dict = {}

        if market != '':
            try:
                fn = f'{os.getcwd()}/MostActiveStocks.csv'
                mas_dict = pd.read_csv(fn).to_dict('records')

                fn = f'{os.getcwd()}/ForeignExchangeRates.csv'
                fx_dict = pd.read_csv(fn).to_dict('records')
            except Exception as e:
                return f'csv file read error: {e}'

            for row in mas_dict:
                if row['Name'] == market:
                    for index, (key, value) in enumerate(row.items()):
                        if (index > 1):
                            if not pd.isnull(value):
                                headings.append(value)
                    break
            if len(headings) == 0:
                for row in fx_dict:
                    if row['Name'] == market:
                        for index, (key, value) in enumerate(row.items()):
                            if (index > 1):
                                if not pd.isnull(value):
                                    headings.append(value)
                        break
                    
        MostActiveStocks.headerLength = len(headings)
        return headings
  
    # ------------------------------------------------------------------------
    #                       getHrefs
    # ------------------------------------------------------------------------
    @staticmethod
    def getHrefs(url):

        MostActiveStocksHrefs = {}
        CurrencyHrefs = {}
        mas_dict = {}
        cur_dict = {}

        try:
            fn = f'{os.getcwd()}/MostActiveStocks.csv'
            df = pd.read_csv(fn)
            mas_dict = df.to_dict('records')

            fn = f'{os.getcwd()}/ForeignExchangeRates.csv'
            df = pd.read_csv(fn)
            cur_dict = df.to_dict('records')
        except Exception as e:
            return f'csv file read error: {e}'

        for row in mas_dict:
            name = row['Name']
            if name[0] != '#':
                MostActiveStocksHrefs[name] = f'{url}/mostactivestocks?market={name}'

        for row in cur_dict:
            name = row['Name']
            if name[0] != '#':
                CurrencyHrefs[name] = f'{url}/mostactivestocks?market={name}'

        return MostActiveStocksHrefs,CurrencyHrefs

    # ------------------------------------------------------------------------
    #                       getTableHead
    # ------------------------------------------------------------------------
    @staticmethod
    def getTableHead(market):

        tableHead = '<tr>'
        headings = MostActiveStocks.getHeading(market)
        for index,header in enumerate(headings):
            tableHead += f'<th>{ header }</th>'
        tableHead += '</tr>'
        
        return tableHead

    # ------------------------------------------------------------------------
    #                       getMostActiveUrl
    # ------------------------------------------------------------------------
    @staticmethod
    def getMostActiveUrl(market):

        url = ''
        mas_dict = {}

        try:
            fn = f'{os.getcwd()}/MostActiveStocks.csv'
            mas_dict = pd.read_csv(fn).to_dict('records')
        except Exception as e:
            return f'csv file read error: {e}'

        for row in mas_dict:
            if row['Name'] == market:
                url = row['Url']
                break

        return url

    # ------------------------------------------------------------------------
    #                       getCurrencyUrl
    # ------------------------------------------------------------------------
    @staticmethod
    def getCurrencyUrl(market):

        url = ''
        cur_dict = {}

        try:
            fn = f'{os.getcwd()}/ForeignExchangeRates.csv'
            cur_dict = pd.read_csv(fn).to_dict('records')
        except Exception as e:
            return f'csv file read error: {e}'

        for row in cur_dict:
            if row['Name'] == market:
                url = row['Url']
                break

        return url

    # ------------------------------------------------------------------------
    #                       getUrl
    # ------------------------------------------------------------------------
    @staticmethod
    def getUrl(market):

        url = MostActiveStocks.getMostActiveUrl(market)
        if url == '':
            url = MostActiveStocks.getCurrencyUrl(market)
        return url
