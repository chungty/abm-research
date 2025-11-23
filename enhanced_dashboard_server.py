#!/usr/bin/env python3
"""
Enhanced ABM Dashboard Server - Premium Verdigris Edition
Integrates all advanced ABM intelligence modules with premium dark mode UI
"""

import os
import json
import time
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

# Import our enhanced ABM intelligence modules
try:
    from enhanced_buying_signals_analyzer import EnhancedBuyingSignalsAnalyzer
    from contact_value_analyzer import ContactValueAnalyzer
    from enhanced_account_plan_generator import EnhancedAccountPlanGenerator
    from dashboard_data_service import DashboardDataService
except ImportError as e:
    print(f"⚠️  Warning: Could not import some ABM modules: {e}")
    print("📊 Dashboard will run with mock data")

app = Flask(__name__)
CORS(app)

# Initialize ABM intelligence services
try:
    buying_signals_analyzer = EnhancedBuyingSignalsAnalyzer()
    contact_value_analyzer = ContactValueAnalyzer()
    account_plan_generator = EnhancedAccountPlanGenerator()
    data_service = DashboardDataService()

    services_available = True
    print("✅ ABM Intelligence Services Initialized")
except Exception as e:
    print(f"⚠️  Warning: Could not initialize ABM services: {e}")
    services_available = False

# Cache for dashboard data
dashboard_cache = {
    'data': None,
    'last_updated': None,
    'cache_duration': 300  # 5 minutes
}

@app.route('/')
@app.route('/dashboard')
def dashboard():
    """Serve the premium Verdigris ABM dashboard"""
    return send_from_directory('.', 'verdigris_sales_dashboard.html')

@app.route('/api/dashboard/enhanced')
def get_enhanced_dashboard_data():
    """Get comprehensive dashboard data with enhanced intelligence"""
    try:
        # Check cache
        if (dashboard_cache['data'] and dashboard_cache['last_updated'] and
            time.time() - dashboard_cache['last_updated'] < dashboard_cache['cache_duration']):
            return jsonify(dashboard_cache['data'])

        start_time = time.time()

        if services_available:
            # Get real data from our enhanced services
            dashboard_data = get_real_dashboard_data()
        else:
            # Fallback to enhanced mock data
            dashboard_data = get_enhanced_mock_data()

        # Update cache
        dashboard_cache['data'] = dashboard_data
        dashboard_cache['last_updated'] = time.time()

        query_time = time.time() - start_time
        dashboard_data['meta'] = {
            'query_time': round(query_time, 3),
            'cache_updated': datetime.now().isoformat(),
            'services_available': services_available
        }

        return jsonify(dashboard_data)

    except Exception as e:
        print(f"❌ Error generating dashboard data: {e}")
        return jsonify({'error': str(e), 'fallback': True}), 500

