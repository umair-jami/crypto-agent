import requests
from agents import Agent, function_tool

@function_tool
def get_crypto_price(symbol: str) -> str:
    """Get current price of a cryptocurrency from Coinlore. Symbol examples: BTC, ETH."""
    try:
        # Step 1: Get all tickers to map symbol to ID
        all_coins_url = "https://api.coinlore.net/api/tickers/"
        response = requests.get(all_coins_url)
        tickers = response.json().get("data", [])

        # Step 2: Find coin ID by symbol
        coin = next((c for c in tickers if c["symbol"].upper() == symbol.upper()), None)
        if not coin:
            return f"Symbol '{symbol}' not found."

        coin_id = coin["id"]

        # Step 3: Fetch price by ID
        coin_url = f"https://api.coinlore.net/api/ticker/?id={coin_id}"
        coin_response = requests.get(coin_url)
        coin_data = coin_response.json()[0]  # it's a list

        return f"Current price of {symbol.upper()} is {coin_data['price_usd']} USD."

    except Exception as e:
        return f"Error: {str(e)}"
