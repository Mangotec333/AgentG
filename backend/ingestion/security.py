"""
Security utilities for ingestion API.
"""
import os
from typing import Optional
from shared.logger import backend_logger
from shared.token_auth import TokenManager
from shared.config import BackendConfig


def verify_api_key(api_key: Optional[str], workspace_id: str) -> bool:
    """
    Verify API key for a workspace.
    
    Args:
        api_key: API key from request
        workspace_id: Workspace identifier
    
    Returns:
        True if valid
    """
    if not api_key:
        backend_logger.warning("No API key provided")
        return False
    
    # In production, this would:
    # 1. Look up workspace in database
    # 2. Verify API key hash matches stored hash
    # 3. Check if workspace is active
    
    # For now, simple check against environment variable
    config = BackendConfig()
    expected_key = os.getenv("SHIELD_API_KEY")
    
    if expected_key and api_key == expected_key:
        return True
    
    # Alternative: verify token format
    try:
        return TokenManager.verify_token(api_key, expected_key or "", workspace_id)
    except Exception as e:
        backend_logger.error(f"Token verification error: {e}")
        return False

