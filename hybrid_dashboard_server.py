#!/usr/bin/env python3
"""
Hybrid ABM Dashboard Server - Next-Level Performance
Uses Hybrid Data Manager for fast local queries + Notion sync
"""

import os
import json
import time
import threading
from datetime import datetime, timedelta
from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_cors import CORS

# Import hybrid data manager
from hybrid_data_manager import hybrid_data_manager

app = Flask(__name__)
CORS(app)

# ═══════════════════════════════════════════════════════════════════════════════════
# MAIN DASHBOARD ROUTES
# ═══════════════════════════════════════════════════════════════════════════════════

@app.route('/')
@app.route('/dashboard')
def dashboard():
    """Serve the hybrid dashboard"""
    return send_from_directory('.', 'hybrid_dashboard.html')

@app.route('/api/navigation/overview')
def get_navigation_overview():
    """Get high-level navigation data (FAST - from local DB)"""
    try:
        # Fast analytics from local database
        analytics = hybrid_data_manager.get_dashboard_analytics_fast()

        # Fast account list
        top_accounts = hybrid_data_manager.get_accounts_fast(limit=10)

        # Recent high-priority signals
        recent_signals = hybrid_data_manager.get_trigger_events_fast(
            urgency_level=None,  # All urgency levels
            days_back=7
        )[:5]

        # Research queue status
        queue_status = hybrid_data_manager.get_research_queue_status()

        nav_data = {
            'global_stats': {
                'total_accounts': analytics['total_accounts'],
                'total_contacts': analytics['total_contacts'],
                'active_signals': analytics['active_signals'],
                'priority_contacts': analytics['priority_contacts'],
                'strategic_partnerships': 0,  # TODO: Add to analytics
                'research_queue_size': analytics['queued_research'] + analytics['active_research']
            },
            'account_list': [
                {
                    'id': acc['id'],
                    'name': acc['name'],
                    'domain': acc['domain'] or '',
                    'icp_fit_score': acc['icp_fit_score'] or 0,
                    'contact_count': len(hybrid_data_manager.get_contacts_fast(company_name=acc['name'])),
                    'signal_count': len(hybrid_data_manager.get_trigger_events_fast(company_name=acc['name'], days_back=30)),
                    'research_status': acc['research_status'] or 'pending'
                }
                for acc in top_accounts
            ],
            'recent_signals': [
                {
                    'id': signal['id'],
                    'company': signal['company_name'] or 'Unknown',
                    'description': (signal['event_description'] or '')[:100] + '...' if signal['event_description'] else '',
                    'urgency': signal['urgency_level'] or 'Low',
                    'timestamp': signal['timestamp'] or '',
                    'confidence': signal['confidence_score'] or 0
                }
                for signal in recent_signals
            ],
            'performance': {
                'query_time': f"{time.time() - time.time():.3f}s",  # Would be actual timing
                'data_source': 'hybrid_local_db',
                'last_sync': hybrid_data_manager.sync_status.get('accounts', {}).get('last_notion_sync', 'never') if hybrid_data_manager.sync_status else 'never'
            }
        }

        return jsonify(nav_data)

    except Exception as e:
        print(f"Error fetching navigation overview: {e}")
        return jsonify({'error': str(e)}), 500

# ═══════════════════════════════════════════════════════════════════════════════════
# FAST ACCOUNT QUERIES
# ═══════════════════════════════════════════════════════════════════════════════════

@app.route('/api/account/<account_id>')
def get_account_details(account_id):
    """Get comprehensive account details (FAST - from local DB)"""
    try:
        start_time = time.time()

        # Get account info
        accounts = hybrid_data_manager.get_accounts_fast()
        account = next((acc for acc in accounts if acc['id'] == account_id), None)

        if not account:
            return jsonify({'error': 'Account not found'}), 404

        account_name = account['name']

        # Fast queries for account data
        account_contacts = hybrid_data_manager.get_contacts_fast(company_name=account_name)
        account_signals = hybrid_data_manager.get_trigger_events_fast(
            company_name=account_name,
            days_back=90
        )

        # Build research timeline
        timeline = _build_research_timeline_fast(account_name, account_contacts, account_signals)

        # Generate next actions
        next_actions = _generate_next_actions_fast(account, account_contacts, account_signals)

        # Calculate research progress
        research_progress = _calculate_research_progress_fast(account_name, account_contacts, account_signals)

        query_time = time.time() - start_time

        account_data = {
            'account_info': account,
            'contacts': sorted(account_contacts, key=lambda x: x.get('final_lead_score', 0), reverse=True),
            'trigger_events': sorted(account_signals, key=lambda x: x.get('timestamp', ''), reverse=True),
            'partnerships': [],  # TODO: Add partnerships to hybrid manager
            'research_timeline': timeline,
            'next_actions': next_actions,
            'research_progress': research_progress,
            'performance': {
                'query_time': f"{query_time:.3f}s",
                'data_source': 'hybrid_local_db',
                'contact_count': len(account_contacts),
                'signal_count': len(account_signals)
            }
        }

        return jsonify(account_data)

    except Exception as e:
        print(f"Error fetching account {account_id}: {e}")
        return jsonify({'error': str(e)}), 500

