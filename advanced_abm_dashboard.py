#!/usr/bin/env python3
"""
Advanced ABM Dashboard - Next-Level Account-Centric Research Platform
Account-focused navigation with Notion table inspector and research queue management
"""

import os
import json
import time
import threading
from datetime import datetime, timedelta
from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_cors import CORS

# Import existing services
from dashboard_data_service import NotionDataService

app = Flask(__name__)
CORS(app)

# Global state for research queue management
research_queue = {}
active_researches = {}

# Initialize data service
notion_service = NotionDataService()

# ═══════════════════════════════════════════════════════════════════════════════════
# MAIN DASHBOARD ROUTES
# ═══════════════════════════════════════════════════════════════════════════════════

@app.route('/')
@app.route('/dashboard')
def dashboard():
    """Serve the advanced dashboard with account-centric navigation"""
    return send_from_directory('.', 'advanced_dashboard.html')

@app.route('/api/navigation/overview')
def get_navigation_overview():
    """Get high-level navigation data for the sidebar"""
    try:
        # Get all data from Notion
        accounts = notion_service.fetch_accounts()
        contacts = notion_service.fetch_contacts()
        trigger_events = notion_service.fetch_trigger_events()
        partnerships = notion_service.fetch_partnerships()

        # Calculate navigation stats
        nav_data = {
            'global_stats': {
                'total_accounts': len(accounts),
                'total_contacts': len(contacts),
                'active_signals': len([e for e in trigger_events if e.get('urgency_level') in ['High', 'Medium']]),
                'priority_contacts': len([c for c in contacts if c.get('final_lead_score', 0) >= 70]),
                'strategic_partnerships': len(partnerships),
                'research_queue_size': len(research_queue)
            },
            'account_list': [
                {
                    'id': acc.get('id'),
                    'name': acc.get('name', 'Unknown Company'),
                    'domain': acc.get('domain', ''),
                    'icp_fit_score': acc.get('icp_fit_score', 0),
                    'contact_count': len([c for c in contacts if c.get('company_name') == acc.get('name')]),
                    'signal_count': len([e for e in trigger_events if acc.get('name', '').lower() in e.get('event_description', '').lower()]),
                    'research_status': 'completed' if acc.get('research_completed') else 'pending'
                }
                for acc in accounts[:10]  # Top 10 accounts for navigation
            ],
            'recent_signals': [
                {
                    'id': event.get('id'),
                    'company': event.get('company_name', 'Unknown'),
                    'description': event.get('event_description', '')[:100] + '...',
                    'urgency': event.get('urgency_level', 'Low'),
                    'timestamp': event.get('timestamp', ''),
                    'confidence': event.get('confidence_score', 0)
                }
                for event in sorted(trigger_events, key=lambda x: x.get('timestamp', ''), reverse=True)[:5]
            ]
        }

        return jsonify(nav_data)

    except Exception as e:
        print(f"Error fetching navigation overview: {e}")
        return jsonify({'error': str(e)}), 500

# ═══════════════════════════════════════════════════════════════════════════════════
# ACCOUNT-SPECIFIC ROUTES
# ═══════════════════════════════════════════════════════════════════════════════════

