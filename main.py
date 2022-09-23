import requests
import os

from twilio.rest import Client

import datetime


STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"


def get_data(day):
    url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=" + STOCK_NAME + "&apikey=" + os.getenv(
        'STOCK_KEY')

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    stocks = data["Time Series (Daily)"][str(day)]
    return str(float(stocks["4. close"])).format(".:2f")


def get_yesterday_price():
    day = datetime.date.today() - datetime.timedelta(days=1)
    print(day)
    yday_price = get_data(day)
    return float(yday_price)


def get_previous_day_price():
    day = datetime.date.today()-datetime.timedelta(days=2)
    pday_price = get_data(day)
    return float(pday_price)


def get_news(day):
    url = "https://newsapi.org/v2/everything?q="+COMPANY_NAME+"&from="+str(day)+"&sortBy=publishedAt&apiKey="+os.getenv("API_KEY")

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)
    news = response.json()["articles"][0:3]

    summary_news = [f"Headline: {x['title']}.\nBrief: {x['description']}" for x in news]
    return summary_news


def send_sms(message, phone):
    account_sid = os.getenv('ASID')
    auth_token = os.getenv('ATKN')
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=message,
        from_=os.getenv("ANUM"),
        to=phone
    )
    print(message.sid, message.status)


y_price = get_yesterday_price()
p_price = get_previous_day_price()

diff = abs(y_price - p_price)
display_diff = str(diff).format(".:2f")
print(f"The difference between {y_price} and {p_price} is {display_diff}")


percent = (diff / y_price) * 100
print(f"The corresponding percentage is {percent}")


day = datetime.date.today() - datetime.timedelta(days=1)
if percent > 1:
    summary = get_news(day)
    for item in summary:
        send_sms(item, '+233242182591')




#Optional TODO: Format the message like this: 
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""

