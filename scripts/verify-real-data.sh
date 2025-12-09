#!/bin/bash

# ABM Dashboard Real Data Verification Script
# Ensures the dashboard is using real Notion data, not mock/fallback data

set -e

echo "🔍 ABM Dashboard Real Data Verification"
echo "======================================"

PORT=8006
HEALTH_URL="http://localhost:$PORT/api/health"
DASHBOARD_URL="http://localhost:$PORT/api/dashboard/enhanced"

# Step 1: Check if dashboard is running
echo "📋 Step 1: Checking dashboard availability..."

if ! curl -s "$HEALTH_URL" > /dev/null 2>&1; then
    echo "  ❌ Dashboard not responding at $HEALTH_URL"
    echo "  💡 Run './scripts/dev-clean-start.sh' first to start the dashboard"
    exit 1
fi

echo "  ✅ Dashboard responding at port $PORT"

# Step 2: Test health endpoint for detailed status
echo "📋 Step 2: Checking health endpoint..."

HEALTH_RESPONSE=$(curl -s "$HEALTH_URL" 2>/dev/null || echo "")

if [ -z "$HEALTH_RESPONSE" ]; then
    echo "  ⚠️  Health endpoint returned empty response"
else
    echo "  ✅ Health endpoint response:"
    echo "     $HEALTH_RESPONSE"
fi

# Step 3: Test dashboard API endpoint
echo "📋 Step 3: Testing dashboard API endpoint..."

# Get dashboard data
DASHBOARD_RESPONSE=$(curl -s "$DASHBOARD_URL" 2>/dev/null || echo "")

if [ -z "$DASHBOARD_RESPONSE" ]; then
    echo "  ❌ Dashboard API returned empty response"
    echo "  💡 Check dashboard logs: tail -f dashboard.log"
    exit 1
fi

# Step 4: Analyze response for mock data indicators
echo "📋 Step 4: Analyzing response for mock data indicators..."

# Save response to temporary file for analysis
TEMP_RESPONSE="/tmp/dashboard_response.json"
echo "$DASHBOARD_RESPONSE" > "$TEMP_RESPONSE"

# Check for mock data indicators
python3 -c "
import json
import sys

try:
    with open('$TEMP_RESPONSE', 'r') as f:
        data = json.load(f)

    print('  🔍 Analyzing dashboard response...')

    mock_indicators = []
    real_indicators = []
    warnings = []

    # Check accounts data
    accounts = data.get('accounts', [])
    print(f'     Accounts found: {len(accounts)}')

    if len(accounts) == 0:
        mock_indicators.append('No accounts returned')
    elif len(accounts) == 3 and any('Mock' in str(account) for account in accounts):
        mock_indicators.append('Contains mock account data')
    else:
        real_indicators.append(f'{len(accounts)} real accounts found')

    # Check contacts data
    contacts = data.get('contacts', [])
    print(f'     Contacts found: {len(contacts)}')

    if len(contacts) == 0:
        warnings.append('No contacts returned')
    elif any('john.doe' in str(contact).lower() for contact in contacts):
        mock_indicators.append('Contains mock contact data (john.doe pattern)')
    else:
        real_indicators.append(f'{len(contacts)} real contacts found')

    # Check buying signals
    signals = data.get('buying_signals', [])
    print(f'     Buying signals found: {len(signals)}')

    if len(signals) == 0:
        warnings.append('No buying signals returned')
    elif any('mock' in str(signal).lower() for signal in signals):
        mock_indicators.append('Contains mock buying signal data')
    else:
        real_indicators.append(f'{len(signals)} real buying signals found')

    # Check partnerships
    partnerships = data.get('partnerships', [])
    print(f'     Partnerships found: {len(partnerships)}')

    if len(partnerships) == 0:
        warnings.append('No partnerships returned')
    else:
        real_indicators.append(f'{len(partnerships)} partnerships found')

    # Report results
    print('')
    print('  🎯 VERIFICATION RESULTS:')

    if mock_indicators:
        print('  ❌ MOCK DATA DETECTED:')
        for indicator in mock_indicators:
            print(f'     • {indicator}')
        print('')
        print('  💡 SOLUTION: Dashboard is running in fallback mode')
        print('     - Check Notion API key configuration')
        print('     - Verify import integrity with import tests')
        print('     - Check dashboard logs for error messages')
        sys.exit(1)

    elif real_indicators:
        print('  ✅ REAL DATA CONFIRMED:')
        for indicator in real_indicators:
            print(f'     • {indicator}')

        if warnings:
            print('')
            print('  ⚠️  WARNINGS:')
            for warning in warnings:
                print(f'     • {warning}')

        print('')
        print('  🎉 Dashboard is successfully using real Notion data!')
        sys.exit(0)

    else:
        print('  ❌ UNCLEAR DATA STATUS')
        print('     Unable to determine if data is real or mock')
        print('     Response may be malformed or empty')
        sys.exit(1)

except json.JSONDecodeError:
    print('  ❌ Invalid JSON response from dashboard')
    print('  💡 Dashboard may be returning HTML error page instead of JSON')
    print('     Check dashboard logs and ensure it started correctly')
    sys.exit(1)
except Exception as e:
    print(f'  ❌ Error analyzing response: {e}')
    sys.exit(1)
"

VERIFICATION_RESULT=$?

# Step 5: Additional environment checks if verification failed
if [ $VERIFICATION_RESULT -ne 0 ]; then
    echo ""
    echo "📋 Step 5: Additional diagnostics..."

    echo "  🔍 Environment variables:"
    if [ -n "$NOTION_API_KEY" ]; then
        echo "     NOTION_API_KEY: Set (length: ${#NOTION_API_KEY})"
    else
        echo "     NOTION_API_KEY: Not set ❌"
    fi

    if [ -n "$APOLLO_API_KEY" ]; then
        echo "     APOLLO_API_KEY: Set ✅"
    else
        echo "     APOLLO_API_KEY: Not set ⚠️"
    fi

    if [ -n "$OPENAI_API_KEY" ]; then
        echo "     OPENAI_API_KEY: Set ✅"
    else
        echo "     OPENAI_API_KEY: Not set ⚠️"
    fi

    echo ""
    echo "  📄 Recent dashboard logs:"
    if [ -f "dashboard.log" ]; then
        tail -n 10 dashboard.log | sed 's/^/     /'
    else
        echo "     No dashboard.log found"
    fi
fi

# Cleanup
rm -f "$TEMP_RESPONSE"

exit $VERIFICATION_RESULT
