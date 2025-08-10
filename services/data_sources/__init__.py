"""
Data Sources Module - Enhanced with Sigmanaut Integration
Comprehensive data source management with AI capabilities
"""

# Core data source services
from .sanctions_watchlists import SanctionsWatchlistService
from .pep_data import PEPDataService
from .corruption_data import CorruptionDataService
from .adverse_media_simple import AdverseMediaService
from .manager import DataSourcesManager

# Enhanced capabilities (from sigmanaut integration)
try:
    from .enhanced_manager import EnhancedDataSourcesManager, EnhancedScreeningConfig
    from .adverse_media import AdverseMediaMonitor
    ENHANCED_FEATURES_AVAILABLE = True
except ImportError:
    ENHANCED_FEATURES_AVAILABLE = False

__all__ = [
    "SanctionsWatchlistService",
    "PEPDataService", 
    "CorruptionDataService",
    "AdverseMediaService",
    "DataSourcesManager",
]

# Add enhanced features if available
if ENHANCED_FEATURES_AVAILABLE:
    __all__.extend([
        "EnhancedDataSourcesManager",
        "EnhancedScreeningConfig",
        "AdverseMediaMonitor",
    ])

# Future data source services (planned)
# from .beneficial_ownership import BeneficialOwnershipService
# from .transaction_monitoring import TransactionMonitoringService  
# from .legal_records import LegalRecordsService
# from .blockchain_intelligence import BlockchainIntelligenceService
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
