"""
Scheduler for Automated Lead Generation Tasks
Runs daily outreach and maintenance tasks.

Usage:
  python scheduler.py              # Run scheduler in foreground
  python scheduler.py --run-now    # Run outreach immediately and exit
"""

import schedule
import time
import sys
from datetime import datetime
import json

from agent import LeadGenerationAgent
from resend_integration import ResendClient


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
    return count


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

    # Send email summary if enabled
    config = load_config()
    if config.get('notifications', {}).get('daily_summary', False):
        send_daily_email_summary(agent, summary)


def send_daily_email_summary(agent, summary):
    """Send daily pipeline summary via email."""
    config = load_config()
    notification_email = config.get('notifications', {}).get('email_alerts', '')

    if not notification_email or not config.get('resend_enabled', False):
        return

    resend = ResendClient(
        api_key=config.get('resend_api_key'),
        from_email=config.get('resend_from_email'),
        from_name=config.get('resend_from_name')
    )

    # Build email body
    subject = f"📊 Daily Lead Report - {datetime.now().strftime('%Y-%m-%d')}"

    # Count engaged leads
    engaged_count = summary['by_status'].get('engaged', 0)
    contacted_count = summary['by_status'].get('contacted', 0)
    new_count = summary['by_status'].get('new', 0)

    hot_leads_text = ""
    if summary['high_priority']:
        hot_leads_text = "\n🔥 HOT LEADS (Score 70+):\n"
        for lead in summary['high_priority'][:5]:
            hot_leads_text += f"  • {lead['name']} @ {lead['company']} (Score: {lead['score']})\n"

    body = f"""Daily Lead Generation Report

📈 PIPELINE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Leads: {summary['total_leads']}

By Status:
  • New: {new_count}
  • Contacted: {contacted_count}
  • Engaged: {engaged_count}

By Service:
  • LinkedIn Presence: {summary['by_service'].get('linkedin_presence', 0)}
  • Market Validation: {summary['by_service'].get('customer_voice_research', 0)}
{hot_leads_text}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

View full pipeline in Attio:
https://app.attio.com/rocksalt-consulting-ltd

--
Lead Generation Agent
Rocksalt Consulting
"""

    result = resend.send_email(
        to=notification_email,
        subject=subject,
        text_body=body
    )

    if result.success:
        print(f"[SCHEDULER] Daily summary email sent to {notification_email}")
    else:
        print(f"[SCHEDULER] Failed to send summary: {result.error}")


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
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--run-now":
            print("\n=== Running Outreach Now ===")
            count = run_daily_outreach()
            generate_daily_report()
            print(f"\nCompleted! {count} outreach actions executed.")
            return
        elif sys.argv[1] == "--report":
            generate_daily_report()
            return
        elif sys.argv[1] == "--help":
            print(__doc__)
            print("\nOptions:")
            print("  --run-now    Run outreach immediately and exit")
            print("  --report     Generate report only")
            print("  --help       Show this help message")
            print("\nNo arguments: Start scheduler daemon")
            return

    setup_schedule()

    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    main()