def get_real_dashboard_data():
    """Get real dashboard data from enhanced ABM services"""

    # Get accounts from data service
    accounts = data_service.get_accounts_with_contacts()[:10]  # Top 10 accounts
    all_contacts = []
    all_signals = []

    enhanced_contacts = []
    enhanced_signals = []
    account_plans = []

    for account in accounts:
        try:
            company_name = account.get('name', '')

            # Get contacts for this account
            contacts = data_service.get_contacts_for_account(company_name)
            all_contacts.extend(contacts)

            # Analyze contact value for high-ICP contacts
            if contacts:
                contact_analysis = contact_value_analyzer.analyze_contacts(contacts)
                high_value_contacts = [
                    contact for contact in contact_analysis.contacts
                    if contact.value_score >= 70
                ]
                enhanced_contacts.extend([
                    {
                        'name': contact.basic_info.name,
                        'title': contact.basic_info.title,
                        'company': contact.basic_info.company,
                        'final_lead_score': int(contact.value_score),
                        'tier': f"Tier {contact.tier}",
                        'verdigris_relevance': contact.role_analysis.verdigris_fit_reasoning[:100] + "..." if contact.role_analysis.verdigris_fit_reasoning else "Standard profile"
                    } for contact in high_value_contacts[:5]  # Top 5 per account
                ])

            # Get buying signals
            signals = data_service.get_trigger_events_for_account(company_name, days_back=30)
            all_signals.extend(signals)

            # Analyze buying signals with enhanced intelligence
            if signals:
                signals_analysis = buying_signals_analyzer.analyze_company_signals(company_name, signals)
                enhanced_signals.extend([
                    {
                        'company': signal.company_name,
                        'description': signal.event_description,
                        'urgency': signal.priority.priority_level.title(),
                        'confidence': int(signal.confidence_score),
                        'source_url': getattr(signal, 'source_url', '#'),
                        'timestamp': signal.priority.time_sensitivity,
                        'trend': signal.trend.trend_direction if signal.trend else 'Stable'
                    } for signal in signals_analysis.enhanced_signals[:3]  # Top 3 per account
                ])

            # Generate enhanced account plan
            try:
                account_plan = account_plan_generator.generate_enhanced_account_plan(
                    account, contacts, signals
                )
                if account_plan:
                    account_plans.append({
                        'company': company_name,
                        'confidence': f"{int(account_plan.confidence_score)}%",
                        'summary': account_plan.executive_summary[:200] + "..." if account_plan.executive_summary else "Strategic analysis pending",
                        'actions': [action.action_type for action in account_plan.recommended_actions[:4]],
                        'icp_composition': {
                            'fit_percentage': int(account_plan.icp_composition.overall_fit_score),
                            'key_strengths': account_plan.icp_composition.key_strengths[:3],
                            'growth_indicators': len(account_plan.icp_composition.growth_indicators)
                        } if account_plan.icp_composition else None
                    })
            except Exception as e:
                print(f"⚠️  Warning: Could not generate account plan for {company_name}: {e}")

        except Exception as e:
            print(f"⚠️  Warning: Error processing account {company_name}: {e}")
            continue

    # Get partnerships data
    partnerships = data_service.get_strategic_partnerships()[:10]

    # Calculate analytics
    analytics = {
        'total_accounts': len(accounts),
        'priority_contacts': len(enhanced_contacts),
        'active_signals': len(enhanced_signals),
        'partnership_opportunities': len(partnerships),
        'total_contacts': len(all_contacts),
        'total_signals': len(all_signals)
    }

    return {
        'analytics': analytics,
        'contacts': enhanced_contacts[:15],  # Top 15 contacts
        'signals': enhanced_signals[:10],    # Top 10 signals
        'account_plans': account_plans[:5],  # Top 5 account plans
        'partnerships': [
            {
                'company': p.get('partner_name', 'Unknown'),
                'relationship': p.get('relationship_type', 'Partner'),
                'opportunity': p.get('opportunity_description', 'Strategic collaboration')[:100] + "...",
                'relevance': p.get('verdigris_relevance', 'Medium'),
                'technologies': p.get('technologies_used', [])[:3]
            } for p in partnerships
        ],
        'accounts': [
            {
                'name': account.get('name', ''),
                'status': 'Active',
                'contact_count': len([c for c in all_contacts if c.get('company') == account.get('name', '')]),
                'signal_count': len([s for s in all_signals if s.get('company_name') == account.get('name', '')]),
                'last_activity': 'Recent'
            } for account in accounts
        ]
    }

