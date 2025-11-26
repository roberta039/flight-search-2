"""Main Streamlit application for flight search."""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time
from services.flight_apis import FlightAggregator
from utils.helpers import FlightFormatter
from utils.validators import FlightValidator
from config.settings import AppConfig
from services.cache_manager import cache_manager

# Page configuration
st.set_page_config(
    page_title="✈️ Flight Search Engine",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
    }
    .price-tag {
        font-size: 24px;
        font-weight: bold;
        color: #FF4B4B;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'flights' not in st.session_state:
    st.session_state.flights = []
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = False
if 'monitor_routes' not in st.session_state:
    st.session_state.monitor_routes = []

def main():
    """Main application function"""
    
    st.title("✈️ Flight Search Engine")
    st.markdown("### Find the cheapest flights from multiple sources")
    
    # Sidebar for search parameters
    with st.sidebar:
        st.header("🔍 Search Parameters")
        
        # Origin and destination
        col1, col2 = st.columns(2)
        with col1:
            origin = st.text_input(
                "From (IATA)",
                placeholder="e.g., OTP",
                help="3-letter airport code"
            ).upper()
        
        with col2:
            destination = st.text_input(
                "To (IATA)",
                placeholder="e.g., LHR",
                help="3-letter airport code"
            ).upper()
        
        # Dates
        col1, col2 = st.columns(2)
        with col1:
            departure_date = st.date_input(
                "Departure",
                min_value=datetime.now().date(),
                value=datetime.now().date() + timedelta(days=7)
            )
        
        with col2:
            trip_type = st.radio("Trip type", ["One-way", "Round-trip"])
            if trip_type == "Round-trip":
                return_date = st.date_input(
                    "Return",
                    min_value=departure_date + timedelta(days=1),
                    value=departure_date + timedelta(days=14)
                )
            else:
                return_date = None
        
        # Passengers and class
        adults = st.number_input("Passengers", min_value=1, max_value=9, value=1)
        
        cabin_class = st.selectbox(
            "Cabin Class",
            AppConfig.CABIN_CLASSES,
            index=0
        )
        
        # Additional filters
        st.markdown("---")
        st.subheader("Filters")
        
        non_stop = st.checkbox("Non-stop flights only", value=False)
        max_results = st.slider("Max results", 10, 100, 50)
        
        currency = st.selectbox("Currency", ["EUR", "USD", "RON", "GBP"], index=0)
        
        # Search button
        st.markdown("---")
        search_button = st.button("🔍 Search Flights", type="primary")
        
        # Auto-refresh settings
        st.markdown("---")
        st.subheader("⏰ Price Monitor")
        
        enable_monitor = st.checkbox("Enable auto-refresh")
        
        if enable_monitor:
            refresh_interval = st.selectbox(
                "Refresh every",
                list(AppConfig.REFRESH_INTERVALS.keys())
            )
            st.session_state.auto_refresh = True
            st.session_state.refresh_interval = AppConfig.REFRESH_INTERVALS[refresh_interval]
        else:
            st.session_state.auto_refresh = False
        
        # Clear cache button
        if st.button("🗑️ Clear Cache"):
            cache_manager.clear_cache()
            st.success("Cache cleared!")
    
    # Main content area
    if search_button or st.session_state.auto_refresh:
        # Validate inputs
        validator = FlightValidator()
        
        valid_origin, origin_msg = validator.validate_iata_code(origin)
        valid_dest, dest_msg = validator.validate_iata_code(destination)
        valid_dep, dep_msg = validator.validate_date(datetime.combine(departure_date, datetime.min.time()))
        valid_passengers, pass_msg = validator.validate_passenger_count(adults)
        
        if not all([valid_origin, valid_dest, valid_dep, valid_passengers]):
            error_msgs = [msg for msg in [origin_msg, dest_msg, dep_msg, pass_msg] if msg]
            for msg in error_msgs:
                st.error(f"❌ {msg}")
            return
        
        if return_date:
            valid_dates, dates_msg = validator.validate_dates(
                datetime.combine(departure_date, datetime.min.time()),
                datetime.combine(return_date, datetime.min.time())
            )
            if not valid_dates:
                st.error(f"❌ {dates_msg}")
                return
        
        # Search flights
        aggregator = FlightAggregator()
        
        with st.spinner('🔄 Searching for the best flights...'):
            flights = aggregator.search_all(
                origin=origin,
                destination=destination,
                departure_date=departure_date.strftime('%Y-%m-%d'),
                return_date=return_date.strftime('%Y-%m-%d') if return_date else None,
                adults=adults,
                cabin_class=cabin_class,
                non_stop=non_stop,
                max_results=max_results
            )
        
        st.session_state.flights = flights
        
        # Add to monitor routes
        if enable_monitor:
            route_key = f"{origin}-{destination}-{departure_date}"
            if route_key not in st.session_state.monitor_routes:
                st.session_state.monitor_routes.append({
                    'route': f"{origin} → {destination}",
                    'date': departure_date,
                    'key': route_key
                })
    
    # Display results
    if st.session_state.flights:
        display_results(st.session_state.flights)
    
    # Auto-refresh logic
    if st.session_state.auto_refresh and st.session_state.flights:
        st.info(f"🔄 Auto-refresh enabled. Next update in {st.session_state.refresh_interval} seconds")
        time.sleep(st.session_state.refresh_interval)
        st.rerun()

def display_results(flights):
    """Display flight search results"""
    
    st.success(f"✅ Found {len(flights)} flights")
    
    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)
    
    if flights:
        prices = [f.get('price', 0) for f in flights if f.get('price')]
        
        with col1:
            st.metric("Cheapest Flight", f"€{min(prices):.2f}" if prices else "N/A")
        
        with col2:
            st.metric("Average Price", f"€{sum(prices)/len(prices):.2f}" if prices else "N/A")
        
        with col3:
            st.metric("Most Expensive", f"€{max(prices):.2f}" if prices else "N/A")
        
        with col4:
            direct_flights = len([f for f in flights if f.get('stops', 0) == 0])
            st.metric("Direct Flights", direct_flights)
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📋 Table View", "💰 Best Deals", "📊 Price Analysis"])
    
    with tab1:
        display_table_view(flights)
    
    with tab2:
        display_best_deals(flights)
    
    with tab3:
        display_price_analysis(flights)

