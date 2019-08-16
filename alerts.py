from yahoofinancials import YahooFinancials
import datetime
import smtplib
import json



# Just want to watch some major worldwide indexes
mutual_funds = ['^GSPC', '^DJI', '^IXIC', '^FTSE', '^N100', '^FCHI', '^GDAXI', '^N225', '^TWII', '^HSI']
mutual_funds = YahooFinancials(mutual_funds)



# Define dates for the historical price data arguments
today = datetime.date.today()
endDate = (today - datetime.timedelta(weeks=1)).strftime('%Y-%m-%d')
startDate = (today - datetime.timedelta(weeks=52)).strftime('%Y-%m-%d')



# Actually call the YF functions
hist = mutual_funds.get_historical_price_data(startDate, endDate, "monthly")
curr = mutual_funds.get_current_price()



# Initialize empty list of alerts
alerts = []



# Loop through provided tickers to get Current price and High/Low range.
for ticker in curr:
  currentValue = curr[ticker]

  lows = []
  highs = []

  for price in hist[ticker]['prices']:
    if price['low'] is not None:
      lows.append(price['low'])
    if price['high'] is not None:
      highs.append(price['high'])

  lowest = min(lows)
  highest = max(highs)

  currentPct = (currentValue - lowest) / (highest - lowest)
  
  if currentPct <= .05:
    currentPct = "{:.2%}".format(currentPct)
    alerts.append(f"{ticker} is currently at {currentPct} of the 52 week range.")



# If any alerts were generated, send them out
if len(alerts) > 0:

  # Load settings from external file
  with open('settings.json', 'r') as settings_file:
    settings = json.load(settings_file)  
  
  server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
  server.ehlo()
  server.login(settings['user'], settings['pass'])

  for recipient in settings['recipients']:
  
    server.sendmail(settings['user'], recipient, ' '.join(alerts))
    
  server.close()
