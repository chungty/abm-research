"""
Secure Notion API Proxy Server
Backend to fetch Notion data and serve to frontend - XSS safe
"""
import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

class NotionProxyHandler(BaseHTTPRequestHandler):
    """HTTP request handler for Notion API proxy"""

    def __init__(self, *args, **kwargs):
        self.api_key = os.getenv('NOTION_ABM_API_KEY')
        self.database_ids = {
            'accounts': '2b27f5fe-e5e2-8129-a865-f052744f9fcc',
            'trigger_events': '2b27f5fe-e5e2-81b5-a20e-c35e17d500c7',
            'contacts': '2b27f5fe-e5e2-818d-988c-e8dd53d4d172',
            'partnerships': '2b27f5fe-e5e2-8179-83f0-dec272ec1856'
        }
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET requests"""
        try:
            parsed_url = urlparse(self.path)

            # Enable CORS
            self.send_response(200)
            self.send_header('Content-Type', 'application/json' if parsed_url.path.startswith('/api') else 'text/html')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()

            if parsed_url.path == '/api/abm-data':
                # Fetch all ABM data
                data = self.fetch_abm_data()
                self.wfile.write(json.dumps(data, indent=2).encode())
            elif parsed_url.path == '/' or parsed_url.path == '/dashboard':
                # Serve the secure dashboard HTML
                self.serve_dashboard()
            else:
                self.send_error(404, "Not Found")

        except Exception as e:
            self.send_error(500, f"Server Error: {str(e)}")

    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def serve_dashboard(self):
        """Serve the secure dashboard HTML"""
        # Read the secure dashboard template
        dashboard_file = Path(__file__).parent / 'secure_dashboard.html'
        if dashboard_file.exists():
            with open(dashboard_file, 'r') as f:
                html_content = f.read()
        else:
            html_content = self.get_default_dashboard()

        self.wfile.write(html_content.encode())

    def get_default_dashboard(self):
        """Get default dashboard HTML (XSS safe - no innerHTML usage)"""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Center Command Center - ABM Intelligence</title>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root {
            --dark-bg: #0B1426; --darker-bg: #061018; --accent-blue: #00D4FF;
            --accent-green: #00FFB3; --accent-orange: #FF8A00; --accent-red: #FF4757;
            --text-primary: #FFFFFF; --text-secondary: #8B9DC3; --text-muted: #5A6B85;
            --border-color: #1E293B; --card-bg: #0F1B2E; --hover-bg: #1E293B;
        }
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, var(--dark-bg) 0%, var(--darker-bg) 100%);
            color: var(--text-primary); min-height: 100vh; line-height: 1.6;
        }
        .header { padding: 2rem; border-bottom: 2px solid var(--border-color);
            background: rgba(11, 20, 38, 0.95); backdrop-filter: blur(10px); }
        .header h1 { font-family: 'JetBrains Mono', monospace; font-size: 2.5rem; font-weight: 700;
            background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-green) 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; margin-bottom: 0.5rem; }
        .subtitle { text-align: center; color: var(--text-secondary); font-size: 1.1rem; }
        .loading { display: flex; justify-content: center; align-items: center; min-height: 400px;
            color: var(--accent-blue); font-family: 'JetBrains Mono', monospace; }
        .spinner { border: 4px solid var(--border-color); border-top: 4px solid var(--accent-blue);
            border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin-right: 1rem; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .dashboard { padding: 2rem; max-width: 1400px; margin: 0 auto; }
        .success-message { background: rgba(0, 255, 179, 0.1); border: 1px solid var(--accent-green);
            color: var(--accent-green); padding: 1rem; border-radius: 8px; margin: 1rem 0;
            font-family: 'JetBrains Mono', monospace; }
        .account-header { background: linear-gradient(135deg, var(--card-bg) 0%, #1a2332 100%);
            border: 1px solid var(--border-color); border-radius: 12px; padding: 2rem; margin-bottom: 2rem;
            position: relative; overflow: hidden; }
        .account-header::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px;
            background: linear-gradient(90deg, var(--accent-blue) 0%, var(--accent-green) 100%); }
        .account-info { display: grid; grid-template-columns: 1fr auto auto; gap: 2rem; align-items: center; }
        .account-details h2 { font-family: 'JetBrains Mono', monospace; font-size: 1.8rem;
            color: var(--text-primary); margin-bottom: 0.5rem; }
        .account-meta { display: flex; gap: 1rem; color: var(--text-secondary); font-size: 0.9rem; }
        .icp-score { background: linear-gradient(135deg, var(--accent-green), #00CC88);
            padding: 0.75rem 1.5rem; border-radius: 8px; text-align: center; }
        .icp-score .score { font-family: 'JetBrains Mono', monospace; font-size: 2rem;
            font-weight: 700; display: block; }
        .icp-score .label { font-size: 0.8rem; opacity: 0.9; }
        .status-badge { padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.8rem;
            font-weight: 600; font-family: 'JetBrains Mono', monospace;
            background: rgba(0, 255, 179, 0.15); color: var(--accent-green); border: 1px solid var(--accent-green); }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-bottom: 2rem; }
        .card { background: linear-gradient(135deg, var(--card-bg) 0%, #1a2332 100%);
            border: 1px solid var(--border-color); border-radius: 12px; padding: 1.5rem;
            transition: transform 0.3s ease, box-shadow 0.3s ease; }
        .card:hover { transform: translateY(-4px); box-shadow: 0 8px 32px rgba(0, 212, 255, 0.1); }
        .card-header { display: flex; align-items: center; justify-content: space-between;
            margin-bottom: 1.5rem; padding-bottom: 0.75rem; border-bottom: 1px solid var(--border-color); }
        .card-title { font-family: 'JetBrains Mono', monospace; font-size: 1.1rem;
            font-weight: 600; color: var(--text-primary); }
        .card-count { background: var(--accent-blue); color: var(--dark-bg); padding: 0.25rem 0.75rem;
            border-radius: 12px; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; font-weight: 600; }
        .item { background: rgba(139, 157, 195, 0.05); border: 1px solid var(--border-color);
            border-radius: 8px; padding: 1rem; margin-bottom: 1rem; transition: background-color 0.3s ease; }
        .item:hover { background: rgba(139, 157, 195, 0.1); }
        .contact-card { background: linear-gradient(135deg, rgba(139, 157, 195, 0.08) 0%, rgba(30, 41, 59, 0.1) 100%);
            border: 1px solid var(--border-color); border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem;
            transition: all 0.3s ease; }
        .contact-card:hover { background: linear-gradient(135deg, rgba(139, 157, 195, 0.12) 0%, rgba(30, 41, 59, 0.15) 100%);
            transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0, 212, 255, 0.1); }
        .contact-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; }
        .contact-name { font-family: 'JetBrains Mono', monospace; font-size: 1.1rem; font-weight: 600;
            color: var(--text-primary); }
        .contact-title { color: var(--text-secondary); font-size: 0.9rem; margin-bottom: 0.5rem; }
        .contact-role { margin-bottom: 1rem; }
        .score-breakdown { background: rgba(0, 0, 0, 0.2); border: 1px solid var(--border-color);
            border-radius: 8px; padding: 1rem; margin-bottom: 1rem; }
        .score-header { font-family: 'JetBrains Mono', monospace; font-size: 1rem; margin-bottom: 0.75rem;
            color: var(--text-primary); }
        .score-details { margin-left: 0.5rem; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; }
        .score-component { color: var(--text-secondary); margin-bottom: 0.25rem; }
        .score-explanation { margin-top: 0.75rem; padding-top: 0.75rem; border-top: 1px solid var(--border-color); }
        .explanation-title { color: var(--text-primary); font-weight: 600; margin-bottom: 0.5rem; font-size: 0.85rem; }
        .explanation-item { color: var(--text-secondary); font-size: 0.8rem; margin-bottom: 0.25rem; }
        .contact-actions { display: flex; gap: 0.75rem; flex-wrap: wrap; }
        .action-btn { padding: 0.5rem 1rem; border-radius: 6px; border: none; font-size: 0.8rem; font-weight: 600;
            font-family: 'JetBrains Mono', monospace; cursor: pointer; transition: all 0.3s ease; }
        .call-btn { background: var(--accent-blue); color: var(--dark-bg); }
        .call-btn:hover { background: #00c4ef; transform: scale(1.05); }
        .email-btn { background: var(--accent-green); color: var(--dark-bg); }
        .email-btn:hover { background: #00e9a3; transform: scale(1.05); }
        .casestudy-btn { background: var(--accent-orange); color: var(--dark-bg); }
        .casestudy-btn:hover { background: #ff7a00; transform: scale(1.05); }
        .priority-1 { background: var(--accent-red); color: white; padding: 0.25rem 0.75rem; border-radius: 12px;
            font-size: 0.7rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
        .priority-2 { background: var(--accent-orange); color: white; padding: 0.25rem 0.75rem; border-radius: 12px;
            font-size: 0.7rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
        .priority-3 { background: var(--text-muted); color: white; padding: 0.25rem 0.75rem; border-radius: 12px;
            font-size: 0.7rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
        .sales-intelligence { background: rgba(0, 212, 255, 0.05); border: 1px solid rgba(0, 212, 255, 0.2);
            border-radius: 8px; padding: 1rem; margin-bottom: 1rem; }
        .intelligence-section { margin-bottom: 1rem; }
        .intelligence-section:last-child { margin-bottom: 0; }
        .intelligence-title { font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; font-weight: 600;
            color: var(--accent-blue); margin-bottom: 0.5rem; }
        .intelligence-item { font-size: 0.85rem; margin-bottom: 0.25rem; line-height: 1.4; }
        .urgency-item { color: var(--accent-red); font-weight: 500; }
        .pain-item { color: var(--text-secondary); }
        .value-item { color: var(--accent-green); }
        .opening-line { font-style: italic; color: var(--text-primary); background: rgba(0, 0, 0, 0.3);
            padding: 0.75rem; border-radius: 6px; margin-top: 0.5rem; font-size: 0.9rem; line-height: 1.5; }
        .badge { padding: 0.25rem 0.75rem; border-radius: 12px; font-size: 0.75rem;
            font-weight: 600; font-family: 'JetBrains Mono', monospace; margin-bottom: 0.5rem;
            display: inline-block; background: rgba(0, 212, 255, 0.2); color: var(--accent-blue); }
        .description { margin-bottom: 0.5rem; color: var(--text-primary); }
        .meta { display: flex; justify-content: space-between; font-size: 0.8rem; color: var(--text-muted); }
        .name { font-weight: 600; color: var(--text-primary); margin-bottom: 0.25rem; }
        .title { font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 0.5rem; }
        .score { float: right; font-family: 'JetBrains Mono', monospace; color: var(--accent-blue); }
        .opportunity { font-size: 0.9rem; color: var(--text-secondary); margin-top: 0.5rem; }
        .action { margin-top: 0.5rem; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem;
            color: var(--accent-orange); }
        @media (max-width: 768px) {
            .grid { grid-template-columns: 1fr; }
            .account-info { grid-template-columns: 1fr; text-align: center; gap: 1rem; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>DATA CENTER COMMAND CENTER</h1>
        <p class="subtitle">Account-Based Marketing Intelligence • Live Data from Notion</p>
    </div>

    <div class="dashboard">
        <div id="loading" class="loading">
            <div class="spinner"></div>
            <div>Loading live data from Notion databases...</div>
        </div>

        <div id="content" style="display: none;">
            <div class="success-message">
                ✅ Successfully connected to Notion databases! Data is live and updating.
            </div>

            <div class="account-header">
                <div class="account-info">
                    <div class="account-details">
                        <h2 id="account-name">Loading...</h2>
                        <div class="account-meta">
                            <span id="account-domain">Loading...</span>
                            <span id="account-employees">Loading...</span>
                            <span id="account-model">Loading...</span>
                        </div>
                    </div>
                    <div class="icp-score">
                        <span class="score" id="icp-score">--</span>
                        <span class="label">ICP FIT</span>
                    </div>
                    <div class="status-badge" id="research-status">Loading</div>
                </div>
            </div>

            <div class="grid">
                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">TRIGGER EVENTS</h3>
                        <span class="card-count" id="events-count">0</span>
                    </div>
                    <div id="trigger-events"></div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <h3 class="card-title">HIGH-PRIORITY CONTACTS</h3>
                        <span class="card-count" id="contacts-count">0</span>
                    </div>
                    <div id="contacts"></div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">STRATEGIC PARTNERSHIPS</h3>
                    <span class="card-count" id="partnerships-count">0</span>
                </div>
                <div id="partnerships"></div>
            </div>
        </div>
    </div>

    <script>
        // XSS-safe DOM helper functions - only using safe methods
        function createSecureElement(tag, className, textContent) {
            const element = document.createElement(tag);
            if (className) element.className = className;
            if (textContent) element.textContent = textContent;
            return element;
        }

        function clearContainer(container) {
            while (container.firstChild) {
                container.removeChild(container.firstChild);
            }
        }

        function populateAccount(account) {
            document.getElementById('account-name').textContent = account.name || 'Unknown';
            document.getElementById('account-domain').textContent = account.domain || '';
            document.getElementById('account-employees').textContent = (account.employees || 0) + ' employees';
            document.getElementById('account-model').textContent = account.model || '';
            document.getElementById('icp-score').textContent = account.icpScore || '--';
            document.getElementById('research-status').textContent = account.status || 'Unknown';
        }

        function populateEvents(events) {
            const container = document.getElementById('trigger-events');
            const count = document.getElementById('events-count');

            count.textContent = events.length;
            clearContainer(container);

            events.forEach(event => {
                const eventDiv = createSecureElement('div', 'item');

                const typeSpan = createSecureElement('span', 'badge', event.type || 'Unknown');
                const descDiv = createSecureElement('div', 'description', event.description || 'No description');
                const metaDiv = createSecureElement('div', 'meta');

                const confSpan = createSecureElement('span', '', 'Confidence: ' + (event.confidence || 'Unknown'));
                const relSpan = createSecureElement('span', '', 'Relevance: ' + (event.relevanceScore || 0) + '%');

                metaDiv.appendChild(confSpan);
                metaDiv.appendChild(relSpan);

                eventDiv.appendChild(typeSpan);
                eventDiv.appendChild(descDiv);
                eventDiv.appendChild(metaDiv);

                container.appendChild(eventDiv);
            });
        }

        function populateContacts(contacts) {
            const container = document.getElementById('contacts');
            const count = document.getElementById('contacts-count');

            count.textContent = contacts.length;
            clearContainer(container);

            contacts.forEach(contact => {
                const contactCard = createSecureElement('div', 'contact-card');

                // Header with name and priority
                const headerDiv = createSecureElement('div', 'contact-header');
                const nameDiv = createSecureElement('div', 'contact-name', contact.name || 'Unknown');
                const priorityBadge = createSecureElement('span', getPriorityClass(contact.leadScore || 0),
                    (contact.leadScore >= 90) ? 'PRIORITY 1' :
                    (contact.leadScore >= 75) ? 'PRIORITY 2' : 'PRIORITY 3');

                headerDiv.appendChild(nameDiv);
                headerDiv.appendChild(priorityBadge);

                // Title and role
                const titleDiv = createSecureElement('div', 'contact-title', contact.title || 'Unknown Title');
                const roleSpan = createSecureElement('span', 'contact-role badge', contact.role || 'Unknown Role');

                // Scoring breakdown using safe DOM methods
                const scoreSection = createSecureElement('div', 'score-breakdown');
                const scoreHeader = createSecureElement('div', 'score-header');

                // Build score header safely
                const scoreLabel = createSecureElement('span', '', 'Lead Score: ');
                const scoreValue = createSecureElement('strong', '', String(contact.leadScore || 0));
                const scoreStars = createSecureElement('span', '', ' ' + getScoreStars(contact.leadScore || 0));
                scoreHeader.appendChild(scoreLabel);
                scoreHeader.appendChild(scoreValue);
                scoreHeader.appendChild(scoreStars);

                // Score breakdown details
                const breakdown = createSecureElement('div', 'score-details');
                if (contact.scoringBreakdown) {
                    const icpDiv = createSecureElement('div', 'score-component');
                    const icpPrefix = createSecureElement('span', '', '├─ ICP Fit: ');
                    const icpScore = createSecureElement('strong', '', (contact.scoringBreakdown.icpScore || 0) + '/100');
                    icpDiv.appendChild(icpPrefix);
                    icpDiv.appendChild(icpScore);

                    const buyingDiv = createSecureElement('div', 'score-component');
                    const buyingPrefix = createSecureElement('span', '', '├─ Buying Power: ');
                    const buyingScore = createSecureElement('strong', '', (contact.scoringBreakdown.buyingPower || 0) + '/100');
                    buyingDiv.appendChild(buyingPrefix);
                    buyingDiv.appendChild(buyingScore);

                    const engageDiv = createSecureElement('div', 'score-component');
                    const engagePrefix = createSecureElement('span', '', '└─ Engagement: ');
                    const engageScore = createSecureElement('strong', '', (contact.scoringBreakdown.engagementScore || 0) + '/100');
                    engageDiv.appendChild(engagePrefix);
                    engageDiv.appendChild(engageScore);

                    breakdown.appendChild(icpDiv);
                    breakdown.appendChild(buyingDiv);
                    breakdown.appendChild(engageDiv);

                    // Explanation list
                    if (contact.scoringBreakdown.explanation && contact.scoringBreakdown.explanation.length > 0) {
                        const explanationDiv = createSecureElement('div', 'score-explanation');
                        const explanationTitle = createSecureElement('div', 'explanation-title', 'Why this score:');
                        explanationDiv.appendChild(explanationTitle);

                        contact.scoringBreakdown.explanation.forEach(reason => {
                            const reasonDiv = createSecureElement('div', 'explanation-item', reason);
                            explanationDiv.appendChild(reasonDiv);
                        });
                        breakdown.appendChild(explanationDiv);
                    }
                }

                scoreSection.appendChild(scoreHeader);
                scoreSection.appendChild(breakdown);

                // Sales Intelligence Section
                const intelligenceSection = createSecureElement('div', 'sales-intelligence');

                if (contact.salesIntelligence) {
                    const intel = contact.salesIntelligence;

                    // Why call now
                    if (intel.whyCallNow && intel.whyCallNow.length > 0) {
                        const whySection = createSecureElement('div', 'intelligence-section');
                        const whyTitle = createSecureElement('div', 'intelligence-title', '🔥 WHY CALL NOW:');
                        whySection.appendChild(whyTitle);

                        intel.whyCallNow.forEach(reason => {
                            const reasonDiv = createSecureElement('div', 'intelligence-item urgency-item', '• ' + reason);
                            whySection.appendChild(reasonDiv);
                        });
                        intelligenceSection.appendChild(whySection);
                    }

                    // Pain points
                    if (intel.painPoints && intel.painPoints.length > 0) {
                        const painSection = createSecureElement('div', 'intelligence-section');
                        const painTitle = createSecureElement('div', 'intelligence-title', '💡 PAIN POINTS THEY LIKELY OWN:');
                        painSection.appendChild(painTitle);

                        intel.painPoints.slice(0, 4).forEach(pain => {
                            const painDiv = createSecureElement('div', 'intelligence-item pain-item', '• ' + pain);
                            painSection.appendChild(painDiv);
                        });
                        intelligenceSection.appendChild(painSection);
                    }

                    // Opening line
                    if (intel.openingLine) {
                        const openingSection = createSecureElement('div', 'intelligence-section');
                        const openingTitle = createSecureElement('div', 'intelligence-title', '💬 OPENING LINE:');
                        const openingText = createSecureElement('div', 'opening-line', '"' + intel.openingLine + '"');
                        openingSection.appendChild(openingTitle);
                        openingSection.appendChild(openingText);
                        intelligenceSection.appendChild(openingSection);
                    }

                    // Value props
                    if (intel.valueProps && intel.valueProps.length > 0) {
                        const valueSection = createSecureElement('div', 'intelligence-section');
                        const valueTitle = createSecureElement('div', 'intelligence-title', '🎯 KEY VALUE PROPS:');
                        valueSection.appendChild(valueTitle);

                        intel.valueProps.slice(0, 3).forEach(prop => {
                            const propDiv = createSecureElement('div', 'intelligence-item value-item', '• ' + prop);
                            valueSection.appendChild(propDiv);
                        });
                        intelligenceSection.appendChild(valueSection);
                    }
                }

                // Action buttons
                const actionsDiv = createSecureElement('div', 'contact-actions');
                const callBtn = createSecureElement('button', 'action-btn call-btn', '📞 Call Script');
                const emailBtn = createSecureElement('button', 'action-btn email-btn', '📧 Email Template');
                const caseStudyBtn = createSecureElement('button', 'action-btn casestudy-btn', '📊 Case Study');

                // Add click handlers
                callBtn.onclick = () => showCallScript(contact);
                emailBtn.onclick = () => showEmailTemplate(contact);
                caseStudyBtn.onclick = () => showCaseStudy(contact);

                actionsDiv.appendChild(callBtn);
                actionsDiv.appendChild(emailBtn);
                actionsDiv.appendChild(caseStudyBtn);

                // Assemble the card
                contactCard.appendChild(headerDiv);
                contactCard.appendChild(titleDiv);
                contactCard.appendChild(roleSpan);
                contactCard.appendChild(scoreSection);
                contactCard.appendChild(intelligenceSection);
                contactCard.appendChild(actionsDiv);

                container.appendChild(contactCard);
            });
        }

        function getPriorityClass(score) {
            if (score >= 90) return 'priority-1';
            if (score >= 75) return 'priority-2';
            return 'priority-3';
        }

        function getScoreStars(score) {
            const stars = Math.round((score || 0) / 20);
            return '⭐'.repeat(Math.max(1, Math.min(5, stars)));
        }

        function generateCallScript(contact) {
            // Use the auto-generated opening line if available
            if (contact.salesIntelligence && contact.salesIntelligence.openingLine) {
                return contact.salesIntelligence.openingLine;
            }

            // Fallback to basic template
            return 'Hi ' + (contact.name || 'there') + ', this is [Your Name] from Verdigris. I saw Genesis\\'s recent developments, and with your role in ' + (contact.title || 'operations').toLowerCase() + ', I imagine power monitoring and capacity planning are top priorities. We helped CloudFlare achieve 30% power efficiency gains - worth a 15-minute conversation about how they approached it?';
        }

        function generateEmailTemplate(contact) {
            let subject = 'Re: Genesis infrastructure expansion';
            let urgency = '';
            let painPoint = 'power monitoring and capacity planning';
            let valueProps = '30% power efficiency gains and eliminated capacity guesswork';

            // Use sales intelligence if available
            if (contact.salesIntelligence) {
                const intel = contact.salesIntelligence;

                if (intel.whyCallNow && intel.whyCallNow.length > 0) {
                    if (intel.whyCallNow[0].toLowerCase().includes('ai')) {
                        subject = 'Re: Genesis\\' $75M AI infrastructure investment';
                        urgency = 'With Genesis\\'s recent $75M AI infrastructure investment';
                    } else if (intel.whyCallNow[0].toLowerCase().includes('energy')) {
                        subject = 'Re: Energy cost optimization priorities';
                        urgency = 'Given the CEO\\'s focus on rising energy costs';
                    }
                }

                if (intel.painPoints && intel.painPoints.length > 0) {
                    painPoint = intel.painPoints[0].toLowerCase();
                }

                if (intel.valueProps && intel.valueProps.length > 0) {
                    valueProps = intel.valueProps.slice(0, 2).join(' and ').toLowerCase();
                }
            }

            return 'Subject: ' + subject + '\\n\\n' +
                   (contact.name || 'Hi') + ',\\n\\n' +
                   urgency + ', ' + painPoint + ' must be a pressing priority.\\n\\n' +
                   'We helped CloudFlare solve similar challenges during their infrastructure expansion - they achieved ' + valueProps + '.\\n\\n' +
                   'Worth a brief call to share what we learned? Happy to send over their case study first if that\\'s helpful.\\n\\n' +
                   'Best,\\n[Your name]';
        }

        function showCallScript(contact) {
            const script = generateCallScript(contact);
            alert('Call Script for ' + (contact.name || 'contact') + ':\\n\\n' + script);
        }

        function showEmailTemplate(contact) {
            const email = generateEmailTemplate(contact);
            alert('Email Template for ' + (contact.name || 'contact') + ':\\n\\n' + email);
        }

        function showCaseStudy(contact) {
            alert('Case Study for ' + (contact.name || 'contact') + ':\\n\\nSending GPU rack optimization case study showing 30% power efficiency gains and predictive capacity planning insights.');
        }

        function populatePartnerships(partnerships) {
            const container = document.getElementById('partnerships');
            const count = document.getElementById('partnerships-count');

            count.textContent = partnerships.length;
            clearContainer(container);

            partnerships.forEach(partnership => {
                const partnershipDiv = createSecureElement('div', 'item');

                const nameDiv = createSecureElement('div', 'name', partnership.name || 'Unknown Partner');
                const catSpan = createSecureElement('span', 'badge', partnership.category || 'Unknown');
                const oppDiv = createSecureElement('div', 'opportunity', partnership.opportunity || 'No opportunity description');
                const actionDiv = createSecureElement('div', 'action', 'Action: ' + (partnership.action || 'None'));

                partnershipDiv.appendChild(nameDiv);
                partnershipDiv.appendChild(catSpan);
                partnershipDiv.appendChild(oppDiv);
                partnershipDiv.appendChild(actionDiv);

                container.appendChild(partnershipDiv);
            });
        }

        async function loadData() {
            try {
                const response = await fetch('/api/abm-data');
                if (!response.ok) throw new Error('HTTP ' + response.status);

                const data = await response.json();

                if (data.account) populateAccount(data.account);
                if (data.events) populateEvents(data.events);
                if (data.contacts) populateContacts(data.contacts);
                if (data.partnerships) populatePartnerships(data.partnerships);

                setTimeout(() => {
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('content').style.display = 'block';
                }, 1500);

            } catch (error) {
                console.error('Error loading data:', error);
                const loadingDiv = document.getElementById('loading');
                clearContainer(loadingDiv);
                const errorDiv = createSecureElement('div', '', 'Error loading data: ' + error.message);
                errorDiv.style.color = 'var(--accent-red)';
                loadingDiv.appendChild(errorDiv);
            }
        }

        window.addEventListener('DOMContentLoaded', loadData);
    </script>
</body>
</html>'''

    def query_notion_database(self, database_id):
        """Query a Notion database"""
        if not self.api_key:
            raise Exception("NOTION_ABM_API_KEY not configured")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }

        response = requests.post(
            f"https://api.notion.com/v1/databases/{database_id}/query",
            headers=headers,
            json={}
        )

        if response.status_code != 200:
            raise Exception(f"Notion API error: {response.status_code} - {response.text}")

        return response.json()

    def fetch_abm_data(self):
        """Fetch all ABM data from Notion databases"""
        try:
            # Fetch all database data
            accounts_data = self.query_notion_database(self.database_ids['accounts'])
            events_data = self.query_notion_database(self.database_ids['trigger_events'])
            contacts_data = self.query_notion_database(self.database_ids['contacts'])
            partnerships_data = self.query_notion_database(self.database_ids['partnerships'])

            # Parse account data (take first account)
            account = None
            if accounts_data['results']:
                account_page = accounts_data['results'][0]
                props = account_page['properties']

                account = {
                    'name': self.extract_title(props.get('Account Name', {})),
                    'domain': self.extract_rich_text(props.get('Domain', {})),
                    'employees': props.get('Employee Count', {}).get('number', 0),
                    'model': self.extract_select(props.get('Business Model', {})),
                    'icpScore': props.get('ICP Fit Score', {}).get('number', 0),
                    'status': self.extract_select(props.get('Research Status', {}))
                }

            # Parse events
            events = []
            for event_page in events_data['results']:
                props = event_page['properties']
                events.append({
                    'description': self.extract_title(props.get('Event Description', {})),
                    'type': self.extract_select(props.get('Event Type', {})),
                    'confidence': self.extract_select(props.get('Confidence', {})),
                    'relevanceScore': props.get('Relevance Score', {}).get('number', 0)
                })

            # Parse contacts with scoring breakdown
            contacts = []
            for contact_page in contacts_data['results']:
                props = contact_page['properties']

                # Get individual scores
                icp_score = props.get('ICP Score', {}).get('number', 0)
                buying_power = props.get('Buying Power', {}).get('number', 0)
                engagement_score = props.get('Engagement Score', {}).get('number', 0)
                lead_score = props.get('Lead Score', {}).get('formula', {}).get('number', 0)

                # Calculate score breakdown reasons
                name = self.extract_title(props.get('Contact Name', {}))
                title = self.extract_rich_text(props.get('Title', {}))
                role = self.extract_select(props.get('Role', {}))

                # Generate scoring explanation
                scoring_breakdown = self.generate_scoring_explanation(title, role, icp_score, buying_power, engagement_score)

                # Generate automatic sales intelligence
                sales_intelligence = self.generate_sales_intelligence(name, title, role, events)

                contacts.append({
                    'name': name,
                    'title': title,
                    'role': role,
                    'leadScore': round(lead_score) if lead_score else 0,
                    'scoringBreakdown': {
                        'icpScore': round(icp_score) if icp_score else 0,
                        'buyingPower': round(buying_power) if buying_power else 0,
                        'engagementScore': round(engagement_score) if engagement_score else 0,
                        'explanation': scoring_breakdown
                    },
                    'salesIntelligence': sales_intelligence
                })

            # Parse partnerships
            partnerships = []
            for partnership_page in partnerships_data['results']:
                props = partnership_page['properties']
                partnerships.append({
                    'name': self.extract_title(props.get('Partner Name', {})),
                    'category': self.extract_select(props.get('Category', {})),
                    'opportunity': self.extract_rich_text(props.get('Verdigris Opportunity', {})),
                    'action': self.extract_select(props.get('Partnership Action', {}))
                })

            return {
                'account': account,
                'events': events,
                'contacts': contacts,
                'partnerships': partnerships
            }

        except Exception as e:
            print(f"Error fetching ABM data: {str(e)}")
            return {
                'account': {'name': 'Error loading account', 'domain': '', 'employees': 0, 'model': '', 'icpScore': 0, 'status': 'Error'},
                'events': [],
                'contacts': [],
                'partnerships': []
            }

    def extract_title(self, prop):
        """Extract text from title property"""
        if prop.get('title'):
            return ''.join([t['plain_text'] for t in prop['title']])
        return ''

    def extract_rich_text(self, prop):
        """Extract text from rich text property"""
        if prop.get('rich_text'):
            return ''.join([t['plain_text'] for t in prop['rich_text']])
        return ''

    def extract_select(self, prop):
        """Extract value from select property"""
        select_value = prop.get('select')
        return select_value['name'] if select_value else ''

    def generate_scoring_explanation(self, title, role, icp_score, buying_power, engagement_score):
        """Generate human-readable scoring explanation"""
        explanations = []

        # ICP Fit explanations
        if 'VP' in title or 'Vice President' in title:
            explanations.append("✓ VP-level title (high ICP fit)")
        elif 'Director' in title:
            explanations.append("✓ Director-level title (strong ICP fit)")
        elif 'Head' in title:
            explanations.append("✓ Head-level title (good ICP fit)")

        if 'Operations' in title or 'Infrastructure' in title:
            explanations.append("✓ Operations/Infrastructure role (target persona)")

        # Buying Power explanations
        if role == 'Economic Buyer':
            explanations.append("✓ Economic Buyer (budget authority)")
        elif role == 'Technical Evaluator':
            explanations.append("✓ Technical Evaluator (influences decisions)")
        elif role == 'Champion':
            explanations.append("✓ Champion (daily pain point owner)")

        # Engagement explanations
        if engagement_score >= 80:
            explanations.append("✓ High LinkedIn activity (posts regularly)")
        elif engagement_score >= 50:
            explanations.append("✓ Moderate LinkedIn activity (monthly posts)")
        else:
            explanations.append("• Limited LinkedIn activity detected")

        return explanations

    def generate_sales_intelligence(self, name, title, role, trigger_events):
        """Generate automatic sales intelligence based on contact data and trigger events"""
        intelligence = {
            'whyCallNow': [],
            'painPoints': [],
            'openingLine': '',
            'valueProps': []
        }

        # Generate "Why call now" based on trigger events
        for event in trigger_events:
            event_type = event.get('type', '').lower()

            if 'ai' in event_type:
                intelligence['whyCallNow'].append("Genesis invested $75M in AI infrastructure - power monitoring is critical for GPU deployments")
            elif 'energy' in event_type:
                intelligence['whyCallNow'].append("CEO mentioned rising energy costs as top priority - immediate ROI opportunity")
            elif 'expansion' in event_type:
                intelligence['whyCallNow'].append("Data center expansion creates new monitoring requirements")

        # Generate pain points based on title/role
        title_lower = title.lower() if title else ''

        if 'vp' in title_lower or 'vice president' in title_lower:
            intelligence['painPoints'].extend([
                "Budget pressure to reduce energy costs",
                "Board-level sustainability reporting requirements",
                "Strategic planning for AI workload capacity",
                "Risk management for critical infrastructure"
            ])
        elif 'director' in title_lower:
            intelligence['painPoints'].extend([
                "Technical integration with existing DCIM systems",
                "Capacity planning accuracy and forecasting",
                "Equipment performance optimization",
                "Team efficiency and automated monitoring"
            ])
        elif 'head' in title_lower or 'manager' in title_lower:
            intelligence['painPoints'].extend([
                "Daily operations visibility and alerts",
                "Preventive maintenance scheduling",
                "Power distribution troubleshooting",
                "Compliance reporting and documentation"
            ])

        if 'operations' in title_lower:
            intelligence['painPoints'].extend([
                "24/7 monitoring and alert fatigue",
                "Mean time to resolution (MTTR) pressure",
                "Predictive maintenance implementation"
            ])

        if 'infrastructure' in title_lower:
            intelligence['painPoints'].extend([
                "Infrastructure scaling decisions",
                "Technology stack integration",
                "Performance optimization initiatives"
            ])

        # Generate value propositions based on role
        if role == 'Economic Buyer':
            intelligence['valueProps'].extend([
                "30% reduction in energy costs through optimization",
                "ROI payback in 6-12 months",
                "Reduced insurance premiums via risk detection",
                "Sustainability reporting automation"
            ])
        elif role == 'Technical Evaluator':
            intelligence['valueProps'].extend([
                "RESTful API integration with existing DCIM",
                "Real-time granular power monitoring",
                "Machine learning anomaly detection",
                "Custom alerting and automation"
            ])
        elif role == 'Champion':
            intelligence['valueProps'].extend([
                "Simplified daily operations dashboard",
                "Automated reporting saves 10+ hours/week",
                "Predictive alerts prevent downtime",
                "Easy implementation with existing team"
            ])

        # Generate contextual opening line
        urgency_context = ""
        if intelligence['whyCallNow']:
            urgency_context = intelligence['whyCallNow'][0].split(' - ')[0]

        role_context = title.replace('Director of', '').replace('VP of', '').replace('Head of', '').strip() if title else 'operations'

        intelligence['openingLine'] = f"Hi {name}, I noticed Genesis's recent developments around {urgency_context.lower() if urgency_context else 'infrastructure expansion'}. Given your role in {role_context.lower()}, I imagine power monitoring and capacity planning are top priorities. We've helped similar companies like CloudFlare achieve 30% power efficiency gains - worth a brief conversation?"

        # Remove duplicates from pain points
        intelligence['painPoints'] = list(set(intelligence['painPoints']))

        return intelligence

    def log_message(self, format, *args):
        """Override to customize logging"""
        print(f"[{self.address_string()}] {format % args}")

def main():
    """Start the proxy server"""
    api_key = os.getenv('NOTION_ABM_API_KEY')
    if not api_key:
        print("❌ NOTION_ABM_API_KEY not found in environment variables")
        print("   Please check your .env file")
        return

    print("🚀 Starting Secure Notion ABM Proxy Server...")
    print("📊 Dashboard: http://localhost:8080")
    print("🔗 API endpoint: http://localhost:8080/api/abm-data")
    print("🔒 XSS-safe implementation with live Notion data")
    print("⚡ Press Ctrl+C to stop\n")

    server = HTTPServer(('localhost', 8080), NotionProxyHandler)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        server.server_close()

if __name__ == "__main__":
    main()