def display_table_view(flights):
    """Display flights in table format"""
    
    formatter = FlightFormatter()
    df = formatter.flights_to_dataframe(flights)
    
    if df.empty:
        st.warning("No flights found")
        return
    
    # Select and reorder columns for display
    display_columns = [
        'airline', 'flight_number', 'origin', 'destination',
        'departure_time', 'arrival_time', 'duration', 'stops',
        'price', 'currency', 'cabin_class'
    ]
    
    available_columns = [col for col in display_columns if col in df.columns]
    df_display = df[available_columns]
    
    # Configure column settings
    column_config = {
        'price': st.column_config.NumberColumn(
            'Price',
            format="€%.2f"
        ),
        'stops': st.column_config.NumberColumn(
            'Stops',
            format="%d"
        )
    }
    
    st.dataframe(
        df_display,
        column_config=column_config,
        hide_index=True,
        use_container_width=True,
        height=600
    )
    
    # Download button
    csv = df_display.to_csv(index=False)
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f"flights_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

def display_best_deals(flights):
    """Display best flight deals"""
    
    formatter = FlightFormatter()
    cheapest = formatter.get_cheapest_flights(flights, 5)
    
    if not cheapest:
        st.warning("No flights available")
        return
    
    st.subheader("🏆 Top 5 Cheapest Flights")
    
    for i, flight in enumerate(cheapest, 1):
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            
            with col1:
                st.markdown(f"**{i}. {flight.get('airline', 'N/A')} - {flight.get('flight_number', 'N/A')}**")
                st.text(f"{flight.get('origin', 'N/A')} → {flight.get('destination', 'N/A')}")
            
            with col2:
                st.text(f"🛫 {FlightFormatter.format_datetime(flight.get('departure_time', 'N/A'))}")
                st.text(f"🛬 {FlightFormatter.format_datetime(flight.get('arrival_time', 'N/A'))}")
            
            with col3:
                st.text(f"⏱️ {FlightFormatter.format_duration(flight.get('duration', 'N/A'))}")
                stops = flight.get('stops', 0)
                st.text(f"🔄 {stops} stop(s)" if stops > 0 else "✈️ Direct")
            
            with col4:
                st.markdown(f"<div class='price-tag'>€{flight.get('price', 0):.2f}</div>", 
                          unsafe_allow_html=True)
            
            st.markdown("---")

def display_price_analysis(flights):
    """Display price analysis charts"""
    
    if not flights:
        st.warning("No data available for analysis")
        return
    
    import plotly.express as px
    import plotly.graph_objects as go
    
    df = FlightFormatter.flights_to_dataframe(flights)
    
    if df.empty or 'price' not in df.columns:
        st.warning("No price data available")
        return
    
    # Price distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 Price Distribution")
        fig = px.histogram(df, x='price', nbins=20, 
                          labels={'price': 'Price (EUR)', 'count': 'Number of Flights'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("✈️ Price by Airline")
        if 'airline' in df.columns:
            avg_price = df.groupby('airline')['price'].mean().sort_values()
            fig = px.bar(x=avg_price.values, y=avg_price.index, 
                        orientation='h',
                        labels={'x': 'Average Price (EUR)', 'y': 'Airline'})
            st.plotly_chart(fig, use_container_width=True)
    
    # Price vs Stops
    if 'stops' in df.columns:
        st.subheader("🔄 Price vs Number of Stops")
        fig = px.box(df, x='stops', y='price',
                    labels={'stops': 'Number of Stops', 'price': 'Price (EUR)'})
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
