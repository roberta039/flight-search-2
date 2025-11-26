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
from data.airports import (
    get_continents, 
    get_countries_by_continent, 
    get_airports_by_country,
    search_airport,
    get_airport_name
)

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
    .airport-info {
        font-size: 12px;
        color: #666;
        font-style: italic;
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
if 'origin_iata' not in st.session_state:
    st.session_state.origin_iata = None
if 'destination_iata' not in st.session_state:
    st.session_state.destination_iata = None

def main():
    """Main application function"""
    
    st.title("✈️ Flight Search Engine")
    st.markdown("### Find the cheapest flights from multiple sources")
    
    # Sidebar for search parameters
    with st.sidebar:
        st.header("🔍 Search Parameters")
        
        # Tab pentru selecție mod
        selection_mode = st.radio(
            "Mod selectare aeroport:",
            ["📍 Selectare pe țări", "🔎 Căutare rapidă", "⌨️ Cod IATA manual"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # ORIGIN AIRPORT
        st.subheader("🛫 De unde pleci?")
        
        if selection_mode == "📍 Selectare pe țări":
            col1, col2 = st.columns(2)
            
            with col1:
                origin_continent = st.selectbox(
                    "Continent plecare",
                    [""] + get_continents(),
                    key="origin_continent"
                )
            
            if origin_continent:
                with col2:
                    origin_countries = get_countries_by_continent(origin_continent)
                    origin_country = st.selectbox(
                        "Țară plecare",
                        [""] + origin_countries,
                        key="origin_country"
                    )
                
                if origin_country:
                    origin_airports = get_airports_by_country(origin_continent, origin_country)
                    origin_airport = st.selectbox(
                        "Aeroport plecare",
                        [""] + list(origin_airports.keys()),
                        key="origin_airport"
                    )
                    
                    if origin_airport:
                        origin = origin_airports[origin_airport]
                        st.session_state.origin_iata = origin
                        st.markdown(f'<p class="airport-info">✈️ Cod IATA: {origin}</p>', 
                                  unsafe_allow_html=True)
                    else:
                        origin = None
                else:
                    origin = None
            else:
                origin = None
        
        elif selection_mode == "🔎 Căutare rapidă":
            search_query_origin = st.text_input(
                "Caută aeroport plecare",
                placeholder="ex: București, OTP, Heathrow...",
                key="search_origin"
            )
            
            if search_query_origin and len(search_query_origin) >= 2:
                results = search_airport(search_query_origin)
                
                if results:
                    origin_options = [
                        f"{r['airport']}, {r['country']} ({r['iata']})" 
                        for r in results
                    ]
                    selected_origin = st.selectbox(
                        "Selectează aeroportul",
                        origin_options,
                        key="origin_select"
                    )
                    
                    if selected_origin:
                        origin = selected_origin.split('(')[-1].strip(')')
                        st.session_state.origin_iata = origin
                    else:
                        origin = None
                else:
                    st.warning("Niciun aeroport găsit")
                    origin = None
            else:
                origin = None
        
        else:  # Manual IATA
            origin = st.text_input(
                "Cod IATA plecare",
                placeholder="ex: OTP",
                help="Cod aeroport de 3 litere"
            ).upper()
            st.session_state.origin_iata = origin if origin else None
        
        st.markdown("---")
        
        # DESTINATION AIRPORT
        st.subheader("🛬 Unde mergi?")
        
        if selection_mode == "📍 Selectare pe țări":
            col1, col2 = st.columns(2)
            
            with col1:
                dest_continent = st.selectbox(
                    "Continent destinație",
                    [""] + get_continents(),
                    key="dest_continent"
                )
            
            if dest_continent:
                with col2:
                    dest_countries = get_countries_by_continent(dest_continent)
                    dest_country = st.selectbox(
                        "Țară destinație",
                        [""] + dest_countries,
                        key="dest_country"
                    )
                
                if dest_country:
                    dest_airports = get_airports_by_country(dest_continent, dest_country)
                    dest_airport = st.selectbox(
                        "Aeroport destinație",
                        [""] + list(dest_airports.keys()),
                        key="dest_airport"
                    )
                    
                    if dest_airport:
                        destination = dest_airports[dest_airport]
                        st.session_state.destination_iata = destination
                        st.markdown(f'<p class="airport-info">✈️ Cod IATA: {destination}</p>', 
                                  unsafe_allow_html=True)
                    else:
                        destination = None
                else:
                    destination = None
            else:
                destination = None
        
        elif selection_mode == "🔎 Căutare rapidă":
            search_query_dest = st.text_input(
                "Caută aeroport destinație",
                placeholder="ex: London, LHR, Paris...",
                key="search_dest"
            )
            
            if search_query_dest and len(search_query_dest) >= 2:
                results = search_airport(search_query_dest)
                
                if results:
                    dest_options = [
                        f"{r['airport']}, {r['country']} ({r['iata']})" 
                        for r in results
                    ]
                    selected_dest = st.selectbox(
                        "Selectează aeroportul",
                        dest_options,
                        key="dest_select"
                    )
                    
                    if selected_dest:
                        destination = selected_dest.split('(')[-1].strip(')')
                        st.session_state.destination_iata = destination
                    else:
                        destination = None
                else:
                    st.warning("Niciun aeroport găsit")
                    destination = None
            else:
                destination = None
        
        else:  # Manual IATA
            destination = st.text_input(
                "Cod IATA destinație",
                placeholder="ex: LHR",
                help="Cod aeroport de 3 litere"
            ).upper()
            st.session_state.destination_iata = destination if destination else None
        
        st.markdown("---")
        
        # Dates
        col1, col2 = st.columns(2)
        with col1:
            departure_date = st.date_input(
                "📅 Plecare",
                min_value=datetime.now().date(),
                value=datetime.now().date() + timedelta(days=7)
            )
        
        with col2:
            trip_type = st.radio("Tip călătorie", ["Dus", "Dus-întors"])
            if trip_type == "Dus-întors":
                return_date = st.date_input(
                    "📅 Întoarcere",
                    min_value=departure_date + timedelta(days=1),
                    value=departure_date + timedelta(days=14)
                )
            else:
                return_date = None
        
        # Passengers and class
        adults = st.number_input("👥 Pasageri", min_value=1, max_value=9, value=1)
        
        cabin_class = st.selectbox(
            "🎫 Clasă",
            AppConfig.CABIN_CLASSES,
            format_func=lambda x: {
                'ECONOMY': '💺 Economy',
                'PREMIUM_ECONOMY': '💺+ Premium Economy',
                'BUSINESS': '💼 Business',
                'FIRST': '👑 First Class'
            }.get(x, x),
            index=0
        )
        
        # Additional filters
        st.markdown("---")
        st.subheader("🔧 Filtre")
        
        non_stop = st.checkbox("✈️ Doar zboruri directe", value=False)
        max_results = st.slider("📊 Rezultate maxime", 10, 100, 50)
        
        currency = st.selectbox(
            "💰 Monedă",
            ["EUR", "USD", "RON", "GBP"],
            format_func=lambda x: {
                'EUR': '€ EUR',
                'USD': '$ USD',
                'RON': 'RON',
                'GBP': '£ GBP'
            }.get(x, x),
            index=0
        )
        
        # Search button
        st.markdown("---")
        
        # Validare înainte de search
        can_search = origin and destination and origin != destination
        
        if not origin or not destination:
            st.warning("⚠️ Selectează aeroporturile")
        elif origin == destination:
            st.error("❌ Plecare și destinație trebuie să difere")
        
        search_button = st.button(
            "🔍 Caută Zboruri",
            type="primary",
            disabled=not can_search
        )
        
        # Auto-refresh settings
        st.markdown("---")
        st.subheader("⏰ Monitorizare Prețuri")
        
        enable_monitor = st.checkbox("🔄 Auto-refresh activ")
        
        if enable_monitor:
            refresh_interval = st.selectbox(
                "Refresh la fiecare",
                list(AppConfig.REFRESH_INTERVALS.keys())
            )
            st.session_state.auto_refresh = True
            st.session_state.refresh_interval = AppConfig.REFRESH_INTERVALS[refresh_interval]
        else:
            st.session_state.auto_refresh = False
        
        # Clear cache button
        if st.button("🗑️ Șterge Cache"):
            cache_manager.clear_cache()
            st.success("✅ Cache șters!")
    
    # Display route info in main area
    if origin and destination:
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            st.info(f"🛫 **Plecare:** {get_airport_name(origin)}")
        
        with col2:
            st.markdown("<div style='text-align: center; font-size: 24px;'>✈️</div>", 
                       unsafe_allow_html=True)
        
        with col3:
            st.info(f"🛬 **Destinație:** {get_airport_name(destination)}")
    
    # Main content area
    if search_button or st.session_state.auto_refresh:
        if not can_search:
            return
        
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
        
        with st.spinner('🔄 Căutăm cele mai bune zboruri...'):
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
                    'route': f"{get_airport_name(origin)} → {get_airport_name(destination)}",
                    'date': departure_date,
                    'key': route_key
                })
    
    # Display results
    if st.session_state.flights:
        display_results(st.session_state.flights)
    elif origin and destination:
        st.info("👆 Apasă butonul '🔍 Caută Zboruri' pentru a începe căutarea")
    
    # Auto-refresh logic
    if st.session_state.auto_refresh and st.session_state.flights:
        st.info(f"🔄 Auto-refresh activ. Următorul update în {st.session_state.refresh_interval} secunde")
        time.sleep(st.session_state.refresh_interval)
        st.rerun()


# Restul funcțiilor rămân la fel (display_results, display_table_view, etc.)
# ... (păstrezi toate funcțiile existente)
