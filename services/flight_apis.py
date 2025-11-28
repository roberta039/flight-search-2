"""Flight API integrations - WITHOUT Amadeus."""
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from config.settings import APIConfig, AppConfig
from services.cache_manager import cache_manager
import streamlit as st


class SkyscannerAPI:
    """Skyscanner API via RapidAPI"""
    
    def __init__(self):
        self.api_key = APIConfig.get_rapidapi_key()
        self.base_url = "https://skyscanner-api.p.rapidapi.com"
        self.headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': 'skyscanner-api.p.rapidapi.com'
        }
    
    def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        adults: int = 1,
        cabin_class: str = 'ECONOMY',
        non_stop: bool = False,
        currency: str = 'EUR'
    ) -> List[Dict[str, Any]]:
        """Search flights using Skyscanner API"""
        
        # Note: Skyscanner API via RapidAPI might require different endpoints
        # This is a placeholder that will gracefully fail and use mock data
        
        cache_key = f"sky_{origin}_{destination}_{departure_date}_{return_date}_{adults}_{non_stop}"
        cached = cache_manager.get_cached('skyscanner', cache_key, 
                                         AppConfig.CACHE_TTL['flight_search'])
        if cached:
            return cached
        
        try:
            # Attempt to call API (this might fail if endpoint is wrong)
            # We'll catch the error and return empty list
            return []
        except Exception as e:
            return []


class AviationStackAPI:
    """AviationStack API via RapidAPI"""
    
    def __init__(self):
        self.api_key = APIConfig.get_rapidapi_key()
        self.headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': 'aviationstack1.p.rapidapi.com'
        }
    
    def search_flights(
        self,
        origin: str,
        destination: str
    ) -> List[Dict[str, Any]]:
        """Search flights using AviationStack"""
        
        cache_key = f"avstack_{origin}_{destination}"
        cached = cache_manager.get_cached('aviationstack', cache_key,
                                         AppConfig.CACHE_TTL['flight_search'])
        if cached:
            return cached
        
        try:
            url = "https://aviationstack1.p.rapidapi.com/v1/flights"
            
            params = {
                'dep_iata': origin.upper(),
                'arr_iata': destination.upper()
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return []  # We'll use mock data instead
            else:
                return []
                
        except Exception:
            return []


class AirLabsAPI:
    """AirLabs API - Route information"""
    
    def __init__(self):
        self.api_key = APIConfig.get_airlabs_key()
        self.base_url = "https://airlabs.co/api/v9"
    
    def search_routes(
        self,
        dep_iata: str,
        arr_iata: str
    ) -> List[Dict[str, Any]]:
        """Search flight routes"""
        
        cache_key = f"airlabs_{dep_iata}_{arr_iata}"
        cached = cache_manager.get_cached('airlabs', cache_key,
                                         AppConfig.CACHE_TTL['flight_search'])
        if cached:
            return cached
        
        cache_manager.wait_for_rate_limit('airlabs',
                                         AppConfig.RATE_LIMITS['airlabs'])
        
        try:
            url = f"{self.base_url}/routes"
            params = {
                'api_key': self.api_key,
                'dep_iata': dep_iata.upper(),
                'arr_iata': arr_iata.upper()
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                routes = data.get('response', [])
                
                cache_manager.set_cached('airlabs', cache_key, routes,
                                       AppConfig.CACHE_TTL['flight_search'])
                
                return routes
            else:
                return []
                
        except Exception:
            return []


class FlightAggregator:
    """Aggregates flight results - Uses MOCK DATA primarily"""
    
    def __init__(self):
        """Initialize flight aggregator"""
        # Initialize APIs but don't show messages yet
        self.skyscanner = SkyscannerAPI()
        self.aviationstack = AviationStackAPI()
        self.airlabs = AirLabsAPI()
        self.use_mock = True  # Default to mock data
    
    def search_all(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        adults: int = 1,
        cabin_class: str = 'ECONOMY',
        non_stop: bool = False,
        max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """Search flights - primarily using mock data"""
        
        st.markdown("---")
        st.markdown("### 🔍 Căutare Zboruri")
        
        all_flights = []
        
        # Show info about search
        st.info(f"""
        **Căutare pentru:**
        - Rută: {origin.upper()} → {destination.upper()}
        - Dată plecare: {departure_date}
        - Dată întoarcere: {return_date if return_date else 'Nu'}
        - Pasageri: {adults}
        - Clasă: {cabin_class}
        - Doar directe: {'Da' if non_stop else 'Nu'}
        """)
        
        # Try to get data from AirLabs (just for route verification)
        try:
            with st.spinner('🔍 Verificare rute disponibile...'):
                routes = self.airlabs.search_routes(origin, destination)
                if routes:
                    st.success(f"✅ Rută validă: Găsite {len(routes)} conexiuni aeriene")
                else:
                    st.info("ℹ️ Verificare rute completată")
        except Exception as e:
            st.info("ℹ️ Verificare rute...")
        
        # Load mock data
        st.info("📦 Încărcare date de zbor...")
        
        try:
            from data.mock_flights import get_mock_flights
            
            mock_flights = get_mock_flights(
                origin=origin,
                destination=destination,
                departure_date=departure_date,
                return_date=return_date,
                adults=adults,
                non_stop=non_stop,
                cabin_class=cabin_class
            )
            
            if mock_flights:
                all_flights.extend(mock_flights)
                self.use_mock = True
                
                st.success(f"""
                ✅ **Găsite {len(mock_flights)} zboruri!**
                
                **Note:**
                - Zborurile afișate sunt **date demonstrative**
                - Prețurile sunt **estimate** bazate pe ruta selectată
                - Pentru rezervări reale, vizitați site-urile companiilor aeriene
                
                **Caracteristici:**
                - Filtrare funcțională (directe/escale)
                - Sortare după preț
                - Export date (CSV)
                - Analiză statistică
                """)
            else:
                st.warning("Nu s-au putut genera date de zbor")
                
        except ImportError:
            st.error("❌ Modulul de date nu este disponibil")
        except Exception as e:
            st.error(f"❌ Eroare: {str(e)}")
        
        st.markdown("---")
        
        # Summary statistics
        if all_flights:
            direct_count = len([f for f in all_flights if f.get('stops', 0) == 0])
            with_stops_count = len([f for f in all_flights if f.get('stops', 0) > 0])
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Zboruri", len(all_flights))
            
            with col2:
                st.metric("✈️ Zboruri Directe", direct_count)
            
            with col3:
                st.metric("🔄 Cu Escale", with_stops_count)
        
        # Sort by price
        all_flights.sort(key=lambda x: x.get('price', float('inf')))
        
        # Apply non-stop filter if needed
        if non_stop and all_flights:
            before_filter = len(all_flights)
            all_flights = [f for f in all_flights if f.get('stops', 0) == 0]
            if len(all_flights) < before_filter:
                st.info(f"🔍 Filtru aplicat: {len(all_flights)} zboruri directe din {before_filter} total")
        
        return all_flights[:max_results]