def get_enhanced_mock_data():
    """Enhanced mock data for demonstration"""
    return {
        'analytics': {
            'total_accounts': 7,
            'priority_contacts': 18,
            'active_signals': 12,
            'partnership_opportunities': 15,
            'total_contacts': 45,
            'total_signals': 28
        },
        'contacts': [
            {
                'name': "Sarah Chen",
                'title': "VP of Engineering",
                'company': "Genesis Cloud",
                'final_lead_score': 89,
                'tier': "Tier 1",
                'verdigris_relevance': "High infrastructure spend, GPU optimization focus, energy efficiency initiatives"
            },
            {
                'name': "Marcus Rodriguez",
                'title': "Head of Data Science",
                'company': "DataBricks",
                'final_lead_score': 82,
                'tier': "Tier 1",
                'verdigris_relevance': "ML infrastructure optimization, cost reduction focus, scalability challenges"
            },
            {
                'name': "Emily Zhang",
                'title': "CTO",
                'company': "Anthropic",
                'final_lead_score': 94,
                'tier': "Tier 1",
                'verdigris_relevance': "AI training infrastructure needs, energy-efficient computing research"
            },
            {
                'name': "David Kim",
                'title': "Director of Infrastructure",
                'company': "Scale AI",
                'final_lead_score': 76,
                'tier': "Tier 1",
                'verdigris_relevance': "Data labeling infrastructure, GPU cluster optimization"
            },
            {
                'name': "Lisa Martinez",
                'title': "VP of Operations",
                'company': "Cohere",
                'final_lead_score': 71,
                'tier': "Tier 2",
                'verdigris_relevance': "NLP model training infrastructure, cost optimization initiatives"
            }
        ],
        'signals': [
            {
                'company': "Genesis Cloud",
                'description': "Announced $25M Series B funding round for GPU infrastructure expansion",
                'urgency': "High",
                'confidence': 92,
                'source_url': "https://techcrunch.com/genesis-funding-series-b",
                'timestamp': "2 hours ago",
                'trend': "Growing"
            },
            {
                'company': "DataBricks",
                'description': "Posted 15+ infrastructure engineering positions focused on ML optimization",
                'urgency': "High",
                'confidence': 78,
                'source_url': "https://linkedin.com/jobs/databricks-infrastructure",
                'timestamp': "4 hours ago",
                'trend': "Accelerating"
            },
            {
                'company': "Anthropic",
                'description': "Published research on energy-efficient AI training methodologies",
                'urgency': "Medium",
                'confidence': 85,
                'source_url': "https://anthropic.com/research/energy-efficient-training",
                'timestamp': "1 day ago",
                'trend': "Stable"
            },
            {
                'company': "Scale AI",
                'description': "Migrating data labeling infrastructure to reduce operational costs",
                'urgency': "Medium",
                'confidence': 73,
                'source_url': "https://scale.com/blog/infrastructure-optimization",
                'timestamp': "2 days ago",
                'trend': "Growing"
            },
            {
                'company': "Cohere",
                'description': "Expanding model training capabilities, seeking infrastructure partnerships",
                'urgency': "Medium",
                'confidence': 67,
                'source_url': "https://cohere.ai/blog/infrastructure-expansion",
                'timestamp': "3 days ago",
                'trend': "Growing"
            }
        ],
        'account_plans': [
            {
                'company': "Genesis Cloud",
                'confidence': "89%",
                'summary': "High-growth GPU cloud provider with strong infrastructure needs. Recent funding indicates expansion plans. Focus on energy efficiency and cost optimization aligns with Verdigris solutions.",
                'actions': ["Energy Audit", "GPU Optimization Analysis", "Cost Reduction Strategy", "Partnership Discussion"],
                'icp_composition': {
                    'fit_percentage': 92,
                    'key_strengths': ["High Infrastructure Spend", "GPU-Heavy Workloads", "Growth Stage"],
                    'growth_indicators': 5
                }
            },
            {
                'company': "DataBricks",
                'confidence': "82%",
                'summary': "Enterprise data platform expanding ML infrastructure. Heavy hiring in infrastructure roles indicates growth and optimization needs. Strong fit for energy monitoring solutions.",
                'actions': ["ML Infrastructure Assessment", "Data Center Efficiency", "Partnership Exploration", "Pilot Program"],
                'icp_composition': {
                    'fit_percentage': 85,
                    'key_strengths': ["Enterprise Scale", "ML Focus", "Infrastructure Investment"],
                    'growth_indicators': 4
                }
            },
            {
                'company': "Anthropic",
                'confidence': "94%",
                'summary': "Leading AI safety company with significant training infrastructure needs. Research focus on energy efficiency creates strong alignment with Verdigris mission and values.",
                'actions': ["Research Collaboration", "Energy Efficiency Partnership", "Custom Solution Development", "Long-term Agreement"],
                'icp_composition': {
                    'fit_percentage': 96,
                    'key_strengths': ["AI Training Focus", "Energy Efficiency Research", "Premium Brand"],
                    'growth_indicators': 6
                }
            }
        ],
        'partnerships': [
            {
                'company': "NVIDIA",
                'relationship': "Technology Partner",
                'opportunity': "Joint development of GPU energy optimization solutions for AI workloads",
                'relevance': "High",
                'technologies': ["GPU", "AI Training", "Energy Management"]
            },
            {
                'company': "AWS",
                'relationship': "Cloud Marketplace Partner",
                'opportunity': "Integration with AWS energy monitoring and optimization services",
                'relevance': "High",
                'technologies': ["Cloud Infrastructure", "Energy Monitoring", "Cost Optimization"]
            },
            {
                'company': "Google Cloud",
                'relationship': "Strategic Partner",
                'opportunity': "Carbon-neutral infrastructure initiatives and energy efficiency programs",
                'relevance': "High",
                'technologies': ["Sustainable Computing", "Carbon Tracking", "Energy Optimization"]
            },
            {
                'company': "Microsoft Azure",
                'relationship': "Technology Integration",
                'opportunity': "Azure Marketplace integration for enterprise energy monitoring solutions",
                'relevance': "Medium",
                'technologies': ["Enterprise Solutions", "Energy Analytics", "Cloud Integration"]
            }
        ],
        'accounts': [
            {'name': "Genesis Cloud", 'status': "Active", 'contact_count': 8, 'signal_count': 3, 'last_activity': "2 hours ago"},
            {'name': "DataBricks", 'status': "Active", 'contact_count': 12, 'signal_count': 5, 'last_activity': "4 hours ago"},
            {'name': "Anthropic", 'status': "Active", 'contact_count': 6, 'signal_count': 2, 'last_activity': "1 day ago"},
            {'name': "Scale AI", 'status': "Active", 'contact_count': 9, 'signal_count': 4, 'last_activity': "2 days ago"},
            {'name': "Cohere", 'status': "Active", 'contact_count': 7, 'signal_count': 3, 'last_activity': "3 days ago"},
            {'name': "Hugging Face", 'status': "Active", 'contact_count': 5, 'signal_count': 2, 'last_activity': "1 week ago"},
            {'name': "Stability AI", 'status': "Active", 'contact_count': 4, 'signal_count': 1, 'last_activity': "1 week ago"}
        ]
    }

