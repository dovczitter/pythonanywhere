import pandas as pd
import json
import requests

# Local Ubuntu
import cloudscraper

class MostActiveStocks:

    def __init__(self):
        print('MostActiveStocks init')
        pass

    marketList = []
    version='6.00'
    hostName=''
    serverPort=0
    YahooMostActivesName='YahooMostActives'
    InvestingMostActivesName='InvestingMostActives'
    YahooMostActivesUrl='https://finance.yahoo.com/most-active'
    InvestingMostActivesUrl='https://www.investing.com/equities/most-active-stocks'

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
    def getData(url):
        htmlSrc = ''
        data = ''
        try:
            # --- NOTE : comment out accordingly
            
            # PythonAnywhere
            #htmlSrc = requests.get(url).text
            # Local Ubuntu
            scraper = cloudscraper.create_scraper(browser={'browser': 'firefox','platform': 'windows','mobile': False})
            htmlSrc = scraper.get(url).text

            df_list = pd.read_html(htmlSrc, flavor='html5lib')
            df = df_list[0]
            df.head()
        except Exception as e:
            return e, data

        jsonResult = df.to_json(orient="values")
        jsonParsed = json.loads(jsonResult)
        data = jsonParsed
        return htmlSrc, data
