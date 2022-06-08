from flask import Flask, render_template, request, send_from_directory
import pytz, time
from datetime import datetime
from mostactivestocks import MostActiveStocks
import os

app = Flask(__name__)

# ============================================
# Required for requestResume() call in home.html.

app.config['UPLOAD_FOLDER'] = os.getcwd()

try:
    os.makedirs(app.config['UPLOAD_FOLDER'])
except:
    pass

def get_files(target):
    for file in os.listdir(target):
        path = os.path.join(target, file)
        if os.path.isfile(path):
            yield (
                file,
                datetime.utcfromtimestamp(os.path.getmtime(path)),
                os.path.getsize(path)
            )
@app.route('/download/<path:filename>')
def download(filename):
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename,
        as_attachment=True
    )
# ============================================

@app.route('/')
@app.route('/mostactivestocks')
def handle_home():
    url = request.url
    args = url.split("=")
    market = args[1] if len(args) > 1 else ''
    htmlSrc = ''
    info = {}
    dtLocal = datetime.now().strftime("%d%b%Y:%H:%M:%S") + ' ' +  time.localtime().tm_zone
    tzNY = pytz.timezone('America/New_York')
    dtNY = datetime.now(tzNY).strftime("%d%b%Y:%H:%M:%S %Z")
    yhaooHref = ''
    investingHref = ''

    if market == MostActiveStocks.YahooMostActivesName:
        # --- Yahoo page ---
        htmlSrc, data = MostActiveStocks.getData(MostActiveStocks.YahooMostActivesUrl)
        headings = ( 'Symbol', 'Name', 'Price', 'Change', '%-Change', 'Volume', '3-Month-AvgVol', 'Monthly-Cap', 'PE-Ratio(TTM)' )
        return render_template('data.html', market=market, headings=headings, data=data, htmlSrc=htmlSrc, dtNY=dtNY, MostActiveStocks=MostActiveStocks())

    elif market == MostActiveStocks.InvestingMostActivesName:
        # --- Investing page ---
        htmlSrc, data = MostActiveStocks.getData(MostActiveStocks.InvestingMostActivesUrl)
        headings = ( 'Name', 'Last', 'High', 'Low', 'Chg', 'Chg %', 'Vol', 'Time' )
        return render_template('data.html', market=market, headings=headings, data=data, htmlSrc=htmlSrc,  dtNY=dtNY, MostActiveStocks=MostActiveStocks())

    else:
        # --- HOME page ---
        yhaooHref = f'{request.url}/mostactivestocks?market={MostActiveStocks.YahooMostActivesName}'
        investingHref = f'{request.url}/mostactivestocks?market={MostActiveStocks.InvestingMostActivesName}'
        if 'pythonanywhere' in url:
            yhaooHref = f'{request.url}?market={MostActiveStocks.YahooMostActivesName}'
            investingHref = f'{request.url}?market={MostActiveStocks.InvestingMostActivesName}'
        info = {
            'homePath' : url,
            'YahooHref' : yhaooHref,
            'InvestingHref' : investingHref,
            'dtLocal' : dtLocal,
            'dtNY' : dtNY,
        }
        return render_template('home.html', info=info, MostActiveStocks=MostActiveStocks())
