"""
Data source integrations for ABM Research System
Handles API clients and web scraping for research data
"""
from .apollo_client import ApolloClient
from .web_scraper import WebScraper
from .linkedin_scraper import LinkedInScraper
from .trigger_event_detector import TriggerEventDetector

__all__ = ["ApolloClient", "WebScraper", "LinkedInScraper", "TriggerEventDetector"]