@app.route('/api/account-plans/generate', methods=['POST'])
def generate_account_plan():
    """Generate enhanced account plan for specific company"""
    try:
        data = request.get_json() or {}
        company_name = data.get('company')

        if not company_name:
            return jsonify({'error': 'Company name required'}), 400

        if services_available and account_plan_generator:
            # Get real account data
            account = data_service.get_account_by_name(company_name)
            contacts = data_service.get_contacts_for_account(company_name)
            signals = data_service.get_trigger_events_for_account(company_name)

            # Generate enhanced plan
            plan = account_plan_generator.generate_enhanced_account_plan(
                account, contacts, signals
            )

            return jsonify({
                'company': company_name,
                'plan': plan.to_dict() if plan else None,
                'generated_at': datetime.now().isoformat()
            })
        else:
            # Return mock plan
            return jsonify({
                'company': company_name,
                'plan': f"Enhanced account plan for {company_name} - Full integration pending",
                'generated_at': datetime.now().isoformat(),
                'status': 'mock_data'
            })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<contact_name>')
def get_contact_details(contact_name):
    """Get detailed contact information"""
    try:
        if services_available:
            # Get real contact data
            contact = data_service.get_contact_by_name(contact_name)
            if contact:
                # Analyze contact value
                analysis = contact_value_analyzer.analyze_contact(contact)
                return jsonify({
                    'contact': contact,
                    'analysis': analysis.to_dict() if analysis else None
                })

        return jsonify({
            'contact': contact_name,
            'status': 'Details coming soon',
            'mock_data': True
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/signals/<signal_id>')
def get_signal_details(signal_id):
    """Get detailed buying signal information"""
    try:
        return jsonify({
            'signal_id': signal_id,
            'status': 'Signal details coming soon',
            'mock_data': True
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'services_available': services_available,
        'timestamp': datetime.now().isoformat(),
        'cache_status': 'warm' if dashboard_cache['data'] else 'cold'
    })

@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    """Clear dashboard cache"""
    dashboard_cache['data'] = None
    dashboard_cache['last_updated'] = None
    return jsonify({'status': 'cache_cleared', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    print("🚀 Starting Enhanced ABM Dashboard Server")
    print("💎 Premium Verdigris Edition")
    print("=" * 50)

    if services_available:
        print("✅ Full ABM Intelligence Services Active")
        print("   • Enhanced Buying Signals Analysis")
        print("   • Contact Value Analysis")
        print("   • Account Plan Generation")
        print("   • Real-time Data Integration")
    else:
        print("⚠️  Running with Mock Data")
        print("   • Install ABM modules for full functionality")

    print("\n🌐 Dashboard URLs:")
    print("   • Main Dashboard: http://localhost:8006/dashboard")
    print("   • Health Check:  http://localhost:8006/api/health")
    print("   • API Docs:      http://localhost:8006/api/dashboard/enhanced")
    print("=" * 50)

    app.run(host='0.0.0.0', port=8006, debug=False)