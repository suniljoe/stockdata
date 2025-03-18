
import smtplib
import yfinance as yf
import schedule
import time
import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Email Configuration
SMTP_SERVER = "smtp.mail.yahoo.com"
SMTP_PORT = 587
EMAIL_SENDER = "abisunil@ymail.com"
EMAIL_PASSWORD = "omarwxneoqrgbodg"
EMAIL_RECEIVER = "suniljoe1990@gmail.com"

# Stocks to Track
STOCKS = ["AGX", "CLS", "CRDO", "DXPE", "EAT", "EXC", "EXEL", "INTA", "LRN", "NVDA", "OPFI", "PM", "PPC", "PYPL", "RTX", "URBN"]

# News API Configuration
NEWS_API_KEY = "1850243d5412420faeaaf737350b923a"
NEWS_URL = "https://newsapi.org/v2/top-headlines?category=business&language=en&apiKey=" + NEWS_API_KEY

def get_stock_data():
    """Fetches stock market data and returns a formatted digest with technical indicators."""
    digest = "📈 **Daily Stock Market Update** 📈\n\n"

    for stock in STOCKS:
        ticker = yf.Ticker(stock)
        data = ticker.history(period="1y")  # 1 year of data for SMA calculations

        if not data.empty:
            latest_price = data['Close'].iloc[-1]
            sma_50 = data['Close'].rolling(window=50).mean().iloc[-1]
            sma_200 = data['Close'].rolling(window=200).mean().iloc[-1]
            
            trend = "📉 Bearish" if sma_50 < sma_200 else "📈 Bullish"

            digest += f"**{stock}**: ${latest_price:.2f}\n"
            digest += f"50-Day SMA: ${sma_50:.2f}\n"
            digest += f"200-Day SMA: ${sma_200:.2f}\n"
            digest += f"Trend: {trend}\n\n"

    return digest

def get_market_news():
    """Fetches the latest stock market news headlines."""
    try:
        response = requests.get(NEWS_URL)
        news_data = response.json()

        if news_data["status"] == "ok":
            articles = news_data["articles"][:3]  # Get top 3 news articles
            news_digest = "📰 **Market News** 📰\n\n"

            for article in articles:
                news_digest += f"🔹 {article['title']}\n"
                news_digest += f"Read more: {article['url']}\n\n"

            return news_digest
    except Exception as e:
        return f"❌ Error fetching news: {e}\n\n"

def send_email():
    """Fetches stock data, market news, and sends it as an email."""
    stock_digest = get_stock_data()
    market_news = get_market_news()

    email_content = stock_digest + market_news

    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = "📊 Daily Stock Market Update"

    msg.attach(MIMEText(email_content, "plain"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        server.quit()
        print("✅ Daily stock market email sent successfully!")
    except Exception as e:
        print(f"❌ Error sending email: {e}")

# Schedule the email to be sent daily at 8:30 AM
schedule.every().day.at("07:30").do(send_email)

print("📩 Stock market email scheduler is running...")

while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute