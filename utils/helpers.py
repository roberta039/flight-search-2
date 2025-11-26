"""Helper utilities for formatting and data processing."""
from datetime import datetime, timedelta
from typing import List, Dict, Any
import pandas as pd

class FlightFormatter:
    """Format flight data for display"""
    
    @staticmethod
    def format_duration(duration_str: str) -> str:
        """Format ISO 8601 duration to readable format"""
        if not duration_str or duration_str == 'N/A':
            return 'N/A'
        
        try:
            # Remove PT prefix
            duration_str = duration_str.replace('PT', '')
            
            hours = 0
            minutes = 0
            
            if 'H' in duration_str:
                hours = int(duration_str.split('H')[0])
                duration_str = duration_str.split('H')[1]
            
            if 'M' in duration_str:
                minutes = int(duration_str.replace('M', ''))
            
            return f"{hours}h {minutes}m"
        except:
            return duration_str
    
    @staticmethod
    def format_datetime(dt_str: str) -> str:
        """Format datetime string"""
        if not dt_str or dt_str == 'N/A':
            return 'N/A'
        
        try:
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            return dt.strftime('%Y-%m-%d %H:%M')
        except:
            return dt_str
    
    @staticmethod
    def flights_to_dataframe(flights: List[Dict[str, Any]]) -> pd.DataFrame:
        """Convert flights list to pandas DataFrame"""
        if not flights:
            return pd.DataFrame()
        
        df = pd.DataFrame(flights)
        
        # Format columns
        if 'departure_time' in df.columns:
            df['departure_time'] = df['departure_time'].apply(
                FlightFormatter.format_datetime
            )
        
        if 'arrival_time' in df.columns:
            df['arrival_time'] = df['arrival_time'].apply(
                FlightFormatter.format_datetime
            )
        
        if 'duration' in df.columns:
            df['duration'] = df['duration'].apply(
                FlightFormatter.format_duration
            )
        
        if 'price' in df.columns:
            df['price'] = df['price'].round(2)
        
        return df
    
    @staticmethod
    def get_cheapest_flights(flights: List[Dict[str, Any]], n: int = 10) -> List[Dict[str, Any]]:
        """Get n cheapest flights"""
        sorted_flights = sorted(flights, key=lambda x: x.get('price', float('inf')))
        return sorted_flights[:n]
