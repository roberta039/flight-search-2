"""Flight API integrations with error handling and rate limiting."""
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from amadeus import Client, ResponseError
from config.settings import APIConfig, AppConfig
from services.cache_manager import cache_manager
import streamlit as st
import json

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
                'nonStop': non_stop,  # BOOLEAN, nu string
                'max': max_results,
                'currencyCode': currency
            }
            
            if return_date:
                params['returnDate'] = return_date
            
            st.info(f"📡 Trimit cerere către Amadeus API...")
            st.code(json.dumps(params, indent=2))
            
            response = self.client.shopping.flight_offers_search.get(**params)
            
            st.success(f"✅ Răspuns primit de la Amadeus API")
            
            # Debug: Check response
            if hasattr(response, 'data'):
                st.info(f"📊 Număr de oferte primite: {len(response.data)}")
                
                # Show first offer structure
                if len(response.data) > 0:
                    with st.expander("🔍 DEBUG: Primul zbor din răspuns"):
                        st.json(response.data[0])
            else:
                st.warning("⚠️ Răspunsul nu conține câmpul 'data'")
                st.json(str(response))
            
            flights = self._parse_amadeus_response(response.data)
            
            st.success(f"✅ Zbouri parsate: {len(flights)}")
            
            # Show parsed flights details
            if flights:
                with st.expander("🔍 DEBUG: Primul zbor parsat"):
                    st.json(flights[0])
                
                # Count direct flights
                direct_count = len([f for f in flights if f.get('stops', 0) == 0])
                st.info(f"✈️ Zboruri directe în răspuns: {direct_count}/{len(flights)}")
            
            # Cache results
            cache_manager.set_cached('amadeus_flights', cache_key, flights,
                                   AppConfig.CACHE_TTL['flight_search'])
            
            return flights
            
        except ResponseError as error:
            st.error(f"❌ **Amadeus API Error:**")
            st.error(f"Code: {error.response.status_code}")
            
            # Parse error details
            try:
                error_data = error.response.json()
                st.error(f"Eroare: {json.dumps(error_data, indent=2)}")
                
                if 'errors' in error_data:
                    for err in error_data['errors']:
                        st.error(f"- {err.get('title', 'Unknown error')}: {err.get('detail', '')}")
            except:
                st.error(f"Raw error: {str(error)}")
            
            return []
            
        except Exception as e:
            st.error(f"❌ **Unexpected error:** {str(e)}")
            st.exception(e)
            return []
    
    def _parse_amadeus_response(self, data: List) -> List[Dict[str, Any]]:
        """Parse Amadeus API response into standardized format"""
        
        st.info(f"🔧 Parsez {len(data)} oferte...")
        
        flights = []
        
        for idx, offer in enumerate(data):
            try:
                itineraries = offer.get('itineraries', [])
                price = offer.get('price', {})
                
                st.write(f"Oferta {idx + 1}: {len(itineraries)} itinerarii")
                
                for itin_idx, itinerary in enumerate(itineraries):
                    segments = itinerary.get('segments', [])
                    
                    if not segments:
                        st.warning(f"  - Itinerariu {itin_idx + 1}: Fără segmente")
                        continue
                    
                    first_segment = segments[0]
                    last_segment = segments[-1]
                    
                    num_stops = len(segments) - 1
                    
                    flight = {
                        'source': 'Amadeus',
                        'airline': first_segment.get('carrierCode', 'N/A'),
                        'flight_number': f"{first_segment.get('carrierCode', '')}{first_segment.get('number', '')}",
                        'origin': first_segment.get('departure', {}).get('iataCode', 'N/A'),
                        'destination': last_segment.get('arrival', {}).get('iataCode', 'N/A'),
                        'departure_time': first_segment.get('departure', {}).get('at', 'N/A'),
                        'arrival_time': last_segment.get('arrival', {}).get('at', 'N/A'),
                        'duration': itinerary.get('duration', 'N/A'),
                        'stops': num_stops,
                        'price': float(price.get('total', 0)),
                        'currency': price.get('currency', 'EUR'),
                        'cabin_class': first_segment.get('cabin', 'N/A'),
                        'seats_available': first_segment.get('numberOfBookableSeats', 'N/A'),
                        'booking_link': 'https://www.amadeus.com'
                    }
                    
                    st.write(f"  - Zbor: {flight['airline']} {flight['flight_number']}, Escale: {num_stops}, Preț: €{flight['price']}")
                    
                    flights.append(flight)
                    
            except Exception as e:
                st.warning(f"⚠️ Eroare la parsarea ofertei {idx + 1}: {str(e)}")
                continue
        
        st.success(f"✅ Total zbouri parsate cu succes: {len(flights)}")
        
        return flights


class RapidAPIFlights:
    """RapidAPI flight search integrations"""
    
    def __init__(self):
        self.api_key = APIConfig.get_rapidapi_key()
        self.headers = {
            'x-rapidapi-key': self.api_key,
            'x-rapidapi-host': 'aerodatabox.p.rapidapi.com'
        }
    
    def search_aerodatabox(
        self,
        airport_iata: str,
        direction: str = 'Both'
    ) -> List[Dict[str, Any]]:
        """Search flights using AerodataBox API"""
        
        cache_key = f"aerodatabox_{airport_iata}_{direction}"
        cached = cache_manager.get_cached('aerodatabox', cache_key, 
                                         AppConfig.CACHE_TTL['flight_search'])
        if cached:
            return cached
        
        cache_manager.wait_for_rate_limit('rapidapi', 
                                         AppConfig.RATE_LIMITS['rapidapi'])
        
        try:
            url = f"https://aerodatabox.p.rapidapi.com/flights/airports/iata/{airport_iata}"
            params = {
                'offsetMinutes': '-120',
                'durationMinutes': '720',
                'withLeg': 'true',
                'direction': direction,
                'withCancelled': 'false',
                'withCodeshared': 'true',
                'withCargo': 'false',
                'withPrivate': 'false',
                'withLocation': 'false'
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            flights = self._parse_aerodatabox_response(data)
            
            cache_manager.set_cached('aerodatabox', cache_key, flights,
                                   AppConfig.CACHE_TTL['flight_search'])
            
            return flights
            
        except requests.exceptions.RequestException as e:
            st.warning(f"⚠️ AerodataBox API Error: {str(e)}")
            return []
    
    def _parse_aerodatabox_response(self, data: Dict) -> List[Dict[str, Any]]:
        """Parse AerodataBox response"""
        flights = []
        
        for direction in ['departures', 'arrivals']:
            if direction not in data:
                continue
            
            for flight in data[direction]:
                try:
                    departure = flight.get('departure', {})
                    arrival = flight.get('arrival', {})
                    
                    flight_info = {
                        'source': 'AerodataBox',
                        'airline': flight.get('airline', {}).get('name', 'N/A'),
                        'flight_number': flight.get('number', 'N/A'),
                        'origin': departure.get('airport', {}).get('iata', 'N/A'),
                        'destination': arrival.get('airport', {}).get('iata', 'N/A'),
                        'departure_time': departure.get('scheduledTime', {}).get('local', 'N/A'),
                        'arrival_time': arrival.get('scheduledTime', {}).get('local', 'N/A'),
                        'status': flight.get('status', 'N/A'),
                        'aircraft': flight.get('aircraft', {}).get('model', 'N/A')
                    }
                    
                    flights.append(flight_info)
                    
                except Exception:
                    continue
        
        return flights


class AirLabsAPI:
    """AirLabs API integration"""
    
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
                
