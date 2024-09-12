import logging
logging.basicConfig(filename='app.log', level=logging.ERROR)
import streamlit as st
import pandas as pd
import seaborn as sns
import numpy as np
import math
from scipy.stats import norm
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
cmap=LinearSegmentedColormap.from_list('rg',["r", "w", "g"], N=256)



# Create main header
st.header("Welcome to the Options Price Calculator")

# Create Input Fields For Stock Information

with st.sidebar:
    st.subheader("Options Price Visualizer 📈 ")
    st.text("Created By: Nathaniel Yee ")
    st.subheader("Pricing Requirements")

    cp = st.number_input("Current Price",value=100.0)
    strike = st.number_input("Select the Strike Price", min_value =.001,value=100.0)
    expiry = st.number_input("Time to maturity (Years)",value=1.00)
    vol = st.number_input("Volatility (σ) % ?", min_value=0.00, max_value=1.00, value=0.10)
    risk_free = st.number_input("Risk Free Rate % ?", min_value=0.00, max_value=1.00, value=0.05)
    start = st.date_input('Start', value=pd.to_datetime('today'))
    end = st.date_input('End', value=pd.to_datetime('today'))


# Create scenario analysis
    st.subheader("Scenario Analysis")
    min_spot = st.number_input("Minimum Spot Price $ ?", min_value=0.00, value=95.00)
    max_spot = st.number_input("Maximum Spot Price $ ?", min_value=0.00, value=100.00)
    min_vol = st.slider("Min Volatility",min_value=0.00, max_value=1.00, value=0.05)
    max_vol = st.slider("Max Volatility",min_value=0.00, max_value=1.00, value=0.10)


df = st.write(pd.DataFrame({
        'Current Price': [cp],
        'Expiry (Years)': [expiry],
        'Strike Price': [strike],
        'Risk-Free Rate': [risk_free],
        'Volatility': [vol],
    }))




# Variables For Calculating Prices
S = cp # price of option at time t aka current price

rf = float(risk_free) # rf risk free rate (assuming t-bill rate)
k = strike # strike price
t = expiry # time to maturity in years
volatility = vol # impl vol %



# Create Calculator Element Using Black Scholes
st.header("Pricing Results")
# Calculate Call Price
def bsm(S,k,vol,t,rf):
    d1 = math.log(S/k) + ((rf+vol**2/2)*t)**(1/2) # Take first half of black scholes
    d2 = d1 - vol*t**(1/2) # Second half of black scholes equation
    cs = round((S*norm.cdf(d1,0,1) - k * math.exp(-rf)*norm.cdf(d2,0,1)),2) # final step of normalizing the distribution to derive price and mult by 100
    p = round((k * math.exp(-rf * t) * norm.cdf(-d2) - S * norm.cdf(-d1)), 2) # create put prices
    call_price = f'${cs}'
    put_price = f'${p}'
    return call_price, put_price

# Calculate Put Price

 # put equation assumes normally distributed and mult by 100 for total contract price

st.markdown(f"""
    <div style="display: flex; justify-content: space-around;">
        <div style="background-color: green; padding: 20px; border-radius: 5px; color: white; text-align: center;">
            <h3>CALL Value</h3>
            <p>{bsm(S,k,vol,t,rf)[0]}</p>
        </div>
        <div style="background-color: #e6382c; padding: 20px; border-radius: 5px; color: white; text-align: center;">
            <h3>PUT Value</h3>
            <p>{bsm(S,k,vol,t,rf)[1]}</p>
        </div>
    </div>
""", unsafe_allow_html=True)
# Create Heatmap Visualization
st.subheader("Heatmap Visualization")


# Create heatmap viz data ranges
spot_prices = np.linspace(start=min_spot,stop=max_spot,num=10)
volatilities = np.linspace(start =min_vol,stop=max_vol,num=10)

call_prices = np.zeros((len(volatilities), len(spot_prices)))
put_prices = np.zeros((len(volatilities), len(spot_prices)))

for i, vol in enumerate(volatilities):
    for j, spot in enumerate(spot_prices):
        call_price, put_price = bsm(spot, k, vol, t, rf)
        call_prices[i, j] = float(call_price.replace('$', ''))  # Store call price in the matrix
        put_prices[i, j] = float(put_price.replace('$', ''))

# Plot the heatmap for Call prices
col1,col2 = st.columns(2)
with col1:
    st.subheader("Call Price Heatmap")
    fig, ax = plt.subplots()
    sns.heatmap(call_prices, xticklabels=np.round(spot_prices, 2), yticklabels=np.round(volatilities, 2), cmap=cmap, ax=ax,annot=True)
    ax.set_xlabel('Spot Price')
    ax.set_ylabel('Volatility')
    st.pyplot(fig)

with col2:
    # Plot the heatmap for Put prices
    st.subheader("Put Price Heatmap")
    fig, ax = plt.subplots()
    sns.heatmap(put_prices, xticklabels=np.round(spot_prices, 2), yticklabels=np.round(volatilities, 2), cmap=cmap, ax=ax,annot=True)
    ax.set_xlabel('Spot Price')
    ax.set_ylabel('Volatility')
    st.pyplot(fig)