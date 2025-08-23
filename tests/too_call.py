from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_groq.chat_models import ChatGroq
from pydantic import SecretStr
from langchain_core.messages import HumanMessage
import random
from datetime import datetime, timedelta

# Initialize the LLM
llm = ChatGroq(
    api_key=SecretStr("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"),
    model="openai/gpt-oss-120b"
)

@tool
def get_weather_condition(city: str) -> str:
    """Get current weather condition for a specific city. Returns weather status."""
    # Simulate weather API call
    weather_conditions = ["sunny", "rainy", "cloudy", "stormy", "foggy"]
    condition = random.choice(weather_conditions)
    temperature = random.randint(15, 35)
    return f"Weather in {city}: {condition}, {temperature}°C"

@tool
def check_flight_delay_risk(weather_condition: str) -> str:
    """Check if weather condition poses flight delay risk. Input should be weather condition like 'stormy', 'sunny', etc."""
    high_risk = ["stormy", "foggy", "heavy_rain"]
    medium_risk = ["rainy", "cloudy"]
    low_risk = ["sunny", "clear"]
    
    condition_lower = weather_condition.lower()
    
    if any(risk in condition_lower for risk in high_risk):
        return f"HIGH RISK: {weather_condition} weather typically causes significant flight delays (60-90% chance)"
    elif any(risk in condition_lower for risk in medium_risk):
        return f"MEDIUM RISK: {weather_condition} weather may cause minor flight delays (20-40% chance)"
    else:
        return f"LOW RISK: {weather_condition} weather rarely causes flight delays (5-15% chance)"

@tool
def get_alternative_airports(city: str) -> str:
    """Get alternative airports near a city in case of delays."""
    # Simulate airport database
    airport_alternatives = {
        "new york": ["JFK", "LaGuardia", "Newark"],
        "london": ["Heathrow", "Gatwick", "Stansted", "Luton"],
        "tokyo": ["Haneda", "Narita"],
        "paris": ["Charles de Gaulle", "Orly"],
        "mumbai": ["Chhatrapati Shivaji", "Pune Airport (backup)"]
    }
    
    city_lower = city.lower()
    for key, airports in airport_alternatives.items():
        if key in city_lower:
            return f"Alternative airports near {city}: {', '.join(airports)}"
    
    return f"Alternative airports near {city}: Main airport + 2-3 regional alternatives available"

@tool
def get_travel_recommendation(risk_level: str, alternatives: str) -> str:
    """Provide travel recommendation based on delay risk and alternatives."""
    if "HIGH RISK" in risk_level:
        return "RECOMMENDATION: Consider postponing travel or book with major airlines that offer better rebooking options. Have backup plans ready."
    elif "MEDIUM RISK" in risk_level:
        return "RECOMMENDATION: Allow extra time for potential delays. Consider travel insurance. Monitor flight status closely."
    else:
        return "RECOMMENDATION: Good conditions for travel. Standard precautions apply."

# Create the agent
agent = create_react_agent(
    model=llm,
    tools=[get_weather_condition, check_flight_delay_risk, get_alternative_airports, get_travel_recommendation]
)

# Test query that requires multiple tool calls
query = """I'm planning to fly from Mumbai tomorrow. Can you check the weather conditions, 
assess flight delay risks, find alternative airports if needed, and give me a travel recommendation?"""

print("=" * 60)
print("QUERY:", query)
print("=" * 60)

output = agent.invoke({"messages": [HumanMessage(content=query)]})

print("\nFINAL OUTPUT:")
print(output)
# print("=" * 60)
# for message in output['messages']:
#     if hasattr(message, 'content') and message.content:
#         print(f"{message.__class__.__name__}: {message.content}")
#         print("-" * 40)

# # Another example - cryptocurrency analysis
# print("\n\n" + "=" * 80)
# print("SECOND EXAMPLE - Crypto Analysis")
# print("=" * 80)

# @tool
# def get_crypto_price(symbol: str) -> str:
#     """Get current cryptocurrency price. Use symbols like BTC, ETH, etc."""
#     # Simulate crypto API
#     prices = {"BTC": 45000, "ETH": 2800, "ADA": 0.45, "DOT": 7.2}
#     price = prices.get(symbol.upper(), random.randint(1, 100))
#     change = random.uniform(-5.0, 5.0)
#     return f"{symbol.upper()} current price: ${price:,} (24h change: {change:+.2f}%)"

# @tool
# def get_trading_volume(symbol: str) -> str:
#     """Get 24h trading volume for cryptocurrency."""
#     volume = random.randint(1000000, 50000000)
#     return f"{symbol.upper()} 24h trading volume: ${volume:,}"

# @tool
# def calculate_risk_score(price_change: float, volume: int) -> str:
#     """Calculate investment risk score based on price change and volume."""
#     risk_score = abs(price_change) * 10 + (1000000 / volume) * 100
    
#     if risk_score > 80:
#         return f"Risk Score: {risk_score:.1f} - HIGH RISK (Volatile with low liquidity)"
#     elif risk_score > 40:
#         return f"Risk Score: {risk_score:.1f} - MEDIUM RISK (Moderate volatility)"
#     else:
#         return f"Risk Score: {risk_score:.1f} - LOW RISK (Stable with good liquidity)"

# # Add crypto tools to agent
# crypto_agent = create_react_agent(
#     model=llm,
#     tools=[get_crypto_price, get_trading_volume, calculate_risk_score]
# )

# crypto_query = "Analyze Bitcoin (BTC) and Ethereum (ETH). Get their prices, trading volumes, and calculate risk scores for both."

# print("CRYPTO QUERY:", crypto_query)
# print("=" * 60)

# crypto_output = crypto_agent.invoke({"messages": [HumanMessage(content=crypto_query)]})

# print("\nCRYPTO ANALYSIS OUTPUT:")
# print("=" * 60)
# for message in crypto_output['messages']:
#     if hasattr(message, 'content') and message.content:
#         print(f"{message.__class__.__name__}: {message.content}")
#         print("-" * 40)