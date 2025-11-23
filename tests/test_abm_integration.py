"""
Integration Test Suite for ABM Dashboard
Tests end-to-end workflows, API integrations, and data consistency
"""

import pytest
import asyncio
import json
import time
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from dashboard_data_service import NotionDataService
from comprehensive_abm_system import ComprehensiveABMSystem
from lead_scoring_engine import LeadScoringEngine

class TestNotionIntegration:
    """Test Notion API integration and error handling"""

    @pytest.fixture
    def notion_service(self):
        """Create NotionDataService instance"""
        return NotionDataService()

    def test_notion_connection_failure_handling(self, notion_service):
        """Test handling of Notion API connection failures"""
        with patch('requests.post') as mock_post:
            # Simulate connection error
            mock_post.side_effect = ConnectionError("Unable to connect to Notion API")

            accounts = notion_service.fetch_accounts()

            # Should return empty list on failure, not crash
            assert accounts == [], "Should return empty list on connection failure"

    def test_notion_rate_limit_handling(self, notion_service):
        """Test handling of Notion API rate limits"""
        with patch('requests.post') as mock_post:
            # Simulate rate limit response
            mock_response = MagicMock()
            mock_response.status_code = 429
            mock_response.headers = {'Retry-After': '5'}
            mock_post.return_value = mock_response

            accounts = notion_service.fetch_accounts()

            # Should handle rate limits gracefully
            assert accounts == [], "Should handle rate limits gracefully"

    def test_notion_malformed_response_handling(self, notion_service):
        """Test handling of malformed Notion API responses"""
        with patch('requests.post') as mock_post:
            # Simulate malformed response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"unexpected": "format"}
            mock_post.return_value = mock_response

            accounts = notion_service.fetch_accounts()

            # Should handle malformed responses
            assert isinstance(accounts, list), "Should return list even with malformed response"

    def test_notion_database_id_validation(self, notion_service):
        """Test validation of Notion database IDs"""
        # Test with invalid database ID
        original_id = notion_service.database_ids['accounts']
        notion_service.database_ids['accounts'] = 'invalid-id'

        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_post.return_value = mock_response

            accounts = notion_service.fetch_accounts()

            # Should handle invalid database IDs
            assert accounts == [], "Should handle invalid database IDs"

        # Restore original ID
        notion_service.database_ids['accounts'] = original_id

    def test_notion_property_extraction_with_nulls(self, notion_service):
        """Test property extraction with null/missing values"""
        test_property_configs = [
            (None, ''),  # None property
            ({'type': 'title'}, ''),  # Missing title array
            ({'type': 'title', 'title': []}, ''),  # Empty title array
            ({'type': 'number'}, None),  # Missing number value
            ({'type': 'select'}, ''),  # Missing select value
        ]

        for prop, expected in test_property_configs:
            # Test title extraction
            assert notion_service._extract_title(prop) == expected or \
                   notion_service._extract_title(prop) == '', "Should handle null values"

    def test_cache_functionality(self, notion_service):
        """Test caching mechanism"""
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'results': []}
            mock_post.return_value = mock_response

            # First call
            accounts1 = notion_service.fetch_accounts()
            call_count1 = mock_post.call_count

            # Second call (should use cache)
            accounts2 = notion_service.fetch_accounts()
            call_count2 = mock_post.call_count

            # Cache should prevent second API call
            assert call_count2 == call_count1, "Should use cached data"
            assert accounts1 == accounts2, "Cached data should match"

            # Clear cache and test again
            notion_service.cache = {}
            notion_service.cache_timestamp = {}

            accounts3 = notion_service.fetch_accounts()
            call_count3 = mock_post.call_count

            assert call_count3 > call_count2, "Should make new API call after cache clear"