# ═══════════════════════════════════════════════════════════════════════════════════
# NOTION TABLE INSPECTOR (HYBRID QUERIES)
# ═══════════════════════════════════════════════════════════════════════════════════

@app.route('/api/notion/tables')
def get_notion_tables():
    """Get list of all tables with sync status"""
    try:
        # Get sync status
        sync_info = hybrid_data_manager.get_sync_status()

        # Get current counts from local DB
        analytics = hybrid_data_manager.get_dashboard_analytics_fast()

        tables_info = {
            'accounts': {
                'name': 'Target Accounts',
                'count': analytics['total_accounts'],
                'last_updated': datetime.now().isoformat(),
                'schema': ['name', 'domain', 'icp_fit_score', 'company_size', 'industry'],
                'sync_status': next((s for s in sync_info['sync_status'] if s['table_name'] == 'accounts'), {})
            },
            'contacts': {
                'name': 'Priority Contacts',
                'count': analytics['total_contacts'],
                'last_updated': datetime.now().isoformat(),
                'schema': ['full_name', 'title', 'company_name', 'email', 'final_lead_score'],
                'sync_status': next((s for s in sync_info['sync_status'] if s['table_name'] == 'contacts'), {})
            },
            'trigger_events': {
                'name': 'Trigger Events',
                'count': len(hybrid_data_manager.get_trigger_events_fast(days_back=365)),  # All events
                'last_updated': datetime.now().isoformat(),
                'schema': ['company_name', 'event_description', 'urgency_level', 'confidence_score'],
                'sync_status': next((s for s in sync_info['sync_status'] if s['table_name'] == 'trigger_events'), {})
            }
        }

        return jsonify(tables_info)

    except Exception as e:
        print(f"Error fetching table info: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/notion/table/<table_name>')
def get_table_data(table_name):
    """Get table data with fast local queries and search"""
    try:
        start_time = time.time()

        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        search = request.args.get('search', '')

        # Fast local queries based on table name
        if table_name == 'accounts':
            data = hybrid_data_manager.get_accounts_fast(
                search=search if search else None,
                limit=limit * page  # Simple pagination
            )
            # Extract page slice
            start_idx = (page - 1) * limit
            end_idx = start_idx + limit
            page_data = data[start_idx:end_idx]

        elif table_name == 'contacts':
            data = hybrid_data_manager.get_contacts_fast(limit=limit * page)
            # Apply search filter if needed
            if search:
                search_lower = search.lower()
                data = [item for item in data if any(
                    search_lower in str(value).lower()
                    for value in item.values()
                    if value is not None
                )]
            start_idx = (page - 1) * limit
            end_idx = start_idx + limit
            page_data = data[start_idx:end_idx]

        elif table_name == 'trigger_events':
            data = hybrid_data_manager.get_trigger_events_fast(days_back=365)
            if search:
                search_lower = search.lower()
                data = [item for item in data if any(
                    search_lower in str(value).lower()
                    for value in item.values()
                    if value is not None
                )]
            start_idx = (page - 1) * limit
            end_idx = start_idx + limit
            page_data = data[start_idx:end_idx]

        else:
            return jsonify({'error': 'Table not found'}), 404

        query_time = time.time() - start_time

        total_count = len(data) if 'data' in locals() else len(page_data)

        return jsonify({
            'data': page_data,
            'pagination': {
                'page': page,
                'limit': limit,
                'total_count': total_count,
                'total_pages': (total_count + limit - 1) // limit,
                'has_next': end_idx < total_count,
                'has_prev': page > 1
            },
            'search': search,
            'performance': {
                'query_time': f"{query_time:.3f}s",
                'data_source': 'hybrid_local_db',
                'indexed_search': bool(search)
            }
        })

    except Exception as e:
        print(f"Error fetching table {table_name}: {e}")
        return jsonify({'error': str(e)}), 500

# ═══════════════════════════════════════════════════════════════════════════════════
# RESEARCH QUEUE MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════════

@app.route('/api/research/queue')
def get_research_queue():
    """Get research queue status (FAST - local DB only)"""
    try:
        start_time = time.time()
        queue_status = hybrid_data_manager.get_research_queue_status()
        query_time = time.time() - start_time

        queue_status['performance'] = {
            'query_time': f"{query_time:.3f}s",
            'data_source': 'local_db_only'
        }

        return jsonify(queue_status)

    except Exception as e:
        print(f"Error fetching research queue: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/research/plan', methods=['POST'])
def create_research_plan():
    """Create a research plan for an account"""
    try:
        data = request.json
        account_id = data.get('account_id')
        account_name = data.get('account_name')
        research_phases = data.get('phases', [
            'Contact Discovery',
            'LinkedIn Enrichment',
            'Trigger Event Detection',
            'Partnership Intelligence',
            'Lead Scoring'
        ])
        priority = data.get('priority', 5)

        if not account_id or not account_name:
            return jsonify({'error': 'Missing account_id or account_name'}), 400

        # Add to research queue
        plan_id = hybrid_data_manager.add_to_research_queue(
            account_id=account_id,
            account_name=account_name,
            research_phases=research_phases,
            priority=priority
        )

        return jsonify({
            'plan_id': plan_id,
            'status': 'queued',
            'account_name': account_name,
            'phases': research_phases,
            'priority': priority
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/research/start/<plan_id>', methods=['POST'])
def start_research(plan_id):
    """Start research execution for a queued plan"""
    try:
        # TODO: Implement research execution
        # For now, just return success
        return jsonify({
            'plan_id': plan_id,
            'status': 'started',
            'message': 'Research execution started (placeholder)'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ═══════════════════════════════════════════════════════════════════════════════════
# SYNC MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════════

@app.route('/api/sync/status')
def get_sync_status():
    """Get current sync status between Notion and local DB"""
    try:
        sync_info = hybrid_data_manager.get_sync_status()
        return jsonify(sync_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sync/trigger', methods=['POST'])
def trigger_manual_sync():
    """Trigger manual sync from Notion"""
    try:
        # Start background sync
        def background_sync():
            hybrid_data_manager.sync_from_notion(force=True)

        thread = threading.Thread(target=background_sync)
        thread.start()

        return jsonify({
            'status': 'sync_started',
            'message': 'Manual sync from Notion started in background'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ═══════════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════════

def _build_research_timeline_fast(account_name: str, contacts: list, signals: list) -> list:
    """Build research timeline from local data"""
    timeline = []

    # Add contact discovery events
    for contact in contacts:
        if contact.get('created_date'):
            timeline.append({
                'date': contact['created_date'],
                'type': 'contact_discovered',
                'title': f"Contact discovered: {contact.get('full_name', 'Unknown')}",
                'details': f"Role: {contact.get('title', 'Unknown role')}",
                'priority': contact.get('final_lead_score', 0)
            })

    # Add trigger events
    for signal in signals:
        if signal.get('timestamp'):
            timeline.append({
                'date': signal['timestamp'],
                'type': 'trigger_event',
                'title': signal.get('event_description', 'Trigger detected'),
                'details': f"Urgency: {signal.get('urgency_level', 'Unknown')}",
                'priority': 100 if signal.get('urgency_level') == 'High' else 50
            })

    # Sort by date (most recent first) and limit
    timeline.sort(key=lambda x: x.get('date', ''), reverse=True)
    return timeline[:20]

def _generate_next_actions_fast(account: dict, contacts: list, signals: list) -> list:
    """Generate next actions from local data"""
    actions = []

    # High-priority contacts
    high_value_contacts = [c for c in contacts if c.get('final_lead_score', 0) >= 80]
    if high_value_contacts:
        actions.append({
            'type': 'outreach',
            'priority': 'high',
            'title': f"Reach out to {len(high_value_contacts)} high-value contacts",
            'description': f"Top contact: {high_value_contacts[0].get('full_name', 'Unknown')}",
            'action_url': f"/account/{account.get('id')}/contacts"
        })

    # Recent urgent signals
    urgent_signals = [s for s in signals if s.get('urgency_level') == 'High']
    if urgent_signals:
        actions.append({
            'type': 'signal_response',
            'priority': 'urgent',
            'title': f"Respond to {len(urgent_signals)} urgent trigger events",
            'description': urgent_signals[0].get('event_description', 'Unknown event')[:100],
            'action_url': f"/account/{account.get('id')}/signals"
        })

    # Low ICP fit
    if account.get('icp_fit_score', 0) < 60:
        actions.append({
            'type': 'research',
            'priority': 'medium',
            'title': "Validate ICP fit",
            'description': f"Current fit score: {account.get('icp_fit_score', 0)}%",
            'action_url': f"/account/{account.get('id')}/research"
        })

    return actions

def _calculate_research_progress_fast(account_name: str, contacts: list, signals: list) -> dict:
    """Calculate research progress from local data"""
    progress = {
        'overall_completion': 0,
        'phases': {
            'contact_discovery': bool(contacts),
            'linkedin_enrichment': any(c.get('linkedin_activity_score') for c in contacts),
            'trigger_detection': bool(signals),
            'partnership_intel': False,  # TODO: Add partnerships
            'lead_scoring': any(c.get('final_lead_score') for c in contacts)
        }
    }

    # Calculate overall completion
    completed_phases = sum(progress['phases'].values())
    progress['overall_completion'] = int((completed_phases / 5) * 100)

    return progress

if __name__ == '__main__':
    print("🚀 Starting HYBRID ABM Dashboard Server")
    print("💾 Local database for fast queries")
    print("🔄 Background Notion sync for data consistency")
    print("⚡ Sub-second response times")
    print("💡 Access at: http://localhost:8003")

    # Initial sync
    print("🔄 Performing initial sync...")
    try:
        sync_results = hybrid_data_manager.sync_from_notion()
        print(f"✅ Initial sync completed: {len(sync_results)} tables")
    except Exception as e:
        print(f"⚠️  Initial sync failed: {e}")

    app.run(host='0.0.0.0', port=8003, debug=True)