@app.route('/api/account/<account_id>')
def get_account_details(account_id):
    """Get comprehensive details for a specific account"""
    try:
        # Get all data
        accounts = notion_service.fetch_accounts()
        contacts = notion_service.fetch_contacts()
        trigger_events = notion_service.fetch_trigger_events()
        partnerships = notion_service.fetch_partnerships()

        # Find the specific account
        account = next((acc for acc in accounts if acc.get('id') == account_id), None)
        if not account:
            return jsonify({'error': 'Account not found'}), 404

        account_name = account.get('name', '')

        # Filter data for this account
        account_contacts = [c for c in contacts if c.get('company_name') == account_name]
        account_signals = [e for e in trigger_events if account_name.lower() in e.get('event_description', '').lower()]
        account_partnerships = [p for p in partnerships if p.get('target_company') == account_name]

        # Build comprehensive account view
        account_data = {
            'account_info': account,
            'contacts': sorted(account_contacts, key=lambda x: x.get('final_lead_score', 0), reverse=True),
            'trigger_events': sorted(account_signals, key=lambda x: x.get('timestamp', ''), reverse=True),
            'partnerships': account_partnerships,
            'research_timeline': _build_research_timeline(account_name, account_contacts, account_signals),
            'next_actions': _generate_next_actions(account, account_contacts, account_signals),
            'research_progress': _calculate_research_progress(account_name)
        }

        return jsonify(account_data)

    except Exception as e:
        print(f"Error fetching account {account_id}: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/account/<account_id>/research/plan', methods=['POST'])
def create_research_plan(account_id):
    """Create a research plan for an account"""
    try:
        data = request.json
        research_phases = data.get('phases', [
            'Contact Discovery',
            'LinkedIn Enrichment',
            'Trigger Event Detection',
            'Partnership Intelligence',
            'Lead Scoring'
        ])

        # Create research plan entry
        plan_id = f"plan_{account_id}_{int(time.time())}"
        research_queue[plan_id] = {
            'account_id': account_id,
            'phases': research_phases,
            'created_at': datetime.now().isoformat(),
            'status': 'queued',
            'progress': 0
        }

        return jsonify({
            'plan_id': plan_id,
            'status': 'created',
            'phases': research_phases
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ═══════════════════════════════════════════════════════════════════════════════════
# NOTION TABLE INSPECTOR ROUTES
# ═══════════════════════════════════════════════════════════════════════════════════

@app.route('/api/notion/tables')
def get_notion_tables():
    """Get list of all Notion tables/databases"""
    try:
        tables_info = {
            'accounts': {
                'name': 'Target Accounts',
                'count': len(notion_service.fetch_accounts()),
                'last_updated': datetime.now().isoformat(),
                'schema': ['name', 'domain', 'icp_fit_score', 'company_size', 'industry']
            },
            'contacts': {
                'name': 'Priority Contacts',
                'count': len(notion_service.fetch_contacts()),
                'last_updated': datetime.now().isoformat(),
                'schema': ['full_name', 'title', 'company_name', 'email', 'final_lead_score']
            },
            'trigger_events': {
                'name': 'Trigger Events',
                'count': len(notion_service.fetch_trigger_events()),
                'last_updated': datetime.now().isoformat(),
                'schema': ['company_name', 'event_description', 'urgency_level', 'confidence_score']
            },
            'partnerships': {
                'name': 'Strategic Partnerships',
                'count': len(notion_service.fetch_partnerships()),
                'last_updated': datetime.now().isoformat(),
                'schema': ['target_company', 'partnership_type', 'verdigris_relevance']
            }
        }

        return jsonify(tables_info)

    except Exception as e:
        print(f"Error fetching table info: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/notion/table/<table_name>')
def get_table_data(table_name):
    """Get full data for a specific Notion table with pagination"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        search = request.args.get('search', '')

        # Fetch table data based on table name
        if table_name == 'accounts':
            data = notion_service.fetch_accounts()
        elif table_name == 'contacts':
            data = notion_service.fetch_contacts()
        elif table_name == 'trigger_events':
            data = notion_service.fetch_trigger_events()
        elif table_name == 'partnerships':
            data = notion_service.fetch_partnerships()
        else:
            return jsonify({'error': 'Table not found'}), 404

        # Apply search filter if provided
        if search:
            search_lower = search.lower()
            data = [item for item in data if any(
                search_lower in str(value).lower()
                for value in item.values()
                if value is not None
            )]

        # Apply pagination
        total_count = len(data)
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_data = data[start_idx:end_idx]

        return jsonify({
            'data': paginated_data,
            'pagination': {
                'page': page,
                'limit': limit,
                'total_count': total_count,
                'total_pages': (total_count + limit - 1) // limit,
                'has_next': end_idx < total_count,
                'has_prev': page > 1
            },
            'search': search
        })

    except Exception as e:
        print(f"Error fetching table {table_name}: {e}")
        return jsonify({'error': str(e)}), 500

# ═══════════════════════════════════════════════════════════════════════════════════
# RESEARCH QUEUE MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════════

@app.route('/api/research/queue')
def get_research_queue():
    """Get current research queue status"""
    return jsonify({
        'queue': research_queue,
        'active': active_researches,
        'completed': _get_completed_research(),
        'stats': {
            'queued': len([q for q in research_queue.values() if q['status'] == 'queued']),
            'active': len(active_researches),
            'completed_today': len(_get_completed_research_today())
        }
    })

@app.route('/api/research/start/<plan_id>', methods=['POST'])
def start_research(plan_id):
    """Start research execution for a queued plan"""
    try:
        if plan_id not in research_queue:
            return jsonify({'error': 'Research plan not found'}), 404

        plan = research_queue[plan_id]
        if plan['status'] != 'queued':
            return jsonify({'error': 'Research plan already processed'}), 400

        # Move to active research
        plan['status'] = 'active'
        plan['started_at'] = datetime.now().isoformat()
        active_researches[plan_id] = plan

        # Start background research thread
        thread = threading.Thread(target=_execute_research_plan, args=(plan_id,))
        thread.start()

        return jsonify({
            'plan_id': plan_id,
            'status': 'started',
            'message': 'Research execution started in background'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ═══════════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════════

def _build_research_timeline(account_name, contacts, signals):
    """Build a comprehensive research timeline for an account"""
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

    # Sort by date (most recent first)
    timeline.sort(key=lambda x: x.get('date', ''), reverse=True)
    return timeline[:20]  # Return last 20 events

def _generate_next_actions(account, contacts, signals):
    """Generate suggested next actions based on account data"""
    actions = []

    # High-priority contacts without recent outreach
    high_value_contacts = [c for c in contacts if c.get('final_lead_score', 0) >= 80]
    if high_value_contacts:
        actions.append({
            'type': 'outreach',
            'priority': 'high',
            'title': f"Reach out to {len(high_value_contacts)} high-value contacts",
            'description': f"Top contact: {high_value_contacts[0].get('full_name', 'Unknown')}",
            'action_url': f"/account/{account.get('id')}/contacts"
        })

    # Recent high-urgency signals
    urgent_signals = [s for s in signals if s.get('urgency_level') == 'High']
    if urgent_signals:
        actions.append({
            'type': 'signal_response',
            'priority': 'urgent',
            'title': f"Respond to {len(urgent_signals)} urgent trigger events",
            'description': urgent_signals[0].get('event_description', 'Unknown event')[:100],
            'action_url': f"/account/{account.get('id')}/signals"
        })

    # Low ICP fit score
    if account.get('icp_fit_score', 0) < 60:
        actions.append({
            'type': 'research',
            'priority': 'medium',
            'title': "Validate ICP fit",
            'description': f"Current fit score: {account.get('icp_fit_score', 0)}%",
            'action_url': f"/account/{account.get('id')}/research"
        })

    return actions

def _calculate_research_progress(account_name):
    """Calculate research completion progress for an account"""
    # Simple heuristic based on data availability
    progress = {
        'overall_completion': 0,
        'phases': {
            'contact_discovery': False,
            'linkedin_enrichment': False,
            'trigger_detection': False,
            'partnership_intel': False,
            'lead_scoring': False
        }
    }

    try:
        contacts = notion_service.fetch_contacts()
        signals = notion_service.fetch_trigger_events()
        partnerships = notion_service.fetch_partnerships()

        account_contacts = [c for c in contacts if c.get('company_name') == account_name]
        account_signals = [s for s in signals if account_name.lower() in s.get('event_description', '').lower()]
        account_partnerships = [p for p in partnerships if p.get('target_company') == account_name]

        # Check phase completion
        if account_contacts:
            progress['phases']['contact_discovery'] = True
            if any(c.get('linkedin_activity_score') for c in account_contacts):
                progress['phases']['linkedin_enrichment'] = True
            if any(c.get('final_lead_score') for c in account_contacts):
                progress['phases']['lead_scoring'] = True

        if account_signals:
            progress['phases']['trigger_detection'] = True

        if account_partnerships:
            progress['phases']['partnership_intel'] = True

        # Calculate overall completion
        completed_phases = sum(progress['phases'].values())
        progress['overall_completion'] = int((completed_phases / 5) * 100)

    except Exception as e:
        print(f"Error calculating research progress: {e}")

    return progress

def _execute_research_plan(plan_id):
    """Execute research plan in background thread"""
    try:
        plan = active_researches.get(plan_id)
        if not plan:
            return

        # Import comprehensive system
        from comprehensive_abm_system import ComprehensiveABMSystem
        abm_system = ComprehensiveABMSystem()

        # Get account info
        accounts = notion_service.fetch_accounts()
        account = next((acc for acc in accounts if acc.get('id') == plan['account_id']), None)

        if account:
            company_name = account.get('name', '')
            domain = account.get('domain', '')

            # Execute research
            abm_system.conduct_complete_account_research(company_name, domain)

            # Mark as completed
            plan['status'] = 'completed'
            plan['completed_at'] = datetime.now().isoformat()
            plan['progress'] = 100

        # Move from active to completed
        if plan_id in active_researches:
            del active_researches[plan_id]

    except Exception as e:
        print(f"Research execution error for plan {plan_id}: {e}")
        if plan_id in active_researches:
            active_researches[plan_id]['status'] = 'failed'
            active_researches[plan_id]['error'] = str(e)

def _get_completed_research():
    """Get list of completed research plans"""
    return [q for q in research_queue.values() if q['status'] == 'completed']

def _get_completed_research_today():
    """Get research completed today"""
    today = datetime.now().date()
    return [
        q for q in research_queue.values()
        if q['status'] == 'completed' and
        q.get('completed_at') and
        datetime.fromisoformat(q['completed_at']).date() == today
    ]

if __name__ == '__main__':
    print("🚀 Starting ADVANCED ABM Dashboard")
    print("🎯 Account-centric research platform with navigation")
    print("🔍 Notion table inspector with live editing")
    print("📋 Research queue management")
    print("💡 Access at: http://localhost:8002")
    app.run(host='0.0.0.0', port=8002, debug=True)