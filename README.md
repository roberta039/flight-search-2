# ✈️ Flight Search Engine

A comprehensive flight search application that aggregates the cheapest flights from multiple APIs including Amadeus, RapidAPI, and AirLabs.

## Features

- 🔍 **Multi-API Search**: Searches across Amadeus, AerodataBox, and AirLabs
- 💰 **Price Comparison**: Finds and displays the cheapest flights
- 📊 **Data Visualization**: Interactive charts and analytics
- ⏰ **Auto-Refresh**: Monitor prices with automatic updates
- 📥 **Export Data**: Download results as CSV
- 🎯 **Advanced Filters**: Cabin class, non-stop flights, passenger count
- 🚀 **Fast Caching**: Intelligent caching to reduce API calls

## Deployment on Streamlit Cloud

### 1. Setup Secrets

Create `.streamlit/secrets.toml` in your repository (DON'T commit this):

```toml
[amadeus]
api_key = "X0GWDRRoNmn6ORcSkfhOBGjiR75s0PIo"
api_secret = "2sdyh8nvAi89w0iL"

[rapidapi]
key = "5a26e14d6amsheeb99b61b3ff65ep17583cjsn4eb17402fec4"

[airlabs]
api_key = "15151c68-6858-4cc2-a819-33b87bfc7651"