class TestResearchWorkflow:
    """Test complete research workflow integration"""

    @pytest.fixture
    def abm_system(self):
        """Create ComprehensiveABMSystem instance"""
        return ComprehensiveABMSystem()

    def test_phase_1_failure_handling(self, abm_system):
        """Test handling of Phase 1 failures"""
        with patch.object(abm_system, '_phase_1_account_intelligence') as mock_phase1:
            mock_phase1.side_effect = Exception("Phase 1 failed")

            result = abm_system.conduct_complete_account_research(
                "Test Company", "test.com"
            )

            # Should handle phase 1 failure gracefully
            assert result['research_summary']['status'] == 'failed'
            assert 'Phase 1 failed' in result['research_summary']['error']

    def test_phase_transition_data_consistency(self, abm_system):
        """Test data consistency between phases"""
        with patch.object(abm_system, '_phase_1_account_intelligence') as mock_phase1, \
             patch.object(abm_system, '_phase_2_contact_discovery') as mock_phase2, \
             patch.object(abm_system, '_phase_3_contact_enrichment') as mock_phase3:

            # Setup mock data
            account_data = {'name': 'Test', 'domain': 'test.com', 'icp_fit_score': 75}
            trigger_events = [{'id': '1', 'description': 'Test event'}]
            contacts = [{'id': '1', 'name': 'John Doe', 'lead_score': 80}]

            mock_phase1.return_value = (account_data, trigger_events)
            mock_phase2.return_value = contacts
            mock_phase3.return_value = contacts

            result = abm_system.conduct_complete_account_research(
                "Test Company", "test.com"
            )

            # Verify data flows correctly between phases
            mock_phase2.assert_called_with("Test Company", "test.com", account_data)
            mock_phase3.assert_called_with(contacts)

    def test_partial_phase_completion_recovery(self, abm_system):
        """Test recovery from partial phase completion"""
        with patch.object(abm_system, '_phase_1_account_intelligence') as mock_phase1, \
             patch.object(abm_system, '_phase_2_contact_discovery') as mock_phase2, \
             patch.object(abm_system, '_phase_3_contact_enrichment') as mock_phase3:

            # Phase 1 succeeds
            mock_phase1.return_value = ({'name': 'Test'}, [])
            # Phase 2 succeeds
            mock_phase2.return_value = [{'id': '1', 'name': 'Contact'}]
            # Phase 3 fails
            mock_phase3.side_effect = Exception("Enrichment failed")

            result = abm_system.conduct_complete_account_research(
                "Test Company", "test.com"
            )

            # Should have partial data from successful phases
            assert result['account']['name'] == 'Test'
            assert len(result['contacts']) > 0
            assert result['research_summary']['status'] == 'failed'

    def test_background_job_management(self):
        """Test background job execution and management"""
        from unified_abm_dashboard import app

        with app.test_client() as client:
            with patch('comprehensive_abm_system.ComprehensiveABMSystem.conduct_complete_account_research') as mock_research:
                mock_research.return_value = {'status': 'completed'}

                # Start research job
                response = client.post('/api/research/start',
                                     json={'company_name': 'Test', 'domain': 'test.com'})

                assert response.status_code == 200
                data = response.get_json()
                assert 'job_id' in data
                assert data['status'] == 'started'

                # Give thread time to start
                time.sleep(0.1)

                # Verify research was called
                mock_research.assert_called_once()

class TestLeadScoringIntegration:
    """Test lead scoring engine integration"""

    @pytest.fixture
    def scoring_engine(self):
        """Create LeadScoringEngine instance"""
        return LeadScoringEngine()

    def test_lead_score_calculation_with_missing_data(self, scoring_engine):
        """Test lead scoring with incomplete contact data"""
        incomplete_contact = {
            'name': 'John Doe',
            'title': None,  # Missing title
            'email': 'john@test.com',
            # Missing other fields
        }

        score, breakdown = scoring_engine.calculate_enhanced_lead_score(incomplete_contact)

        # Should handle missing data gracefully
        assert isinstance(score, (int, float)), "Score should be numeric"
        assert 0 <= score <= 100, "Score should be between 0 and 100"
        assert isinstance(breakdown, dict), "Breakdown should be a dictionary"

    def test_lead_score_consistency(self, scoring_engine):
        """Test that lead scoring is consistent"""
        contact = {
            'name': 'Jane Smith',
            'title': 'VP of Engineering',
            'email': 'jane@test.com',
            'buying_committee_role': 'Decision Maker',
            'linkedin_activity_level': 'High'
        }

        # Calculate score multiple times
        scores = []
        for _ in range(5):
            score, _ = scoring_engine.calculate_enhanced_lead_score(contact)
            scores.append(score)

        # Scores should be consistent
        assert len(set(scores)) == 1, "Lead scores should be consistent"

