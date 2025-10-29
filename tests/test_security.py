"""Test security utilities"""

import pytest
from datetime import timedelta

from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token
)


def test_password_hashing():
    """Test password hashing and verification"""
    password = "testpassword123"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)


def test_create_access_token():
    """Test JWT token creation"""
    data = {"sub": "testuser"}
    token = create_access_token(data)
    
    assert token is not None
    assert isinstance(token, str)


def test_decode_access_token():
    """Test JWT token decoding"""
    data = {"sub": "testuser"}
    token = create_access_token(data)
    
    decoded = decode_access_token(token)
    
    assert decoded is not None
    assert decoded["sub"] == "testuser"
    assert "exp" in decoded


def test_decode_invalid_token():
    """Test decoding invalid token"""
    invalid_token = "invalid.token.here"
    
    decoded = decode_access_token(invalid_token)
    
    assert decoded is None


def test_token_expiration():
    """Test token expiration"""
    data = {"sub": "testuser"}
    
    # Create token with very short expiration
    token = create_access_token(data, expires_delta=timedelta(seconds=-1))
    decoded = decode_access_token(token)
    
    # Token should be expired and invalid
    assert decoded is None
