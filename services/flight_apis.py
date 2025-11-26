"""Flight API integrations with error handling and rate limiting."""
import requests
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from amadeus import Client, ResponseError
from config.settings import APIConfig, AppConfig
from services.cache_manager import cache_manager
import streamlit as st

class AmadeusAPI:
    """Amadeus Flight Offers Search API wrapper"""
    
    def __init__(self):
        creds = APIConfig.get_amadeus_credentials()
        try:
            self.client = Client(
                client_id=creds['api_key'],
                client_secret=creds['api_secret']
            )
            st.success("✅ Amadeus API inițializat cu succes")
        except Exception as e:
            st.error(f"❌ Amadeus API initialization failed: {str(e)}")
            self.client = None
    
    def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        adults: int = 1,
        cabin_class: str = 'ECONOMY',
        non_stop: bool = False,
        max_results: int = 10,
        currency: str = 'EUR'
    ) -> List[Dict[str, Any]]:
        """Search for flight offers with advanced parameters"""
        
        st.info(f"""
        🔍 **Amadeus API - Parametri cerere:**
        - Origin: {origin}
        - Destination: {destination}
        - Departure: {departure_date}
        - Return: {return_date}
        - Adults: {adults}
        - Cabin: {cabin_class}
        - Non-stop: {non_stop}
        - Max results: {max_results}
        """)
        
        if not self.client:
            st.error("❌ Amadeus client nu este inițializat!")
            return []
        
        # Check cache
        cache_key = f"{origin}_{destination}_{departure_date}_{return_date}_{adults}_{cabin_class}_{non_stop}"
        cached = cache_manager.get_cached('amadeus_flights', cache_key, 
                                         AppConfig.CACHE_TTL['flight_search'])
        if cached:
            st.success(f"✅ Găsit în cache: {len(cached)} zboruri")
            return cached
        
        # Check rate limit
        cache_manager.wait_for_rate_limit('amadeus', 
                                         AppConfig.RATE_LIMITS['amadeus'])
        
        try:
            params = {
                'originLocationCode': origin.upper(),
                'destinationLocationCode': destination.upper(),
                'departureDate': departure_date,
                'adults': adults,
                'travelClass': cabin_class,
                'nonStop': non_stop,
                'max': max_results,
                'currencyCode': currency
            }
            
            if return_date:
                params['returnDate'] = return_date
            
            st.info(f"📡 Trimit cerere către Amadeus API...")
            st.code(str(params))
            
            response = self.client.shopping.flight_offers_search.get(**params)
            
            st.success(f"✅ Răspuns primit de la Amadeus API")
            
            # Debug: Check response
            if hasattr(response, 'data'):
                st.info(f"📊 Număr de oferte primite: {len(response.data)}")
            else:
                
