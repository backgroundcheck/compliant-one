"""
Data Ingestion Services Package
Handles data ingestion from various regulatory and compliance sources
"""

from .oecd_service import OECDDataIngestionService

__all__ = ['OECDDataIngestionService']