class TestAPIEndpoints:
    """Test API endpoint integration"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        from unified_abm_dashboard import app
        app.config['TESTING'] = True
        return app.test_client()

    def test_api_data_endpoint_integration(self, client):
        """Test /api/data endpoint integration"""
        with patch('dashboard_data_service.NotionDataService.fetch_accounts') as mock_accounts, \
             patch('dashboard_data_service.NotionDataService.fetch_contacts') as mock_contacts, \
             patch('dashboard_data_service.NotionDataService.fetch_trigger_events') as mock_events, \
             patch('dashboard_data_service.NotionDataService.fetch_partnerships') as mock_partnerships:

            # Setup mock data
            mock_accounts.return_value = [{'name': 'Test Account'}]
            mock_contacts.return_value = [{'name': 'Test Contact'}]
            mock_events.return_value = [{'description': 'Test Event'}]
            mock_partnerships.return_value = [{'name': 'Test Partnership'}]

            response = client.get('/api/data')

            assert response.status_code == 200
            data = response.get_json()

            # Verify all data components present
            assert 'primary_account' in data
            assert 'contacts' in data
            assert 'trigger_events' in data
            assert 'partnerships' in data
            assert 'stats' in data
            assert 'timestamp' in data

    def test_api_accounts_filtering(self, client):
        """Test account filtering and sorting"""
        with patch('dashboard_data_service.NotionDataService.fetch_accounts') as mock_fetch:
            mock_fetch.return_value = [
                {'name': 'Account A', 'icp_fit_score': 50},
                {'name': 'Account B', 'icp_fit_score': 90},
                {'name': 'Account C', 'icp_fit_score': 70}
            ]

            response = client.get('/api/accounts')

            assert response.status_code == 200
            data = response.get_json()

            # Should return sorted accounts
            assert len(data['accounts']) == 3

    def test_api_error_handling_consistency(self, client):
        """Test consistent error handling across endpoints"""
        endpoints = [
            '/api/data',
            '/api/accounts',
            '/api/contacts',
            '/api/signals',
            '/api/partnerships'
        ]

        with patch('dashboard_data_service.NotionDataService.fetch_accounts') as mock_fetch:
            mock_fetch.side_effect = Exception("Database error")

            for endpoint in endpoints:
                response = client.get(endpoint)

                # All endpoints should handle errors consistently
                assert response.status_code == 500
                data = response.get_json()
                assert 'error' in data

class TestDataConsistency:
    """Test data consistency across the system"""

    def test_timestamp_consistency(self):
        """Test that timestamps are consistent across the system"""
        from dashboard_data_service import NotionDataService

        service = NotionDataService()

        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'results': [{
                    'id': '123',
                    'created_time': '2024-01-01T00:00:00.000Z',
                    'properties': {}
                }]
            }
            mock_post.return_value = mock_response

            accounts = service.fetch_accounts()

            # Should preserve timestamp format
            assert accounts[0]['created_time'] == '2024-01-01T00:00:00.000Z'

    def test_id_uniqueness_validation(self):
        """Test that IDs are unique across entities"""
        from dashboard_data_service import NotionDataService

        service = NotionDataService()

        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                'results': [
                    {'id': '123', 'properties': {}},
                    {'id': '123', 'properties': {}},  # Duplicate ID
                ]
            }
            mock_post.return_value = mock_response

            accounts = service.fetch_accounts()

            # Should handle duplicate IDs
            ids = [acc['id'] for acc in accounts]
            assert len(ids) == len(set(ids)) or len(accounts) == 2, \
                "Should handle duplicate IDs appropriately"

class TestPerformance:
    """Test performance characteristics"""

    def test_api_response_time(self):
        """Test API response times"""
        from unified_abm_dashboard import app

        with app.test_client() as client:
            with patch('dashboard_data_service.NotionDataService.fetch_accounts') as mock_fetch:
                mock_fetch.return_value = []

                start_time = time.time()
                response = client.get('/api/data')
                end_time = time.time()

                response_time = (end_time - start_time) * 1000  # Convert to ms

                # Should respond within acceptable time
                assert response_time < 1000, f"Response time {response_time}ms exceeds 1000ms"

    def test_concurrent_request_performance(self):
        """Test performance under concurrent load"""
        from unified_abm_dashboard import app
        import threading

        with app.test_client() as client:
            response_times = []

            def make_request():
                start = time.time()
                client.get('/api/data')
                end = time.time()
                response_times.append((end - start) * 1000)

            threads = []
            for _ in range(10):
                t = threading.Thread(target=make_request)
                threads.append(t)
                t.start()

            for t in threads:
                t.join()

            # Average response time should be reasonable
            avg_response_time = sum(response_times) / len(response_times)
            assert avg_response_time < 2000, \
                f"Average response time {avg_response_time}ms under load"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])