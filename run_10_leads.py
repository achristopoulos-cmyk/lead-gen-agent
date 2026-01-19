"""
Run the lead generation agent with 10 sample leads.
Processes leads through scoring, CRM sync, and outreach queuing.
"""

import json
from agent import LeadGenerationAgent

# 10 sample leads with diverse profiles
sample_leads = [
    {
        "email": "sarah.chen@techstartup.io",
        "first_name": "Sarah",
        "last_name": "Chen",
        "company": "TechStartup Inc",
        "title": "CEO & Founder",
        "linkedin_url": "https://linkedin.com/in/sarahchen",
        "interested_in": "linkedin_presence",
        "source": "linkedin_landing_page"
    },
    {
        "email": "mike.johnson@growthventures.com",
        "first_name": "Mike",
        "last_name": "Johnson",
        "company": "Growth Ventures",
        "title": "Co-Founder",
        "linkedin_url": "https://linkedin.com/in/mikejohnson",
        "interested_in": "customer_voice_research",
        "source": "webinar_signup"
    },
    {
        "email": "lisa.park@ecommercebrand.co",
        "first_name": "Lisa",
        "last_name": "Park",
        "company": "EcommerceBrand",
        "title": "Founder & CEO",
        "linkedin_url": "https://linkedin.com/in/lisapark",
        "interested_in": "linkedin_presence",
        "source": "organic_search",
        "industry": "d2c"
    },
    {
        "email": "david.miller@alphavc.com",
        "first_name": "David",
        "last_name": "Miller",
        "company": "Alpha VC Partners",
        "title": "Partner",
        "linkedin_url": "https://linkedin.com/in/davidmiller",
        "interested_in": "customer_voice_research",
        "source": "referral"
    },
    {
        "email": "emma.wilson@consultingpro.com",
        "first_name": "Emma",
        "last_name": "Wilson",
        "company": "Wilson Consulting",
        "title": "Business Coach & Consultant",
        "linkedin_url": "https://linkedin.com/in/emmawilson",
        "interested_in": "linkedin_presence",
        "source": "linkedin_landing_page"
    },
    {
        "email": "james.taylor@saasplatform.io",
        "first_name": "James",
        "last_name": "Taylor",
        "company": "SaaS Platform Co",
        "title": "CEO",
        "linkedin_url": "https://linkedin.com/in/jamestaylor",
        "interested_in": "customer_voice_research",
        "source": "content_download"
    },
    {
        "email": "amanda.brown@retailtech.com",
        "first_name": "Amanda",
        "last_name": "Brown",
        "company": "RetailTech Solutions",
        "title": "Founder",
        "linkedin_url": "https://linkedin.com/in/amandabrown",
        "interested_in": "linkedin_presence",
        "source": "linkedin_ad",
        "industry": "retail"
    },
    {
        "email": "robert.garcia@venturefund.vc",
        "first_name": "Robert",
        "last_name": "Garcia",
        "company": "Venture Fund Capital",
        "title": "Venture Investor",
        "linkedin_url": "https://linkedin.com/in/robertgarcia",
        "interested_in": "customer_voice_research",
        "source": "event_registration"
    },
    {
        "email": "jennifer.lee@marketingagency.co",
        "first_name": "Jennifer",
        "last_name": "Lee",
        "company": "Lee Marketing Agency",
        "title": "Freelance Marketing Advisor",
        "linkedin_url": "https://linkedin.com/in/jenniferlee",
        "interested_in": "linkedin_presence",
        "source": "podcast_listener"
    },
    {
        "email": "chris.anderson@b2bsoftware.com",
        "first_name": "Chris",
        "last_name": "Anderson",
        "company": "B2B Software Inc",
        "title": "Co-Founder & CTO",
        "linkedin_url": "https://linkedin.com/in/chrisanderson",
        "interested_in": "customer_voice_research",
        "source": "linkedin_landing_page"
    }
]


def main():
    print("\n" + "=" * 60)
    print("LEAD GENERATION AGENT - PROCESSING 10 LEADS")
    print("=" * 60)

    # Initialize agent
    agent = LeadGenerationAgent()

    processed_leads = []

    # Process each lead
    for i, lead_data in enumerate(sample_leads, 1):
        print(f"\n--- Processing Lead {i}/10 ---")
        try:
            lead = agent.process_landing_page_lead(lead_data)
            processed_leads.append({
                "id": lead.id,
                "name": f"{lead.first_name} {lead.last_name}",
                "email": lead.email,
                "company": lead.company,
                "score": lead.score,
                "audience_type": lead.audience_type.value,
                "service": lead.interested_service.value,
                "status": lead.status.value
            })
            print(f"    Name: {lead.first_name} {lead.last_name}")
            print(f"    Company: {lead.company}")
            print(f"    Score: {lead.score}")
            print(f"    Audience: {lead.audience_type.value}")
            print(f"    Service: {lead.interested_service.value}")
        except Exception as e:
            print(f"    ERROR: {e}")

    # Show pipeline summary
    print("\n" + "=" * 60)
    print("PIPELINE SUMMARY")
    print("=" * 60)

    summary = agent.get_pipeline_summary()
    print(f"\nTotal Leads: {summary['total_leads']}")

    print("\nBy Status:")
    for status, count in summary['by_status'].items():
        print(f"  {status}: {count}")

    print("\nBy Service:")
    for service, count in summary['by_service'].items():
        print(f"  {service}: {count}")

    print("\nBy Audience Type:")
    for audience, count in summary['by_audience'].items():
        print(f"  {audience}: {count}")

    print("\nHigh Priority Leads (Score >= 70):")
    for lead in summary['high_priority']:
        print(f"  - {lead['name']} @ {lead['company']} (Score: {lead['score']})")

    # Run outreach
    print("\n" + "=" * 60)
    print("RUNNING DAILY OUTREACH")
    print("=" * 60)

    outreach_count = agent.run_daily_outreach()

    print(f"\n{'=' * 60}")
    print(f"COMPLETED: Processed {len(processed_leads)} leads, sent {outreach_count} outreach messages")
    print("=" * 60)

    return processed_leads


if __name__ == "__main__":
    main()
