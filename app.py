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
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #FF6B6B;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
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
        margin-top: -10px;
    }
    .route-display {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
        font-size: 18px;
        font-weight: bold;
    }
    .filter-badge {
        background-color: #4CAF50;
        color: white;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 12px;
        margin: 5px;
        display: inline-block;
    }
    .stats-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
    
    # Header
    st.title("✈️ Flight Search Engine")
    st.markdown("### 🌍 Găsește cele mai ieftine zboruri din toată lumea")
    
    # Sidebar for search parameters
    with st.sidebar:
        st.header("🔍 Parametrii de Căutare")
        
        # Selection mode tabs
        st.markdown("### Mod Selectare Aeroport")
        selection_mode = st.radio(
            "Alege modul de selectare:",
            ["📍 Continent → Țară → Aeroport", "🔎 Căutare Rapidă", "⌨️ Cod IATA Manual"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # ============== ORIGIN AIRPORT ==============
        st.markdown("### 🛫 De unde pleci?")
        
        origin = None
        
        if selection_mode == "📍 Continent → Țară → Aeroport":
            # Origin selection
            origin_continent = st.selectbox(
                "📍 Selectează Continentul (Plecare)",
                [""] + get_continents(),
                key="origin_continent",
                help="Selectează continentul de plecare"
            )
            
            if origin_continent:
                origin_countries = get_countries_by_continent(origin_continent)
                origin_country = st.selectbox(
                    "🌎 Selectează Țara (Plecare)",
                    [""] + origin_countries,
                    key="origin_country",
                    help="Selectează țara de plecare"
                )
                
                if origin_country:
                    origin_airports = get_airports_by_country(origin_continent, origin_country)
                    origin_airport = st.selectbox(
                        "✈️ Selectează Aeroportul (Plecare)",
                        [""] + list(origin_airports.keys()),
                        key="origin_airport",
                        help="Selectează aeroportul de plecare"
                    )
                    
                    if origin_airport:
                        origin = origin_airports[origin_airport]
                        st.session_state.origin_iata = origin
                        st.success(f"✅ Selectat: **{origin_airport}** `({origin})`")
        
        elif selection_mode == "🔎 Căutare Rapidă":
            # Origin search
            search_query_origin = st.text_input(
                "🔍 Caută Aeroport Plecare",
                placeholder="Ex: București, OTP, Otopeni, London...",
                key="search_origin",
                help="Caută după oraș, țară sau cod IATA"
            )
            
            if search_query_origin and len(search_query_origin) >= 2:
                results = search_airport(search_query_origin)
                
                if results:
                    origin_options = {
                        f"{r['airport']}, {r['country']} ({r['iata']})": r['iata']
                        for r in results[:15]  # Limit to 15 results
                    }
                    
                    selected_origin_display = st.selectbox(
                        "Selectează din rezultate:",
                        [""] + list(origin_options.keys()),
                        key="origin_select"
                    )
                    
                    if selected_origin_display:
                        origin = origin_options[selected_origin_display]
                        st.session_state.origin_iata = origin
                        st.success(f"✅ Selectat: **{selected_origin_display}**")
                else:
                    st.warning("⚠️ Niciun aeroport găsit. Încearcă alt termen de căutare.")
        
        else:  # Manual IATA
            origin = st.text_input(
                "⌨️ Introdu Cod IATA Plecare",
                placeholder="Ex: OTP",
                help="Cod IATA de 3 litere (ex: OTP pentru București)",
                max_chars=3,
                key="manual_origin"
            ).upper()
            
            if origin and len(origin) == 3:
                st.session_state.origin_iata = origin
                airport_name = get_airport_name(origin)
                if airport_name != origin:
                    st.success(f"✅ {airport_name}")
                else:
                    st.info(f"ℹ️ Cod: {origin}")
        
        st.markdown("---")
        
        # ============== DESTINATION AIRPORT ==============
        st.markdown("### 🛬 Unde mergi?")
        
        destination = None
        
        if selection_mode == "📍 Continent → Țară → Aeroport":
            # Destination selection
            dest_continent = st.selectbox(
                "📍 Selectează Continentul (Destinație)",
                [""] + get_continents(),
                key="dest_continent",
                help="Selectează continentul de destinație"
            )
            
            if dest_continent:
                dest_countries = get_countries_by_continent(dest_continent)
                dest_country = st.selectbox(
                    "🌎 Selectează Țara (Destinație)",
                    [""] + dest_countries,
                    key="dest_country",
                    help="Selectează țara de destinație"
                )
                
                if dest_country:
                    dest_airports = get_airports_by_country(dest_continent, dest_country)
                    dest_airport = st.selectbox(
                        "✈️ Selectează Aeroportul (Destinație)",
                        [""] + list(dest_airports.keys()),
                        key="dest_airport",
                        help="Selectează aeroportul de destinație"
                    )
                    
                    if dest_airport:
                        destination = dest_airports[dest_airport]
                        st.session_state.destination_iata = destination
                        st.success(f"✅ Selectat: **{dest_airport}** `({destination})`")
        
        elif selection_mode == "🔎 Căutare Rapidă":
            # Destination search
            search_query_dest = st.text_input(
                "🔍 Caută Aeroport Destinație",
                placeholder="Ex: Paris, CDG, London, Dubai...",
                key="search_dest",
                help="Caută după oraș, țară sau cod IATA"
            )
            
            if search_query_dest and len(search_query_dest) >= 2:
                results = search_airport(search_query_dest)
                
                if results:
                    dest_options = {
                        f"{r['airport']}, {r['country']} ({r['iata']})": r['iata']
                        for r in results[:15]
                    }
                    
                    selected_dest_display = st.selectbox(
                        "Selectează din rezultate:",
                        [""] + list(dest_options.keys()),
                        key="dest_select"
                    )
                    
                    if selected_dest_display:
                        destination = dest_options[selected_dest_display]
                        st.session_state.destination_iata = destination
                        st.success(f"✅ Selectat: **{selected_dest_display}**")
                else:
                    st.warning("⚠️ Niciun aeroport găsit. Încearcă alt termen de căutare.")
        
        else:  # Manual IATA
            destination = st.text_input(
                "⌨️ Introdu Cod IATA Destinație",
                placeholder="Ex: LHR",
                help="Cod IATA de 3 litere (ex: LHR pentru London Heathrow)",
                max_chars=3,
                key="manual_dest"
            ).upper()
            
            if destination and len(destination) == 3:
                st.session_state.destination_iata = destination
                airport_name = get_airport_name(destination)
                if airport_name != destination:
                    st.success(f"✅ {airport_name}")
                else:
                    st.info(f"ℹ️ Cod: {destination}")
        
        st.markdown("---")
        
        # ============== DATES ==============
        st.markdown("### 📅 Când călătorești?")
        
        col1, col2 = st.columns(2)
        
        with col1:
            departure_date = st.date_input(
                "🛫 Data Plecare",
                min_value=datetime.now().date(),
                value=datetime.now().date() + timedelta(days=7),
                help="Selectează data de plecare"
            )
        
        with col2:
            trip_type = st.radio(
                "Tip Călătorie",
                ["🔄 Dus-întors", "➡️ Doar Dus"],
                help="Selectează tipul călătoriei"
            )
        
        if trip_type == "🔄 Dus-întors":
            return_date = st.date_input(
                "🛬 Data Întoarcere",
                min_value=departure_date + timedelta(days=1),
                value=departure_date + timedelta(days=14),
                help="Selectează data de întoarcere"
            )
        else:
            return_date = None
        
        st.markdown("---")
        
        # ============== PASSENGERS & CLASS ==============
        st.markdown("### 👥 Pasageri și Clasă")
        
        adults = st.number_input(
            "👤 Număr Pasageri",
            min_value=1,
            max_value=9,
            value=1,
            help="Selectează numărul de pasageri (max 9)"
        )
        
        cabin_class = st.selectbox(
            "🎫 Clasa de Zbor",
            AppConfig.CABIN_CLASSES,
            format_func=lambda x: {
                'ECONOMY': '💺 Economy',
                'PREMIUM_ECONOMY': '💺+ Premium Economy',
                'BUSINESS': '💼 Business',
                'FIRST': '👑 First Class'
            }.get(x, x),
            index=0,
            help="Selectează clasa de zbor dorită"
        )
        
        st.markdown("---")
        
        # ============== FILTERS ==============
        st.markdown("### 🔧 Filtre Avansate")
        
        # BUTON ZBORURI DIRECTE - CU EVIDENȚIERE
        non_stop = st.checkbox(
            "✈️ **DOAR ZBORURI DIRECTE (fără escală)**",
            value=False,
            help="Bifează pentru a vedea DOAR zboruri directe, fără escală"
        )
        
        if non_stop:
            st.success("✅ **Filtru activ**: Doar zboruri directe!")
        
        max_results = st.slider(
            "📊 Număr Maxim de Rezultate",
            min_value=10,
            max_value=100,
            value=50,
            step=10,
            help="Câte rezultate să afișeze"
        )
        
        currency = st.selectbox(
            "💰 Monedă Preferată",
            ["EUR", "USD", "RON", "GBP"],
            format_func=lambda x: {
                'EUR': '€ EUR (Euro)',
                'USD': '$ USD (Dolar American)',
                'RON': 'RON (Leu Românesc)',
                'GBP': '£ GBP (Liră Sterlină)'
            }.get(x, x),
            index=0,
            help="Selectează moneda în care să fie afișate prețurile"
        )
        
        st.markdown("---")
        
        # ============== SEARCH BUTTON ==============
        can_search = origin and destination and origin != destination
        
        if not origin or not destination:
            st.warning("⚠️ **Selectează ambele aeroporturi pentru a căuta**")
        elif origin == destination:
            st.error("❌ **Aeroportul de plecare trebuie să difere de cel de destinație**")
        
        st.markdown("### 🚀 Pornește Căutarea")
        
        search_button = st.button(
            "🔍 CAUTĂ ZBORURI",
            type="primary",
            disabled=not can_search,
            help="Click pentru a căuta zborurile disponibile",
            use_container_width=True
        )
        
        st.markdown("---")
        
        # ============== PRICE MONITORING ==============
        st.markdown("### ⏰ Monitorizare Prețuri")
        
        enable_monitor = st.checkbox(
            "🔄 Activează Auto-Refresh",
            help="Actualizează automat rezultatele la interval"
        )
        
        if enable_monitor:
            refresh_interval = st.selectbox(
                "⏱️ Interval de Refresh",
                list(AppConfig.REFRESH_INTERVALS.keys()),
                help="Cât de des să se actualizeze rezultatele"
            )
            st.session_state.auto_refresh = True
            st.session_state.refresh_interval = AppConfig.REFRESH_INTERVALS[refresh_interval]
            st.info(f"🔄 Auto-refresh activ: la fiecare **{refresh_interval}**")
        else:
            st.session_state.auto_refresh = False
        
        st.markdown("---")
        
        # ============== CACHE MANAGEMENT ==============
        st.markdown("### 🗑️ Gestionare Cache")
        
        if st.button("🗑️ Șterge Cache", help="Șterge datele salvate temporar"):
            cache_manager.clear_cache()
            st.success("✅ Cache șters cu succes!")
            time.sleep(1)
            st.rerun()
    
    # ============== MAIN CONTENT AREA ==============
    
    # Display active filters
    if origin and destination:
        st.markdown("---")
        
        # Route display
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            origin_name = get_airport_name(origin)
            st.markdown(f"""
                <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            color: white; padding: 20px; border-radius: 10px; text-align: center;'>
                    <div style='font-size: 14px; opacity: 0.9;'>🛫 Plecare</div>
                    <div style='font-size: 20px; font-weight: bold; margin-top: 5px;'>{origin_name}</div>
                    <div style='font-size: 16px; margin-top: 5px;'>{origin}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div style='text-align: center; padding: 30px 0;'>
                    <div style='font-size: 40px;'>✈️</div>
                    <div style='font-size: 12px; color: #666;'>{departure_date.strftime('%d.%m.%Y')}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            dest_name = get_airport_name(destination)
            st.markdown(f"""
                <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                            color: white; padding: 20px; border-radius: 10px; text-align: center;'>
                    <div style='font-size: 14px; opacity: 0.9;'>🛬 Destinație</div>
                    <div style='font-size: 20px; font-weight: bold; margin-top: 5px;'>{dest_name}</div>
                    <div style='font-size: 16px; margin-top: 5px;'>{destination}</div>
                </div>
            """, unsafe_allow_html=True)
        
                # Active filters badges
        st.markdown("#### 🏷️ Filtre Active:")
        
        # Display filters as Streamlit components instead of HTML
        cols = st.columns([1, 1, 1, 1])
        
        with cols[0]:
            st.info(f"👥 {adults} {'pasager' if adults == 1 else 'pasageri'}")
        
        with cols[1]:
            st.info(f"🎫 {cabin_class}")
        
        with cols[2]:
            st.info(f"💰 {currency}")
        
        with cols[3]:
            st.info(f"📊 Max {max_results}")
        
        cols2 = st.columns([1, 1, 1])
        
        with cols2[0]:
            if return_date:
                st.info(f"🔄 Dus-întors {return_date.strftime('%d.%m.%Y')}")
            else:
                st.info("➡️ Doar dus")
        
        with cols2[1]:
            if non_stop:
                st.error("✈️ DOAR ZBORURI DIRECTE")
            else:
                st.info("🔄 Cu/fără escale")
        
        with cols2[2]:
            st.info(f"🎫 {cabin_class}")
        
        st.markdown("---")
    
    # ============== FLIGHT SEARCH ==============
    if search_button or st.session_state.auto_refresh:
        if not can_search:
            return
        
        # Validate inputs
        validator = FlightValidator()
        
        valid_origin, origin_msg = validator.validate_iata_code(origin)
        valid_dest, dest_msg = validator.validate_iata_code(destination)
        valid_dep, dep_msg = validator.validate_date(
            datetime.combine(departure_date, datetime.min.time())
        )
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
        
        search_params_display = f"""
        **Parametri căutare:**
        - Rută: {get_airport_name(origin)} → {get_airport_name(destination)}
        - Dată: {departure_date.strftime('%d.%m.%Y')} {f"- {return_date.strftime('%d.%m.%Y')}" if return_date else ""}
        - Pasageri: {adults}
        - Clasă: {cabin_class}
        - **Zboruri directe: {'DA ✅' if non_stop else 'NU'}**
        """
        
        with st.spinner('🔄 Căutăm cele mai bune zboruri...'):
            st.info(search_params_display)
            
            flights = aggregator.search_all(
                origin=origin,
                destination=destination,
                departure_date=departure_date.strftime('%Y-%m-%d'),
                return_date=return_date.strftime('%Y-%m-%d') if return_date else None,
                adults=adults,
                cabin_class=cabin_class,
                non_stop=non_stop,  # IMPORTANT: Parametrul pentru zboruri directe
                max_results=max_results
            )
        
        st.session_state.flights = flights
        
        # Add to monitor routes
        if enable_monitor:
            route_key = f"{origin}-{destination}-{departure_date}"
            route_info = {
                'route': f"{get_airport_name(origin)} → {get_airport_name(destination)}",
                'date': departure_date,
                'key': route_key,
                'non_stop': non_stop
            }
            
            # Update or add route
            existing = False
            for i, r in enumerate(st.session_state.monitor_routes):
                if r['key'] == route_key:
                    st.session_state.monitor_routes[i] = route_info
                    existing = True
                    break
            
            if not existing:
                st.session_state.monitor_routes.append(route_info)
    
    # ============== DISPLAY RESULTS ==============
    if st.session_state.flights:
        display_results(st.session_state.flights, non_stop if 'non_stop' in locals() else False)
    elif origin and destination:
        st.info("👆 **Apasă butonul '🔍 CAUTĂ ZBORURI' pentru a începe căutarea**")
    else:
        st.info("👈 **Selectează aeroporturile din sidebar pentru a începe**")
    
    # ============== AUTO-REFRESH LOGIC ==============
    if st.session_state.auto_refresh and st.session_state.flights:
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i in range(st.session_state.refresh_interval):
            progress = (i + 1) / st.session_state.refresh_interval
            progress_bar.progress(progress)
            remaining = st.session_state.refresh_interval - i - 1
            status_text.info(f"🔄 Auto-refresh în {remaining} secunde...")
            time.sleep(1)
        
        st.rerun()


def display_results(flights, non_stop_filter=False):
    """Display flight search results"""
    
    # Debug information
    total_flights = len(flights)
    direct_flights_count = len([f for f in flights if f.get('stops', 0) == 0])
    
    st.info(f"""
    📊 **Statistici căutare:**
    - Total zboruri găsite: **{total_flights}**
    - Zboruri directe: **{direct_flights_count}**
    - Zboruri cu escale: **{total_flights - direct_flights_count}**
    - Filtru "Doar directe" activ: **{'DA ✅' if non_stop_filter else 'NU'}**
    """)
    
    # Filter results if non-stop was selected
    original_count = len(flights)
    if non_stop_filter:
        flights = [f for f in flights if f.get('stops', 0) == 0]
        st.warning(f"🔍 Filtru activ: Afișez doar {len(flights)} zboruri directe din {original_count} total")
    
    if not flights:
        st.error("❌ **Nu am găsit zboruri care să corespundă criteriilor tale.**")
        
        if non_stop_filter and direct_flights_count == 0:
            st.warning(f"""
            ### ⚠️ Nu există zboruri directe disponibile pe această rută!
            
            **Din {original_count} zboruri găsite, niciun zbor nu este direct.**
            
            **Ce poți face:**
            1. ✅ **Dezactivează** filtrul "Doar zboruri directe" din sidebar
            2. 🔄 Încearcă alte date de călătorie
            3. ✈️ Verifică aeroporturi alternative din apropiere
            4. 📅 Încearcă zile diferite ale săptămânii
            """)
        else:
            st.info("""
            **Sugestii:**
            - Încearcă alte date
            - Verifică dacă există zboruri directe pe această rută
            - Dezactivează filtrul "Doar zboruri directe"
            - Încearcă aeroporturi alternative din apropiere
            """)
        return
    
    st.success(f"✅ **Am găsit {len(flights)} zboruri!**")
    
    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)
    
    prices = [f.get('price', 0) for f in flights if f.get('price')]
    
    with col1:
        if prices:
            st.metric(
                "💰 Cel Mai Ieftin",
                f"€{min(prices):.2f}",
                delta=None,
                help="Cel mai mic preț găsit"
            )
        else:
            st.metric("💰 Cel Mai Ieftin", "N/A")
    
    with col2:
        if prices:
            avg_price = sum(prices) / len(prices)
            st.metric(
                "📊 Preț Mediu",
                f"€{avg_price:.2f}",
                delta=None,
                help="Prețul mediu al zborurilor"
            )
        else:
            st.metric("📊 Preț Mediu", "N/A")
    
    with col3:
        if prices:
            st.metric(
                "💎 Cel Mai Scump",
                f"€{max(prices):.2f}",
                delta=None,
                help="Cel mai mare preț găsit"
            )
        else:
            st.metric("💎 Cel Mai Scump", "N/A")
    
    with col4:
        direct_flights = len([f for f in flights if f.get('stops', 0) == 0])
        st.metric(
            "✈️ Zboruri Directe",
            f"{direct_flights}/{len(flights)}",
            delta=None,
            help="Număr de zboruri directe"
        )
    
    st.markdown("---")
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs([
        "📋 Toate Zborurile",
        "💰 Top 10 Oferte",
        "📊 Analiză Prețuri"
    ])
    
    with tab1:
        display_table_view(flights)
    
    with tab2:
        display_best_deals(flights)
    
    with tab3:
        display_price_analysis(flights)


def display_table_view(flights):
    """Display flights in table format"""
    
    st.subheader("📋 Lista Completă a Zborurilor")
    
    formatter = FlightFormatter()
    df = formatter.flights_to_dataframe(flights)
    
    if df.empty:
        st.warning("⚠️ Nu există date de afișat")
        return
    
    # Select and reorder columns for display
    display_columns = []
    column_config = {}
    
    # Define preferred columns and their config
    preferred_cols = {
        'airline': st.column_config.TextColumn('Companie', width='medium'),
        'flight_number': st.column_config.TextColumn('Zbor', width='small'),
        'origin': st.column_config.TextColumn('De la', width='small'),
        'destination': st.column_config.TextColumn('Spre', width='small'),
        'departure_time': st.column_config.TextColumn('Plecare', width='medium'),
        'arrival_time': st.column_config.TextColumn('Sosire', width='medium'),
        'duration': st.column_config.TextColumn('Durată', width='small'),
        'stops': st.column_config.NumberColumn('Escale', width='small', format='%d'),
        'price': st.column_config.NumberColumn('Preț', width='medium', format='€%.2f'),
        'currency': st.column_config.TextColumn('Monedă', width='small'),
        'cabin_class': st.column_config.TextColumn('Clasă', width='medium'),
        'seats_available': st.column_config.TextColumn('Locuri', width='small')
    }
    
    # Add available columns
    for col, config in preferred_cols.items():
        if col in df.columns:
            display_columns.append(col)
            column_config[col] = config
    
    df_display = df[display_columns].copy()
    
    # Highlight direct flights
    def highlight_direct(row):
        if row.get('stops', 1) == 0:
            return ['background-color: #e8f5e9'] * len(row)
        return [''] * len(row)
    
    # Display dataframe
    st.dataframe(
        df_display,
        column_config=column_config,
        hide_index=True,
        use_container_width=True,
        height=600
    )
    
    # Download button
    csv = df_display.to_csv(index=False)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    st.download_button(
        label="📥 Descarcă rezultatele (CSV)",
        data=csv,
        file_name=f"flights_{timestamp}.csv",
        mime="text/csv",
        help="Descarcă toate rezultatele în format CSV"
    )


def display_best_deals(flights):
    """Display best flight deals"""
    
    st.subheader("💰 Top 10 Cele Mai Ieftine Zboruri")
    
    formatter = FlightFormatter()
    cheapest = formatter.get_cheapest_flights(flights, 10)
    
    if not cheapest:
        st.warning("⚠️ Nu există oferte disponibile")
        return
    
    for i, flight in enumerate(cheapest, 1):
        # Medal emoji for top 3
        medal = ""
        if i == 1:
            medal = "🥇"
        elif i == 2:
            medal = "🥈"
        elif i == 3:
            medal = "🥉"
        
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            
            with col1:
                st.markdown(f"**{medal} {i}. {flight.get('airline', 'N/A')} - {flight.get('flight_number', 'N/A')}**")
                st.text(f"🛫 {flight.get('origin', 'N/A')} → 🛬 {flight.get('destination', 'N/A')}")
                
                # Cabin class badge
                cabin = flight.get('cabin_class', 'N/A')
                cabin_emoji = {
                    'ECONOMY': '💺',
                    'PREMIUM_ECONOMY': '💺+',
                    'BUSINESS': '💼',
                    'FIRST': '👑'
                }.get(cabin, '🎫')
                st.text(f"{cabin_emoji} {cabin}")
            
            with col2:
                st.text(f"🛫 {FlightFormatter.format_datetime(flight.get('departure_time', 'N/A'))}")
                st.text(f"🛬 {FlightFormatter.format_datetime(flight.get('arrival_time', 'N/A'))}")
            
            with col3:
                st.text(f"⏱️ {FlightFormatter.format_duration(flight.get('duration', 'N/A'))}")
                
                stops = flight.get('stops', 0)
                if stops == 0:
                    st.markdown("**✈️ DIRECT**")
                else:
                    st.text(f"🔄 {stops} {'escală' if stops == 1 else 'escale'}")
            
            with col4:
                price = flight.get('price', 0)
                currency_symbol = {'EUR': '€', 'USD': '$', 'RON': 'RON', 'GBP': '£'}.get(
                    flight.get('currency', 'EUR'), '€'
                )
                st.markdown(
                    f"<div class='price-tag'>{currency_symbol}{price:.2f}</div>",
                    unsafe_allow_html=True
                )
                
                seats = flight.get('seats_available', 'N/A')
                if seats != 'N/A':
                    st.caption(f"💺 {seats} locuri")
            
            st.markdown("---")


def display_price_analysis(flights):
    """Display price analysis charts"""
    
    st.subheader("📊 Analiză Statistică a Prețurilor")
    
    if not flights:
        st.warning("⚠️ Nu există date pentru analiză")
        return
    
    import plotly.express as px
    import plotly.graph_objects as go
    
    df = FlightFormatter.flights_to_dataframe(flights)
    
    if df.empty or 'price' not in df.columns:
        st.warning("⚠️ Nu există date de preț disponibile")
        return
    
    # Remove invalid prices
    df = df[df['price'] > 0]
    
    if df.empty:
        st.warning("⚠️ Nu există prețuri valide pentru analiză")
        return
    
    # Row 1: Price distribution and airline comparison
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💰 Distribuția Prețurilor")
        fig = px.histogram(
            df,
            x='price',
            nbins=20,
            labels={'price': 'Preț (EUR)', 'count': 'Număr de Zboruri'},
            color_discrete_sequence=['#667eea']
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### ✈️ Preț Mediu pe Companie")
        if 'airline' in df.columns and df['airline'].notna().any():
            avg_price = df.groupby('airline')['price'].mean().sort_values(ascending=True)
            
            fig = px.bar(
                x=avg_price.values,
                y=avg_price.index,
                orientation='h',
                labels={'x': 'Preț Mediu (EUR)', 'y': 'Companie'},
                color=avg_price.values,
                color_continuous_scale='RdYlGn_r'
            )
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nu există date despre companii")
    
    # Row 2: Price vs Stops and time analysis
    if 'stops' in df.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🔄 Preț vs Număr de Escale")
            fig = px.box(
                df,
                x='stops',
                y='price',
                labels={'stops': 'Număr de Escale', 'price': 'Preț (EUR)'},
                color='stops',
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### 📈 Statistici pe Escale")
            stats_by_stops = df.groupby('stops')['price'].agg(['count', 'mean', 'min', 'max'])
            stats_by_stops.columns = ['Număr Zboruri', 'Preț Mediu', 'Preț Minim', 'Preț Maxim']
            stats_by_stops = stats_by_stops.round(2)
            st.dataframe(stats_by_stops, use_container_width=True)
    
    # Summary statistics
    st.markdown("#### 📊 Statistici Generale")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Zboruri Analizate", len(df))
    
    with col2:
        st.metric("Preț Minim", f"€{df['price'].min():.2f}")
    
    with col3:
        st.metric("Preț Maxim", f"€{df['price'].max():.2f}")
    
    with col4:
        st.metric("Deviație Standard", f"€{df['price'].std():.2f}")


if __name__ == "__main__":
    main()
