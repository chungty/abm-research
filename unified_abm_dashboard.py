#!/usr/bin/env python3
"""
Unified ABM Dashboard - ONE SINGLE DASHBOARD
Combines all the best features into a single, working system
"""

import os
import json
import time
import threading
from datetime import datetime
from flask import Flask, jsonify, render_template, send_from_directory
from flask_cors import CORS
from concurrent.futures import ThreadPoolExecutor
import queue

# Import existing data service
from dashboard_data_service import NotionDataService

app = Flask(__name__)
CORS(app)

# Initialize data service
notion_service = NotionDataService()

# Thread safety components
research_lock = threading.Lock()
active_research_threads = {}
research_results = {}
max_concurrent_research = 3

# Thread pool for managing background research
research_executor = ThreadPoolExecutor(
    max_workers=max_concurrent_research,
    thread_name_prefix="ABMResearch"
)

@app.route('/')
@app.route('/dashboard')
def dashboard():
    """Serve the unified dashboard"""
    return send_from_directory('.', 'unified_dashboard.html')

@app.route('/api/data')
def get_dashboard_data():
    """Get all dashboard data in one call"""
    try:
        # Get all data from Notion
        accounts = notion_service.fetch_accounts()
        contacts = notion_service.fetch_contacts()
        trigger_events = notion_service.fetch_trigger_events()
        partnerships = notion_service.fetch_partnerships()

        # Find primary account
        primary_account = accounts[0] if accounts else {
            'name': 'No accounts found',
            'domain': '',
            'icp_fit_score': 0
        }

        # Calculate stats
        stats = {
            'total_contacts': len(contacts),
            'hot_signals': len([e for e in trigger_events if e.get('urgency_level') == 'High']),
            'priority_contacts': len([c for c in contacts if c.get('final_lead_score', 0) >= 70]),
            'active_triggers': len(trigger_events),
            'strategic_partners': len(partnerships)
        }

        return jsonify({
            'primary_account': primary_account,
            'contacts': contacts,
            'trigger_events': trigger_events,
            'partnerships': partnerships,
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        print(f"Error fetching dashboard data: {e}")
        return jsonify({'error': str(e)}), 500

# Navigation Views
@app.route('/api/accounts')
def get_accounts():
    """Get all target accounts"""
    try:
        accounts = notion_service.fetch_accounts()
        return jsonify({'accounts': accounts})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts')
def get_contacts():
    """Get all priority contacts"""
    try:
        contacts = notion_service.fetch_contacts()
        return jsonify({'contacts': contacts})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/signals')
def get_signals():
    """Get all buying signals"""
    try:
        signals = notion_service.fetch_trigger_events()
        return jsonify({'signals': signals})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/partnerships')
def get_partnerships():
    """Get all strategic partnerships"""
    try:
        partnerships = notion_service.fetch_partnerships()
        return jsonify({'partnerships': partnerships})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/research/start', methods=['POST'])
def start_research():
    """Start ABM research for a new account"""
    from flask import request
    import re

    try:
        # Validate request content type
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400

        data = request.json
        if not data:
            return jsonify({'error': 'Missing request body'}), 400

        company_name = data.get('company_name')
        domain = data.get('domain')

        # Basic presence validation
        if not company_name or not domain:
            return jsonify({'error': 'Missing company name or domain'}), 400

        # Input validation and sanitization
        # Company name validation
        if not isinstance(company_name, str):
            return jsonify({'error': 'Company name must be a string'}), 400

        company_name = company_name.strip()
        if len(company_name) < 2:
            return jsonify({'error': 'Company name must be at least 2 characters'}), 400
        if len(company_name) > 100:
            return jsonify({'error': 'Company name must be less than 100 characters'}), 400

        # Allow letters, numbers, spaces, hyphens, periods, apostrophes, ampersands
        if not re.match(r"^[a-zA-Z0-9\s\-\.'&]+$", company_name):
            return jsonify({'error': 'Company name contains invalid characters'}), 400

        # Domain validation
        if not isinstance(domain, str):
            return jsonify({'error': 'Domain must be a string'}), 400

        domain = domain.strip().lower()
        if len(domain) < 4:
            return jsonify({'error': 'Domain must be at least 4 characters'}), 400
        if len(domain) > 255:
            return jsonify({'error': 'Domain must be less than 255 characters'}), 400

        # Basic domain format validation (RFC-compliant)
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$'
        if not re.match(domain_pattern, domain):
            return jsonify({'error': 'Invalid domain format'}), 400

        # Generate unique research key for deduplication
        research_key = f"{domain.lower()}_{company_name.lower().replace(' ', '_')}"
        job_id = f"research_{int(time.time())}_{hash(research_key) % 10000}"

        # Thread-safe check for existing research
        with research_lock:
            # Check if research is already in progress for this account
            if research_key in active_research_threads:
                existing_job = active_research_threads[research_key]
                if existing_job['status'] in ['running', 'queued']:
                    return jsonify({
                        'job_id': existing_job['job_id'],
                        'status': 'already_running',
                        'message': f'Research already in progress for {company_name}',
                        'company_name': company_name
                    })

            # Create research job metadata
            research_job = {
                'job_id': job_id,
                'company_name': company_name,
                'domain': domain,
                'research_key': research_key,
                'status': 'queued',
                'created_at': datetime.now().isoformat(),
                'started_at': None,
                'completed_at': None,
                'error': None,
                'progress': 0
            }

            # Register the research job
            active_research_threads[research_key] = research_job

        # Define thread-safe research execution function
        def execute_research_safely():
            try:
                # Update status to running
                with research_lock:
                    if research_key in active_research_threads:
                        active_research_threads[research_key]['status'] = 'running'
                        active_research_threads[research_key]['started_at'] = datetime.now().isoformat()

                # Import and execute research
                from comprehensive_abm_system import ComprehensiveABMSystem
                comprehensive_abm_system = ComprehensiveABMSystem()

                # Conduct research with progress tracking
                research_result = comprehensive_abm_system.conduct_complete_account_research(
                    company_name, domain
                )

                # Update completion status
                with research_lock:
                    if research_key in active_research_threads:
                        active_research_threads[research_key]['status'] = 'completed'
                        active_research_threads[research_key]['completed_at'] = datetime.now().isoformat()
                        active_research_threads[research_key]['progress'] = 100
                        research_results[research_key] = research_result

                print(f"✅ Research completed successfully for {company_name}")

            except Exception as e:
                error_msg = str(e)
                print(f"❌ Research error for {company_name}: {error_msg}")

                # Update error status
                with research_lock:
                    if research_key in active_research_threads:
                        active_research_threads[research_key]['status'] = 'error'
                        active_research_threads[research_key]['error'] = error_msg
                        active_research_threads[research_key]['completed_at'] = datetime.now().isoformat()

            finally:
                # Clean up thread reference after delay to allow status checking
                def cleanup_thread():
                    time.sleep(300)  # Keep result for 5 minutes
                    with research_lock:
                        if research_key in active_research_threads:
                            if active_research_threads[research_key]['status'] in ['completed', 'error']:
                                del active_research_threads[research_key]
                        if research_key in research_results:
                            del research_results[research_key]

                cleanup_thread = threading.Thread(target=cleanup_thread)
                cleanup_thread.daemon = True
                cleanup_thread.start()

        # Submit research to thread pool
        try:
            future = research_executor.submit(execute_research_safely)

            # Store future reference for potential cancellation
            with research_lock:
                active_research_threads[research_key]['future'] = future

            return jsonify({
                'job_id': job_id,
                'status': 'started',
                'company_name': company_name,
                'message': f'ABM research initiated for {company_name}'
            })

        except Exception as e:
            # Thread pool is full or other error
            with research_lock:
                if research_key in active_research_threads:
                    del active_research_threads[research_key]

            return jsonify({
                'error': f'Failed to start research: {str(e)}',
                'job_id': job_id,
                'status': 'failed'
            }), 503

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/research/status/<job_id>')
def get_research_status(job_id):
    """Get status of a specific research job"""
    try:
        with research_lock:
            # Find job by job_id across all research keys
            for research_key, job_info in active_research_threads.items():
                if job_info['job_id'] == job_id:
                    return jsonify({
                        'job_id': job_id,
                        'status': job_info['status'],
                        'company_name': job_info['company_name'],
                        'progress': job_info.get('progress', 0),
                        'created_at': job_info['created_at'],
                        'started_at': job_info.get('started_at'),
                        'completed_at': job_info.get('completed_at'),
                        'error': job_info.get('error')
                    })

        return jsonify({'error': 'Research job not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/research/active')
def get_active_research():
    """Get all active research operations"""
    try:
        with research_lock:
            active_jobs = []
            for research_key, job_info in active_research_threads.items():
                job_copy = job_info.copy()
                # Remove future object which is not JSON serializable
                job_copy.pop('future', None)
                active_jobs.append(job_copy)

            return jsonify({
                'active_jobs': active_jobs,
                'total_active': len(active_jobs),
                'max_concurrent': max_concurrent_research
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/research/cancel/<job_id>', methods=['POST'])
def cancel_research(job_id):
    """Cancel a running research job"""
    try:
        with research_lock:
            # Find and cancel job
            for research_key, job_info in active_research_threads.items():
                if job_info['job_id'] == job_id:
                    if job_info['status'] in ['queued', 'running']:
                        # Cancel the future if available
                        future = job_info.get('future')
                        if future and not future.done():
                            future.cancel()

                        # Update status
                        job_info['status'] = 'cancelled'
                        job_info['completed_at'] = datetime.now().isoformat()
                        job_info['error'] = 'Cancelled by user request'

                        return jsonify({
                            'job_id': job_id,
                            'status': 'cancelled',
                            'message': f'Research job {job_id} has been cancelled'
                        })
                    else:
                        return jsonify({
                            'error': f'Cannot cancel job in {job_info["status"]} state'
                        }), 400

        return jsonify({'error': 'Research job not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/research/cleanup', methods=['POST'])
def cleanup_completed_research():
    """Clean up completed and failed research jobs"""
    try:
        cleaned_count = 0
        with research_lock:
            keys_to_remove = []
            for research_key, job_info in active_research_threads.items():
                if job_info['status'] in ['completed', 'error', 'cancelled']:
                    keys_to_remove.append(research_key)

            for key in keys_to_remove:
                del active_research_threads[key]
                if key in research_results:
                    del research_results[key]
                cleaned_count += 1

        return jsonify({
            'message': f'Cleaned up {cleaned_count} completed research jobs',
            'cleaned_count': cleaned_count
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def cleanup_on_shutdown():
    """Clean up thread pool on application shutdown"""
    try:
        print("🧹 Shutting down research thread pool...")
        research_executor.shutdown(wait=True, timeout=30)
        print("✅ Thread pool shutdown complete")
    except Exception as e:
        print(f"❌ Error during thread pool shutdown: {e}")

import atexit
atexit.register(cleanup_on_shutdown)

if __name__ == '__main__':
    print("🚀 Starting UNIFIED ABM Dashboard")
    print("📊 One dashboard with all features combined")
    print("💡 Access at: http://localhost:8001")
    app.run(host='0.0.0.0', port=8001, debug=True)