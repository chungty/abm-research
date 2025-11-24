#!/usr/bin/env python3
"""
Hybrid Data Manager - Notion + Database Architecture
Combines Notion API (user-facing CRM) with local database (fast queries/analytics)
"""

import os
import sqlite3
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from contextlib import contextmanager

# Import existing Notion service
from ..dashboard.dashboard_data_service import NotionDataService


@dataclass
class SyncStatus:
    """Track synchronization status between Notion and local database"""
    table_name: str
    last_notion_sync: datetime
    last_db_update: datetime
    record_count_notion: int
    record_count_db: int
    sync_conflicts: int
    sync_status: str  # 'synced', 'drift', 'error'


class HybridDataManager:
    """
    Hybrid Data Manager for ABM Research Platform

    Architecture:
    - Notion API: Source of truth for user-editable data, searchability, CRM integration
    - SQLite Database: Fast queries, analytics, caching, offline access
    - Bi-directional Sync: Keep both systems consistent with conflict resolution
    """

    def __init__(self, db_path: str = "abm_research.db", sync_interval: int = 300):
        self.db_path = db_path
        self.sync_interval = sync_interval  # 5 minutes default
        self.notion_service = NotionDataService()

        # Initialize database
        self._init_database()

        # Sync status tracking
        self.sync_status: Dict[str, SyncStatus] = {}

        # Start background sync thread
        self.sync_thread = threading.Thread(target=self._background_sync_loop, daemon=True)
        self.sync_thread.start()

        print("🔄 Hybrid Data Manager initialized")
        print(f"📊 Database: {db_path}")
        print(f"⏱️  Sync interval: {sync_interval}s")

    def _init_database(self):
        """Initialize SQLite database with optimized schema"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()

            # Accounts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    id TEXT PRIMARY KEY,
                    notion_id TEXT UNIQUE,
                    name TEXT NOT NULL,
                    domain TEXT,
                    industry TEXT,
                    company_size TEXT,
                    icp_fit_score INTEGER,
                    research_status TEXT,
                    created_date TEXT,
                    last_updated TEXT,
                    notion_last_modified TEXT
                )
            """)

            # Contacts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    id TEXT PRIMARY KEY,
                    notion_id TEXT UNIQUE,
                    full_name TEXT NOT NULL,
                    email TEXT,
                    phone TEXT,
                    title TEXT,
                    company_name TEXT,
                    department TEXT,
                    seniority_level TEXT,
                    linkedin_url TEXT,
                    linkedin_activity_score INTEGER,
                    buying_power_score INTEGER,
                    final_lead_score INTEGER,
                    meddic_classification TEXT,
                    created_date TEXT,
                    last_updated TEXT,
                    notion_last_modified TEXT,
                    FOREIGN KEY(company_name) REFERENCES accounts(name)
                )
            """)

            # Trigger Events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trigger_events (
                    id TEXT PRIMARY KEY,
                    notion_id TEXT UNIQUE,
                    company_name TEXT,
                    event_description TEXT,
                    event_type TEXT,
                    source_url TEXT,
                    urgency_level TEXT,
                    confidence_score INTEGER,
                    verdigris_relevance TEXT,
                    timestamp TEXT,
                    created_date TEXT,
                    last_updated TEXT,
                    notion_last_modified TEXT,
                    FOREIGN KEY(company_name) REFERENCES accounts(name)
                )
            """)

            # Strategic Partnerships table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS partnerships (
                    id TEXT PRIMARY KEY,
                    notion_id TEXT UNIQUE,
                    target_company TEXT,
                    partnership_type TEXT,
                    partner_company TEXT,
                    verdigris_relevance TEXT,
                    confidence_score INTEGER,
                    created_date TEXT,
                    last_updated TEXT,
                    notion_last_modified TEXT,
                    FOREIGN KEY(target_company) REFERENCES accounts(name)
                )
            """)

            # Research Queue table (local-only for workflow management)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS research_queue (
                    id TEXT PRIMARY KEY,
                    account_id TEXT,
                    account_name TEXT,
                    research_phases TEXT,  -- JSON array
                    status TEXT,
                    priority INTEGER,
                    created_at TEXT,
                    started_at TEXT,
                    completed_at TEXT,
                    progress_percentage INTEGER,
                    error_message TEXT,
                    estimated_duration INTEGER,
                    actual_duration INTEGER
                )
            """)

            # Sync Metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sync_metadata (
                    table_name TEXT PRIMARY KEY,
                    last_notion_sync TEXT,
                    last_db_update TEXT,
                    record_count_notion INTEGER,
                    record_count_db INTEGER,
                    sync_conflicts INTEGER,
                    sync_status TEXT,
                    error_log TEXT
                )
            """)

            conn.commit()
            print("✅ Database schema initialized")

    @contextmanager
    def get_db_connection(self):
        """Get database connection with proper error handling"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        try:
            yield conn
        finally:
            conn.close()

    # ═══════════════════════════════════════════════════════════════════════════════════
    # FAST LOCAL QUERIES (PRIMARY INTERFACE)
    # ═══════════════════════════════════════════════════════════════════════════════════

    def get_accounts_fast(self,
                         limit: int = None,
                         search: str = None,
                         min_icp_score: int = None,
                         research_status: str = None) -> List[Dict]:
        """Fast account query from local database"""
        with self.get_db_connection() as conn:
            query = "SELECT * FROM accounts WHERE 1=1"
            params = []

            if search:
                query += " AND (name LIKE ? OR domain LIKE ? OR industry LIKE ?)"
                search_term = f"%{search}%"
                params.extend([search_term, search_term, search_term])

            if min_icp_score is not None:
                query += " AND icp_fit_score >= ?"
                params.append(min_icp_score)

            if research_status:
                query += " AND research_status = ?"
                params.append(research_status)

            query += " ORDER BY icp_fit_score DESC"

            if limit:
                query += " LIMIT ?"
                params.append(limit)

            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_contacts_fast(self,
                         company_name: str = None,
                         min_lead_score: int = None,
                         limit: int = None) -> List[Dict]:
        """Fast contact query from local database"""
        with self.get_db_connection() as conn:
            query = "SELECT * FROM contacts WHERE 1=1"
            params = []

            if company_name:
                query += " AND company_name = ?"
                params.append(company_name)

            if min_lead_score is not None:
                query += " AND final_lead_score >= ?"
                params.append(min_lead_score)

            query += " ORDER BY final_lead_score DESC"

            if limit:
                query += " LIMIT ?"
                params.append(limit)

            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_trigger_events_fast(self,
                               company_name: str = None,
                               urgency_level: str = None,
                               days_back: int = 30) -> List[Dict]:
        """Fast trigger events query from local database"""
        with self.get_db_connection() as conn:
            query = "SELECT * FROM trigger_events WHERE 1=1"
            params = []

            if company_name:
                query += " AND company_name = ?"
                params.append(company_name)

            if urgency_level:
                query += " AND urgency_level = ?"
                params.append(urgency_level)

            # Filter by date
            cutoff_date = (datetime.now() - timedelta(days=days_back)).isoformat()
            query += " AND timestamp >= ?"
            params.append(cutoff_date)

            query += " ORDER BY timestamp DESC"

            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_dashboard_analytics_fast(self) -> Dict[str, Any]:
        """Fast analytics query from local database"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()

            # Account metrics
            cursor.execute("SELECT COUNT(*) as total_accounts FROM accounts")
            total_accounts = cursor.fetchone()['total_accounts']

            cursor.execute("SELECT COUNT(*) as high_icp_accounts FROM accounts WHERE icp_fit_score >= 70")
            high_icp_accounts = cursor.fetchone()['high_icp_accounts']

            # Contact metrics
            cursor.execute("SELECT COUNT(*) as total_contacts FROM contacts")
            total_contacts = cursor.fetchone()['total_contacts']

            cursor.execute("SELECT COUNT(*) as priority_contacts FROM contacts WHERE final_lead_score >= 70")
            priority_contacts = cursor.fetchone()['priority_contacts']

            # Signal metrics
            cursor.execute("""
                SELECT COUNT(*) as active_signals
                FROM trigger_events
                WHERE urgency_level IN ('High', 'Medium')
                AND timestamp >= ?
            """, [(datetime.now() - timedelta(days=7)).isoformat()])
            active_signals = cursor.fetchone()['active_signals']

            # Research queue metrics
            cursor.execute("SELECT COUNT(*) as queued_research FROM research_queue WHERE status = 'queued'")
            queued_research = cursor.fetchone()['queued_research']

            cursor.execute("SELECT COUNT(*) as active_research FROM research_queue WHERE status = 'active'")
            active_research = cursor.fetchone()['active_research']

            return {
                'total_accounts': total_accounts,
                'high_icp_accounts': high_icp_accounts,
                'total_contacts': total_contacts,
                'priority_contacts': priority_contacts,
                'active_signals': active_signals,
                'queued_research': queued_research,
                'active_research': active_research,
                'timestamp': datetime.now().isoformat()
            }

    # ═══════════════════════════════════════════════════════════════════════════════════
    # RESEARCH QUEUE MANAGEMENT (LOCAL-ONLY)
    # ═══════════════════════════════════════════════════════════════════════════════════

    def add_to_research_queue(self,
                             account_id: str,
                             account_name: str,
                             research_phases: List[str],
                             priority: int = 5) -> str:
        """Add account to research queue"""
        queue_id = f"research_{account_id}_{int(time.time())}"

        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO research_queue
                (id, account_id, account_name, research_phases, status, priority, created_at, progress_percentage)
                VALUES (?, ?, ?, ?, 'queued', ?, ?, 0)
            """, (
                queue_id,
                account_id,
                account_name,
                json.dumps(research_phases),
                priority,
                datetime.now().isoformat()
            ))
            conn.commit()

        return queue_id

    def get_research_queue_status(self) -> Dict[str, Any]:
        """Get comprehensive research queue status"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()

            # Get all queue items
            cursor.execute("SELECT * FROM research_queue ORDER BY priority DESC, created_at ASC")
            all_items = [dict(row) for row in cursor.fetchall()]

            # Parse JSON phases
            for item in all_items:
                if item['research_phases']:
                    item['research_phases'] = json.loads(item['research_phases'])

            # Group by status
            queue_by_status = {
                'queued': [item for item in all_items if item['status'] == 'queued'],
                'active': [item for item in all_items if item['status'] == 'active'],
                'completed': [item for item in all_items if item['status'] == 'completed'],
                'failed': [item for item in all_items if item['status'] == 'failed']
            }

            # Calculate stats
            stats = {
                'total_items': len(all_items),
                'queued': len(queue_by_status['queued']),
                'active': len(queue_by_status['active']),
                'completed_today': len([
                    item for item in queue_by_status['completed']
                    if item['completed_at'] and
                    datetime.fromisoformat(item['completed_at']).date() == datetime.now().date()
                ]),
                'avg_completion_time': self._calculate_avg_completion_time(queue_by_status['completed'])
            }

            return {
                'queue': queue_by_status,
                'stats': stats,
                'timestamp': datetime.now().isoformat()
            }

    def _calculate_avg_completion_time(self, completed_items: List[Dict]) -> int:
        """Calculate average completion time in seconds"""
        if not completed_items:
            return 0

        total_duration = 0
        valid_items = 0

        for item in completed_items:
            if item['actual_duration']:
                total_duration += item['actual_duration']
                valid_items += 1

        return total_duration // valid_items if valid_items > 0 else 0

    # ═══════════════════════════════════════════════════════════════════════════════════
    # NOTION SYNC OPERATIONS
    # ═══════════════════════════════════════════════════════════════════════════════════

    def sync_from_notion(self, force: bool = False) -> Dict[str, SyncStatus]:
        """Sync data from Notion to local database"""
        print("🔄 Starting Notion → Database sync...")

        tables = ['accounts', 'contacts', 'trigger_events', 'partnerships']
        sync_results = {}

        for table_name in tables:
            try:
                print(f"📥 Syncing {table_name}...")

                # Get data from Notion
                if table_name == 'accounts':
                    notion_data = self.notion_service.fetch_accounts()
                elif table_name == 'contacts':
                    notion_data = self.notion_service.fetch_contacts()
                elif table_name == 'trigger_events':
                    notion_data = self.notion_service.fetch_trigger_events()
                elif table_name == 'partnerships':
                    notion_data = self.notion_service.fetch_partnerships()

                # Update local database
                conflicts = self._update_local_table(table_name, notion_data)

                # Update sync status
                sync_status = SyncStatus(
                    table_name=table_name,
                    last_notion_sync=datetime.now(),
                    last_db_update=datetime.now(),
                    record_count_notion=len(notion_data),
                    record_count_db=self._get_local_record_count(table_name),
                    sync_conflicts=conflicts,
                    sync_status='synced' if conflicts == 0 else 'drift'
                )

                self._save_sync_status(sync_status)
                sync_results[table_name] = sync_status

                print(f"✅ {table_name}: {len(notion_data)} records, {conflicts} conflicts")

            except Exception as e:
                print(f"❌ Error syncing {table_name}: {e}")
                sync_status = SyncStatus(
                    table_name=table_name,
                    last_notion_sync=datetime.now(),
                    last_db_update=datetime.now(),
                    record_count_notion=0,
                    record_count_db=self._get_local_record_count(table_name),
                    sync_conflicts=0,
                    sync_status='error'
                )
                sync_results[table_name] = sync_status

        self.sync_status = sync_results
        return sync_results

    def _update_local_table(self, table_name: str, notion_data: List[Dict]) -> int:
        """Update local table with Notion data, return number of conflicts"""
        conflicts = 0

        # Column mapping between Notion field names and local DB columns
        column_mappings = {
            'accounts': {
                'Company Name': 'name',
                'Domain': 'domain',
                'Industry': 'industry',
                'Company Size': 'company_size',
                'ICP Fit Score': 'icp_fit_score',
                'Research Status': 'research_status'
            },
            'contacts': {
                'Full Name': 'full_name',
                'Name': 'full_name',  # Fallback
                'Email': 'email',
                'Phone': 'phone',
                'Title': 'title',
                'Company Name': 'company_name',
                'Department': 'department',
                'Seniority Level': 'seniority_level',
                'LinkedIn URL': 'linkedin_url',
                'LinkedIn Activity Score': 'linkedin_activity_score',
                'Buying Power Score': 'buying_power_score',
                'Final Lead Score': 'final_lead_score',
                'MEDDIC Classification': 'meddic_classification'
            },
            'trigger_events': {
                'Company Name': 'company_name',
                'Event Description': 'event_description',
                'Description': 'event_description',  # Fallback
                'Event Type': 'event_type',
                'Source URL': 'source_url',
                'Urgency Level': 'urgency_level',
                'Confidence Score': 'confidence_score',
                'Verdigris Relevance': 'verdigris_relevance',
                'Timestamp': 'timestamp'
            },
            'partnerships': {
                'Target Company': 'target_company',
                'Name': 'target_company',  # Fallback
                'Partnership Type': 'partnership_type',
                'Partner Company': 'partner_company',
                'Verdigris Relevance': 'verdigris_relevance',
                'Confidence Score': 'confidence_score'
            }
        }

        mapping = column_mappings.get(table_name, {})

        with self.get_db_connection() as conn:
            cursor = conn.cursor()

            for item in notion_data:
                try:
                    # Transform Notion field names to local column names
                    mapped_item = {}

                    # Generate local ID
                    local_id = f"{table_name}_{int(time.time())}_{hash(str(item))}"
                    mapped_item['id'] = local_id
                    mapped_item['notion_id'] = item.get('id', local_id)

                    # Map fields
                    for notion_field, value in item.items():
                        if notion_field in mapping:
                            local_field = mapping[notion_field]
                            mapped_item[local_field] = value
                        elif notion_field not in ['id']:  # Keep non-mapped fields except id
                            # Use field name as-is for unmapped fields
                            clean_field = notion_field.lower().replace(' ', '_').replace('-', '_')
                            mapped_item[clean_field] = value

                    # Add timestamps
                    current_time = datetime.now().isoformat()
                    mapped_item['created_date'] = current_time
                    mapped_item['last_updated'] = current_time
                    mapped_item['notion_last_modified'] = current_time

                    # Check for existing record by notion_id
                    notion_id = mapped_item['notion_id']
                    cursor.execute(f"SELECT * FROM {table_name} WHERE notion_id = ?", (notion_id,))
                    existing = cursor.fetchone()

                    if existing:
                        # Update existing record
                        update_fields = []
                        update_values = []

                        for key, value in mapped_item.items():
                            if key not in ['id', 'created_date']:  # Don't update id or created_date
                                update_fields.append(f"{key} = ?")
                                update_values.append(value)

                        if update_fields:
                            update_values.append(existing['id'])
                            cursor.execute(f"""
                                UPDATE {table_name}
                                SET {', '.join(update_fields)}
                                WHERE id = ?
                            """, update_values)
                    else:
                        # Insert new record - only insert fields that exist in the table
                        cursor.execute(f"PRAGMA table_info({table_name})")
                        table_columns = [row[1] for row in cursor.fetchall()]

                        insert_item = {k: v for k, v in mapped_item.items() if k in table_columns}

                        if insert_item:  # Only insert if we have valid columns
                            columns = list(insert_item.keys())
                            placeholders = ','.join(['?' for _ in columns])
                            values = list(insert_item.values())

                            cursor.execute(f"""
                                INSERT OR IGNORE INTO {table_name} ({','.join(columns)})
                                VALUES ({placeholders})
                            """, values)

                except Exception as e:
                    print(f"Error processing item for {table_name}: {e}")
                    conflicts += 1
                    continue

            conn.commit()

        return conflicts

    def _get_local_record_count(self, table_name: str) -> int:
        """Get record count from local table"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            return cursor.fetchone()['count']

    def _save_sync_status(self, sync_status: SyncStatus):
        """Save sync status to database"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO sync_metadata
                (table_name, last_notion_sync, last_db_update, record_count_notion,
                 record_count_db, sync_conflicts, sync_status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                sync_status.table_name,
                sync_status.last_notion_sync.isoformat(),
                sync_status.last_db_update.isoformat(),
                sync_status.record_count_notion,
                sync_status.record_count_db,
                sync_status.sync_conflicts,
                sync_status.sync_status
            ))
            conn.commit()

    def _background_sync_loop(self):
        """Background thread for periodic Notion sync"""
        while True:
            try:
                time.sleep(self.sync_interval)
                self.sync_from_notion()
                print(f"🔄 Background sync completed at {datetime.now()}")
            except Exception as e:
                print(f"❌ Background sync error: {e}")
                time.sleep(60)  # Wait 1 minute before retrying

    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status for all tables"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sync_metadata")
            sync_data = [dict(row) for row in cursor.fetchall()]

            return {
                'sync_status': sync_data,
                'last_update': datetime.now().isoformat(),
                'sync_interval': self.sync_interval,
                'database_size': os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
            }


# ═══════════════════════════════════════════════════════════════════════════════════
# SINGLETON INSTANCE
# ═══════════════════════════════════════════════════════════════════════════════════

# Global instance for easy import
hybrid_data_manager = HybridDataManager()

if __name__ == '__main__':
    print("🚀 Hybrid Data Manager - Standalone Test")

    # Test sync
    sync_results = hybrid_data_manager.sync_from_notion()
    print(f"✅ Sync completed: {len(sync_results)} tables")

    # Test analytics
    analytics = hybrid_data_manager.get_dashboard_analytics_fast()
    print(f"📊 Analytics: {analytics}")

    # Test research queue
    queue_status = hybrid_data_manager.get_research_queue_status()
    print(f"📋 Research queue: {queue_status['stats']}")