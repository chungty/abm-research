"""
Data Classification System for Mock vs Real Data
Ensures sales teams know data reliability and source
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class DataSource(Enum):
    """Data source classification"""
    REAL_API = "Real API Data"
    REAL_SCRAPE = "Real Web Scraping"
    REAL_MANUAL = "Real Manual Research"
    MOCK_GENERATED = "Mock Generated"
    TEST_SIMULATED = "Test Simulated"
    DEMO_SAMPLE = "Demo Sample"
    PLACEHOLDER = "Placeholder"


class DataQuality(Enum):
    """Data quality classification"""
    VERIFIED = "Verified"
    HIGH_CONFIDENCE = "High Confidence"
    MEDIUM_CONFIDENCE = "Medium Confidence"
    LOW_CONFIDENCE = "Low Confidence"
    UNVERIFIED = "Unverified"
    MOCK_DATA = "Mock Data"


@dataclass
class DataClassification:
    """Classification metadata for any piece of data"""

    source: DataSource
    quality: DataQuality
    created_date: datetime = field(default_factory=datetime.now)
    verified_date: Optional[datetime] = None
    verification_method: Optional[str] = None
    confidence_score: float = 0.0  # 0-100
    notes: str = ""

    def is_production_ready(self) -> bool:
        """Check if data is suitable for production use"""
        production_sources = [
            DataSource.REAL_API,
            DataSource.REAL_SCRAPE,
            DataSource.REAL_MANUAL
        ]
        return self.source in production_sources

    def is_mock_data(self) -> bool:
        """Check if this is mock/test data"""
        mock_sources = [
            DataSource.MOCK_GENERATED,
            DataSource.TEST_SIMULATED,
            DataSource.DEMO_SAMPLE,
            DataSource.PLACEHOLDER
        ]
        return self.source in mock_sources

    def get_display_indicator(self) -> str:
        """Get visual indicator for UI display"""
        if self.is_mock_data():
            indicators = {
                DataSource.MOCK_GENERATED: "🧪 [MOCK]",
                DataSource.TEST_SIMULATED: "🔬 [SIMULATED]",
                DataSource.DEMO_SAMPLE: "📋 [DEMO]",
                DataSource.PLACEHOLDER: "📝 [PLACEHOLDER]"
            }
            return indicators.get(self.source, "⚠️ [TEST DATA]")
        else:
            return "✅"

    def get_reliability_warning(self) -> Optional[str]:
        """Get warning message if data reliability is questionable"""
        if self.is_mock_data():
            return f"⚠️ WARNING: This is {self.source.value.lower()} - not actual company data"

        if self.quality == DataQuality.LOW_CONFIDENCE:
            return "⚠️ CAUTION: Low confidence data - verify before using in sales outreach"

        if self.quality == DataQuality.UNVERIFIED:
            return "⚠️ UNVERIFIED: This data has not been validated - use with caution"

        return None


class DataClassifier:
    """Helper class to classify and tag data appropriately"""

    @staticmethod
    def create_real_api_classification(api_name: str, confidence: float = 90.0) -> DataClassification:
        """Create classification for real API data"""
        return DataClassification(
            source=DataSource.REAL_API,
            quality=DataQuality.HIGH_CONFIDENCE if confidence >= 80 else DataQuality.MEDIUM_CONFIDENCE,
            confidence_score=confidence,
            verification_method=f"API response from {api_name}",
            verified_date=datetime.now(),
            notes=f"Retrieved from {api_name} API"
        )

    @staticmethod
    def create_mock_classification(mock_type: str = "generated", notes: str = "") -> DataClassification:
        """Create classification for mock/test data"""
        source_mapping = {
            "generated": DataSource.MOCK_GENERATED,
            "simulated": DataSource.TEST_SIMULATED,
            "demo": DataSource.DEMO_SAMPLE,
            "placeholder": DataSource.PLACEHOLDER
        }

        return DataClassification(
            source=source_mapping.get(mock_type, DataSource.MOCK_GENERATED),
            quality=DataQuality.MOCK_DATA,
            confidence_score=0.0,
            notes=notes or f"Mock data for testing purposes"
        )

    @staticmethod
    def create_scraped_classification(source_url: str, confidence: float) -> DataClassification:
        """Create classification for web scraped data"""
        quality_mapping = {
            (90, 100): DataQuality.HIGH_CONFIDENCE,
            (70, 89): DataQuality.MEDIUM_CONFIDENCE,
            (50, 69): DataQuality.LOW_CONFIDENCE,
            (0, 49): DataQuality.UNVERIFIED
        }

        quality = DataQuality.LOW_CONFIDENCE
        for (min_conf, max_conf), qual in quality_mapping.items():
            if min_conf <= confidence <= max_conf:
                quality = qual
                break

        return DataClassification(
            source=DataSource.REAL_SCRAPE,
            quality=quality,
            confidence_score=confidence,
            verification_method=f"Web scraping from {source_url}",
            verified_date=datetime.now(),
            notes=f"Scraped from {source_url}"
        )


def add_classification_to_dict(data_dict: Dict[str, Any],
                              classification: DataClassification) -> Dict[str, Any]:
    """Add classification metadata to a data dictionary"""
    data_dict['_data_classification'] = {
        'source': classification.source.value,
        'quality': classification.quality.value,
        'indicator': classification.get_display_indicator(),
        'is_mock': classification.is_mock_data(),
        'is_production_ready': classification.is_production_ready(),
        'confidence_score': classification.confidence_score,
        'warning': classification.get_reliability_warning(),
        'created_date': classification.created_date.isoformat(),
        'notes': classification.notes
    }
    return data_dict


def format_data_for_display(data_dict: Dict[str, Any], field_name: str) -> str:
    """Format data with appropriate mock/real indicators for display"""
    value = data_dict.get(field_name, "")
    classification = data_dict.get('_data_classification', {})

    if classification.get('is_mock', False):
        indicator = classification.get('indicator', '⚠️ [TEST]')
        return f"{value} {indicator}"
    else:
        return str(value)


def get_data_reliability_summary(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Get summary of data reliability across a collection"""
    total = len(items)
    if total == 0:
        return {'total': 0, 'mock': 0, 'real': 0, 'mock_percentage': 0}

    mock_count = sum(1 for item in items
                    if item.get('_data_classification', {}).get('is_mock', False))
    real_count = total - mock_count

    return {
        'total': total,
        'mock': mock_count,
        'real': real_count,
        'mock_percentage': round((mock_count / total) * 100, 1),
        'production_ready': real_count > 0,
        'warning': f"⚠️ {mock_count}/{total} items are mock/test data" if mock_count > 0 else None
    }