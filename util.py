"""Assorted utility functions for the application"""
import uuid

def generate_token():
    """Generates and returns a random unique string token"""
    return uuid.uuid4().hex
