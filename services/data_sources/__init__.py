"""
Data Sources Management Module
Comprehensive data source integration for compliance and OSINT
"""

from .sanctions_watchlists import SanctionsWatchlistService
from .pep_data import PEPDataService
from .adverse_media import AdverseMediaService
from .corruption_data import CorruptionDataService
from .manager import DataSourcesManager

# Note: Additional services to be implemented in future phases
# from .beneficial_ownership import BeneficialOwnershipDataService
# from .transaction_monitoring_data import TransactionMonitoringDataService
# from .legal_court_data import LegalCourtDataService
# from .data_aggregator import DataAggregationService

__all__ = [
    'SanctionsWatchlistService',
    'PEPDataService', 
    'AdverseMediaService',
    'CorruptionDataService',
    'DataSourcesManager'
    # Future services:
    # 'BeneficialOwnershipDataService',
    # 'TransactionMonitoringDataService',
    # 'LegalCourtDataService',
    # 'DataAggregationService'
]
