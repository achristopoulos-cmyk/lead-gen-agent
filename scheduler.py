"""
Scheduler for Automated Lead Generation Tasks
Runs daily outreach and maintenance tasks.
"""

import schedule
import time
from datetime import datetime
import json

from agent import LeadGenerationAgent


def load_config():
    try:
        with open("config.json", "r") as f:
            return json.load(f)
    except:
        return {}


def run_daily_outreach():
    """Execute daily outreach sequence."""
    print(f"\n[SCHEDULER] {datetime.now().strftime('%Y-%m-%d %H:%M')} - Running daily outreach")
    agent = LeadGenerationAgent()
    count = agent.run_daily_outreach()
    print(f"[SCHEDULER] Completed {count} outreach actions")


def generate_daily_report():
    """Generate and print daily pipeline report."""
    print(f"\n[SCHEDULER] {datetime.now().strftime('%Y-%m-%d %H:%M')} - Daily Report")
    print("=" * 50)

    agent = LeadGenerationAgent()
    summary = agent.get_pipeline_summary()

    print(f"\nTotal Leads: {summary['total_leads']}")

    print("\nBy Status:")
    for status, count in summary['by_status'].items():
        print(f"  {status}: {count}")

    print("\nBy Service:")
    for service, count in summary['by_service'].items():
        print(f"  {service}: {count}")

    print("\nHot Leads (Score 70+):")
    for lead in summary['high_priority'][:5]:
        print(f"  - {lead['name']} ({lead['company']}) - Score: {lead['score']}")

    print("=" * 50)


def cleanup_stale_leads():
    """Mark leads as lost if no engagement after 30 days."""
    print(f"\n[SCHEDULER] Running stale lead cleanup")
    agent = LeadGenerationAgent()

    from datetime import datetime, timedelta
    cutoff = (datetime.now() - timedelta(days=30)).isoformat()
    stale_count = 0

    for lead_id, lead_data in agent.leads.items():
        if lead_data.get('status') in ['contacted', 'new']:
            last_contact = lead_data.get('last_contacted')
            if last_contact and last_contact < cutoff:
                agent.leads[lead_id]['status'] = 'lost'
                agent.leads[lead_id]['notes'].append({
                    "timestamp": datetime.now().isoformat(),
                    "action": "auto_marked_lost",
                    "reason": "No engagement after 30 days"
                })
                stale_count += 1

    if stale_count > 0:
        agent._save_leads()
        print(f"[SCHEDULER] Marked {stale_count} leads as lost (no engagement)")


def setup_schedule():
    """Configure the schedule for automated tasks."""
    config = load_config()
    outreach_settings = config.get("outreach_settings", {})
    send_times = outreach_settings.get("send_times", {})

    start_hour = send_times.get("start_hour", 9)

    # Run outreach at the start of business hours
    schedule.every().day.at(f"{start_hour:02d}:00").do(run_daily_outreach)

    # Generate report at end of day
    schedule.every().day.at("17:00").do(generate_daily_report)

    # Cleanup stale leads weekly
    schedule.every().sunday.at("08:00").do(cleanup_stale_leads)

    print("\n=== Lead Generation Scheduler ===")
    print(f"Outreach scheduled for: {start_hour:02d}:00 daily")
    print("Report scheduled for: 17:00 daily")
    print("Stale cleanup scheduled for: Sunday 08:00")
    print("\nScheduler running... Press Ctrl+C to stop\n")


def main():
    setup_schedule()

    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    main()
