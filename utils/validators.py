"""Input validation utilities."""
import re
from datetime import datetime, timedelta
from typing import Tuple, Optional

class FlightValidator:
    """Validates flight search inputs"""
    
    @staticmethod
    def validate_iata_code(code: str) -> Tuple[bool, str]:
        """Validate IATA airport code"""
        if not code:
            return False, "Airport code cannot be empty"
        
        if len(code) != 3:
            return False, "Airport code must be 3 characters"
        
        if not code.isalpha():
            return False, "Airport code must contain only letters"
        
        return True, ""
    
    @staticmethod
    def validate_date(date: datetime, is_return: bool = False) -> Tuple[bool, str]:
        """Validate flight date"""
        today = datetime.now().date()
        
        if date.date() < today:
            return False, "Date cannot be in the past"
        
        max_date = today + timedelta(days=365)
        if date.date() > max_date:
            return False, "Date cannot be more than 1 year in the future"
        
        return True, ""
    
    @staticmethod
    def validate_passenger_count(count: int) -> Tuple[bool, str]:
        """Validate passenger count"""
        if count < 1:
            return False, "Must have at least 1 passenger"
        
        if count > 9:
            return False, "Maximum 9 passengers allowed"
        
        return True, ""
    
    @staticmethod
    def validate_dates(departure: datetime, return_date: Optional[datetime]) -> Tuple[bool, str]:
        """Validate departure and return dates"""
        if return_date and return_date.date() <= departure.date():
            return False, "Return date must be after departure date"
        
        return True, ""
