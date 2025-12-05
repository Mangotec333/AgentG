"""
Token-based authentication for API requests.
"""
import hmac
import hashlib
import time
from typing import Optional
from shared.logger import backend_logger


class TokenManager:
    """Manages API token authentication."""
    
    @staticmethod
    def generate_token(api_key: str, workspace_id: str, timestamp: Optional[int] = None) -> str:
        """
        Generate an authentication token.
        
        Args:
            api_key: Secret API key
            workspace_id: Workspace identifier
            timestamp: Optional timestamp (defaults to current time)
        
        Returns:
            Authentication token
        """
        if timestamp is None:
            timestamp = int(time.time())
        
        message = f"{workspace_id}:{timestamp}"
        token = hmac.new(
            api_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return f"{timestamp}:{token}"
    
    @staticmethod
    def verify_token(token: str, api_key: str, workspace_id: str, max_age_seconds: int = 300) -> bool:
        """
        Verify an authentication token.
        
        Args:
            token: Token to verify
            api_key: Secret API key
            workspace_id: Workspace identifier
            max_age_seconds: Maximum token age in seconds
        
        Returns:
            True if token is valid
        """
        try:
            parts = token.split(":")
            if len(parts) != 2:
                return False
            
            timestamp_str, token_hash = parts
            timestamp = int(timestamp_str)
            
            # Check token age
            if time.time() - timestamp > max_age_seconds:
                backend_logger.warning(f"Token expired: age={time.time() - timestamp}s")
                return False
            
            # Verify token
            expected_token = TokenManager.generate_token(api_key, workspace_id, timestamp)
            expected_hash = expected_token.split(":")[1]
            
            return hmac.compare_digest(token_hash, expected_hash)
        
        except (ValueError, IndexError) as e:
            backend_logger.error(f"Token verification error: {e}")
            return False

