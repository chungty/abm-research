"""
Geographic scoring for US market preference
"""
from typing import List, Dict, Any
from enum import Enum


class GeographicPriority(Enum):
    US_PRIMARY = "US Primary"
    US_SECONDARY = "US Secondary"
    INTERNATIONAL_WITH_US = "International with US Presence"
    INTERNATIONAL_ONLY = "International Only"


class GeographicScorer:
    """Handles geographic scoring based on US market preference"""

    def __init__(self):
        # US states and regions for scoring
        self.us_indicators = [
            # States
            'california', 'texas', 'new york', 'florida', 'illinois', 'pennsylvania',
            'ohio', 'georgia', 'north carolina', 'michigan', 'virginia', 'washington',
            'arizona', 'massachusetts', 'tennessee', 'indiana', 'missouri', 'maryland',
            'wisconsin', 'colorado', 'minnesota', 'south carolina', 'alabama', 'louisiana',
            'kentucky', 'oregon', 'oklahoma', 'connecticut', 'utah', 'iowa', 'nevada',
            'arkansas', 'mississippi', 'kansas', 'new mexico', 'nebraska', 'west virginia',
            'idaho', 'hawaii', 'new hampshire', 'maine', 'montana', 'rhode island',
            'delaware', 'south dakota', 'north dakota', 'alaska', 'vermont', 'wyoming',

            # Major cities
            'new york city', 'los angeles', 'chicago', 'houston', 'phoenix', 'philadelphia',
            'san antonio', 'san diego', 'dallas', 'san jose', 'austin', 'jacksonville',
            'fort worth', 'columbus', 'charlotte', 'san francisco', 'indianapolis',
            'seattle', 'denver', 'boston', 'atlanta', 'miami', 'las vegas',

            # Common abbreviations
            'ny', 'ca', 'tx', 'fl', 'il', 'pa', 'oh', 'ga', 'nc', 'mi', 'va', 'wa',
            'az', 'ma', 'tn', 'in', 'mo', 'md', 'wi', 'co', 'mn', 'sc', 'al', 'la',

            # Other indicators
            'usa', 'united states', 'americas', 'north america'
        ]

    def score_geographic_fit(self, data_center_locations: List[str],
                           employee_locations: List[str] = None,
                           company_description: str = None) -> Dict[str, Any]:
        """
        Score geographic fit based on US presence

        Returns:
            - geographic_score: 0-100 (higher = better US fit)
            - geographic_priority: enum value
            - us_presence_detected: bool
            - red_flags: list of concerns
        """
        score = 50  # neutral baseline
        red_flags = []
        us_presence = False

        # Check data center locations with improved matching
        us_data_centers = []
        international_data_centers = []

        for location in data_center_locations:
            location_lower = location.lower().strip()
            is_us_location = False

            # Check for exact matches or word boundaries for US indicators
            for us_indicator in self.us_indicators:
                # For short abbreviations (2-3 chars), require word boundaries
                if len(us_indicator) <= 3:
                    import re
                    pattern = r'\b' + re.escape(us_indicator) + r'\b'
                    if re.search(pattern, location_lower):
                        is_us_location = True
                        break
                else:
                    # For longer names, allow substring matching but be more careful
                    if us_indicator in location_lower:
                        # Additional check: make sure it's not a false positive
                        # Skip if it's clearly an international location
                        international_keywords = [
                            'iceland', 'sweden', 'norway', 'denmark', 'finland',
                            'germany', 'france', 'uk', 'united kingdom', 'canada',
                            'australia', 'japan', 'singapore', 'ireland'
                        ]
                        if not any(intl in location_lower for intl in international_keywords):
                            is_us_location = True
                            break

            if is_us_location:
                us_data_centers.append(location)
                us_presence = True
            else:
                international_data_centers.append(location)

        # Scoring logic
        if us_data_centers:
            if len(us_data_centers) >= len(international_data_centers):
                # US-primary company
                score = 100
                priority = GeographicPriority.US_PRIMARY
            else:
                # International with US presence
                score = 75
                priority = GeographicPriority.INTERNATIONAL_WITH_US
        else:
            # No US data centers detected
            if international_data_centers:
                score = 25
                priority = GeographicPriority.INTERNATIONAL_ONLY
                red_flags.append(f"No US data center presence detected. Locations: {', '.join(international_data_centers[:3])}")
            else:
                score = 40
                priority = GeographicPriority.INTERNATIONAL_ONLY
                red_flags.append("No clear geographic data center information available")

        # Check employee/office locations if provided
        if employee_locations:
            us_employees = [loc for loc in employee_locations
                          if any(us_indicator in loc.lower() for us_indicator in self.us_indicators)]
            if us_employees:
                us_presence = True
                if not us_data_centers:
                    score += 15  # Boost for US employees even without US data centers
            elif not us_data_centers:
                red_flags.append(f"No US employee presence detected. Employee locations: {', '.join(employee_locations[:3])}")

        # Check company description for US market focus
        if company_description:
            desc_lower = company_description.lower()
            if any(us_indicator in desc_lower for us_indicator in self.us_indicators):
                us_presence = True
                if score < 50:
                    score += 10  # Small boost for US market mentions

        # Final adjustments
        if not us_presence:
            red_flags.append("⚠️ RED FLAG: No US market presence detected - may not align with Verdigris go-to-market focus")

        return {
            'geographic_score': min(100, max(0, score)),
            'geographic_priority': priority,
            'us_presence_detected': us_presence,
            'us_data_centers': us_data_centers,
            'international_data_centers': international_data_centers,
            'red_flags': red_flags,
            'recommendation': self._get_recommendation(priority, us_presence)
        }

    def _get_recommendation(self, priority: GeographicPriority, us_presence: bool) -> str:
        """Get geographic-based sales recommendation"""
        recommendations = {
            GeographicPriority.US_PRIMARY: "✅ IDEAL: Strong US market focus aligns perfectly with Verdigris GTM strategy",
            GeographicPriority.US_SECONDARY: "✅ GOOD: US operations present, good fit for Verdigris expansion",
            GeographicPriority.INTERNATIONAL_WITH_US: "⚠️ CAUTIOUS: US presence detected but international-focused. Evaluate US decision-making authority",
            GeographicPriority.INTERNATIONAL_ONLY: "🚩 DEPRIORITIZE: No clear US presence. Consider only if exceptional strategic value"
        }
        return recommendations.get(priority, "Requires further geographic analysis")

    def update_account_icp_score(self, current_icp_score: float, geographic_score: float) -> float:
        """Update account ICP score with geographic consideration"""
        # Weight geographic scoring as 20% of total ICP fit
        geographic_weight = 0.2
        base_weight = 0.8

        adjusted_score = (current_icp_score * base_weight) + (geographic_score * geographic_weight)
        return min(100, max(0, adjusted_score))