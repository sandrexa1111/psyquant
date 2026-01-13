import alpaca_trade_api as tradeapi

API_KEY = "PK25PZNE7TLOF2RSL22IQKFWRP"
API_SECRET = "mMDSiFN6p5hEfTGbdNh5Ye9eCrsjbjJc9WjMdibWz2J"
BASE_URL = "https://paper-api.alpaca.markets"

api = tradeapi.REST(API_KEY, API_SECRET, BASE_URL, api_version="v2")

account = api.get_account()

print("✅ Connected!")
print("Account status:", account.status)
print("Buying power:", account.buying_power)
