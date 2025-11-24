#!/usr/bin/env python3
"""
ABM Data Quality Scheduler
Runs automated quality checks and cleanup routines
"""

import schedule
import time
import threading
from datetime import datetime
from automated_data_quality_system import ABMDataQualitySystem
from aggressive_notion_cleanup import AggressiveNotionCleanup

class QualityScheduler:
    """Scheduler for automated data quality checks"""

    def __init__(self):
        self.quality_system = ABMDataQualitySystem()
        self.aggressive_cleanup = AggressiveNotionCleanup()
        self.running = False

    def run_daily_quality_check(self):
        """Daily quality check routine"""
        print(f"\n🕰️ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - RUNNING DAILY QUALITY CHECK")
        print("=" * 70)

        try:
            # Rebuild cache
            self.quality_system.build_deduplication_cache()

            # Run quality checks
            results = self.quality_system.run_quality_checks()

            print(f"✅ Daily quality check complete - Score: {results['quality_score']:.1f}/100")

        except Exception as e:
            print(f"❌ Daily quality check failed: {e}")

    def run_cache_rebuild(self):
        """Cache rebuild routine"""
        print(f"\n🔄 {datetime.now().strftime('%H:%M:%S')} - REBUILDING DEDUPLICATION CACHE")

        try:
            self.quality_system.build_deduplication_cache()
            print("✅ Cache rebuilt successfully")
        except Exception as e:
            print(f"❌ Cache rebuild failed: {e}")

    def run_weekly_deep_clean(self):
        """Weekly deep cleaning routine with aggressive cleanup"""
        print(f"\n🧹 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - RUNNING WEEKLY DEEP CLEAN")
        print("=" * 70)

        try:
            # Run standard deep clean first
            self.quality_system.run_deep_clean()

            # Run aggressive cleanup to actually delete duplicates
            print("🔥 Running aggressive cleanup (deletes duplicates from Notion)...")
            self.aggressive_cleanup.run_aggressive_cleanup()

            print("✅ Weekly deep clean with aggressive cleanup complete")
        except Exception as e:
            print(f"❌ Weekly deep clean failed: {e}")

    def run_manual_aggressive_cleanup(self):
        """Manual aggressive cleanup for immediate execution"""
        print(f"\n🔥 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - MANUAL AGGRESSIVE CLEANUP")
        print("=" * 70)

        try:
            self.aggressive_cleanup.run_aggressive_cleanup()
            print("✅ Manual aggressive cleanup complete")
        except Exception as e:
            print(f"❌ Manual aggressive cleanup failed: {e}")

    def start_scheduler(self):
        """Start the automated scheduler"""
        print("⏰ STARTING ABM DATA QUALITY SCHEDULER")
        print("=" * 50)

        # Schedule jobs
        schedule.every().day.at("06:00").do(self.run_daily_quality_check)
        schedule.every(4).hours.do(self.run_cache_rebuild)
        schedule.every().sunday.at("02:00").do(self.run_weekly_deep_clean)

        # Schedule immediate cache build
        schedule.every().minute.do(self.run_cache_rebuild).tag('initial')

        print("✅ Scheduled daily quality checks at 06:00")
        print("✅ Scheduled cache rebuild every 4 hours")
        print("✅ Scheduled weekly deep clean on Sunday at 02:00")
        print("🔄 Building initial cache...")

        self.running = True

        # Run scheduler loop
        while self.running:
            try:
                schedule.run_pending()

                # Remove initial setup job after first run
                if schedule.get_jobs('initial'):
                    schedule.clear('initial')
                    print("✅ Initial cache built")

                time.sleep(60)  # Check every minute

            except KeyboardInterrupt:
                print("\n🛑 Scheduler stopped by user")
                self.running = False
                break
            except Exception as e:
                print(f"❌ Scheduler error: {e}")
                time.sleep(60)

    def stop_scheduler(self):
        """Stop the scheduler"""
        self.running = False

def run_manual_quality_check():
    """Run a manual quality check for testing"""
    print("🔧 MANUAL ABM DATA QUALITY CHECK")
    print("=" * 45)

    quality_system = ABMDataQualitySystem()

    # Build cache
    quality_system.build_deduplication_cache()

    # Run quality checks
    results = quality_system.run_quality_checks()

    print(f"\n📊 MANUAL CHECK COMPLETE")
    print(f"✅ Quality Score: {results['quality_score']:.1f}/100")
    print(f"🔧 Issues Fixed: {results['issues_fixed']}")

    return results

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "manual":
            # Run manual quality check
            run_manual_quality_check()
        elif sys.argv[1] == "cleanup":
            # Run aggressive cleanup
            scheduler = QualityScheduler()
            scheduler.run_manual_aggressive_cleanup()
        else:
            print("Usage: python quality_scheduler.py [manual|cleanup]")
            print("  manual: Run quality check without cleanup")
            print("  cleanup: Run aggressive cleanup (deletes duplicates)")
            print("  (no args): Start automated scheduler")
    else:
        # Start scheduler
        scheduler = QualityScheduler()
        try:
            scheduler.start_scheduler()
        except KeyboardInterrupt:
            print("\n👋 Scheduler stopped")