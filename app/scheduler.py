import schedule
import time
import os
from datetime import datetime
import pytz
from app.idea_discovery_agent import IdeaDiscoveryAgent
from app.models import create_tables

class IdeaOasisScheduler:
    def __init__(self):
        self.agent = IdeaDiscoveryAgent()
        self.korea_tz = pytz.timezone('Asia/Seoul')
        
    def run_daily_discovery(self):
        """Run the daily idea discovery process"""
        print(f"🌅 Starting daily idea discovery at {datetime.now(self.korea_tz).strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Discover and process a new idea
            processed_idea = self.agent.discover_daily_idea()
            
            if processed_idea:
                # Save to database
                success = self.agent.save_idea_to_database(processed_idea)
                if success:
                    print("✅ Daily idea discovery completed successfully!")
                else:
                    print("❌ Failed to save idea to database")
            else:
                print("❌ No idea was discovered today")
                
        except Exception as e:
            print(f"❌ Error in daily discovery: {e}")
        
        # Archive old ideas
        try:
            self.agent.archive_old_ideas()
        except Exception as e:
            print(f"❌ Error archiving old ideas: {e}")
    
    def run_manual_discovery(self):
        """Run discovery manually (for testing)"""
        print("🔧 Running manual idea discovery...")
        self.run_daily_discovery()
    
    def start_scheduler(self):
        """Start the scheduler"""
        print("⏰ Starting IdeaOasis scheduler...")
        
        # Schedule daily discovery at 6 AM Korea time
        schedule.every().day.at("06:00").timezone("Asia/Seoul").do(self.run_daily_discovery)
        
        # Also run immediately if no ideas exist for today
        self._check_and_run_if_needed()
        
        print("✅ Scheduler started. Daily discovery scheduled for 6:00 AM Korea time.")
        print("Press Ctrl+C to stop the scheduler.")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\n🛑 Scheduler stopped.")
    
    def _check_and_run_if_needed(self):
        """Check if we need to run discovery immediately"""
        try:
            from app.models import get_db, Idea
            from datetime import datetime, timedelta
            
            db = next(get_db())
            
            # Check if there's an active idea for today
            today_start = datetime.now(self.korea_tz).replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            
            active_idea = db.query(Idea).filter(
                Idea.archived == False,
                Idea.created_at >= today_start,
                Idea.created_at < today_end
            ).first()
            
            if not active_idea:
                print("📝 No active idea found for today. Running discovery now...")
                self.run_daily_discovery()
            else:
                print(f"✅ Active idea found: {active_idea.idea_title}")
                
        except Exception as e:
            print(f"❌ Error checking for active ideas: {e}")
        finally:
            db.close()

def main():
    """Main function to start the scheduler"""
    # Create database tables
    create_tables()
    
    # Initialize and start scheduler
    scheduler = IdeaOasisScheduler()
    scheduler.start_scheduler()

if __name__ == "__main__":
    main() 