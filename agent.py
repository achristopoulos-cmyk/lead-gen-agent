"""
Lead Generation Agent for Zag Marketing Services
Handles outreach automation for:
1. LinkedIn Presence Building (Join the Zag)
2. Customer Voice Research & Market Validation
"""

import json
import os
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass, asdict
from enum import Enum

from attio_integration import AttioClient
from lead_scoring import LeadScorer, LeadScore
from outreach_sequences import OutreachManager, ServiceType
from resend_integration import ResendClient


class LeadStatus(Enum):
    NEW = "new"
    CONTACTED = "contacted"
    ENGAGED = "engaged"
    QUALIFIED = "qualified"
    MEETING_SCHEDULED = "meeting_scheduled"
    PROPOSAL_SENT = "proposal_sent"
    WON = "won"
    LOST = "lost"


class AudienceType(Enum):
    B2B_FOUNDER = "b2b_founder"
    B2C_FOUNDER = "b2c_founder"
    VC_INVESTOR = "vc_investor"
    CONSULTANT_COACH = "consultant_coach"


@dataclass
class Lead:
    id: str
    email: str
    first_name: str
    last_name: str
    company: str
    title: str
    linkedin_url: Optional[str]
    audience_type: AudienceType
    interested_service: ServiceType
    status: LeadStatus
    score: int
    source: str
    created_at: str
    last_contacted: Optional[str]
    next_action: Optional[str]
    next_action_date: Optional[str]
    notes: list
    attio_id: Optional[str] = None

    def to_dict(self):
        data = asdict(self)
        data['audience_type'] = self.audience_type.value
        data['interested_service'] = self.interested_service.value
        data['status'] = self.status.value
        return data


class LeadGenerationAgent:
    """
    Main agent that orchestrates lead generation activities:
    - Processes incoming leads from landing pages
    - Scores and qualifies leads
    - Manages outreach sequences
    - Syncs with HubSpot CRM
    """

    def __init__(self, config_path: str = "config.json"):
        self.config = self._load_config(config_path)
        self.attio = AttioClient(self.config.get("attio_api_key"))
        self.resend = ResendClient(
            api_key=self.config.get("resend_api_key"),
            from_email=self.config.get("resend_from_email"),
            from_name=self.config.get("resend_from_name")
        )
        self.scorer = LeadScorer()
        self.outreach = OutreachManager()
        self.leads_db_path = self.config.get("leads_db_path", "leads_database.json")
        self.leads = self._load_leads()

    def _load_config(self, path: str) -> dict:
        config = {}
        # Load from file if exists
        if os.path.exists(path):
            with open(path, 'r') as f:
                config = json.load(f)

        # Override with environment variables (for production deployment)
        env_mappings = {
            "ATTIO_API_KEY": "attio_api_key",
            "ATTIO_ENABLED": "attio_enabled",
            "RESEND_API_KEY": "resend_api_key",
            "RESEND_ENABLED": "resend_enabled",
            "RESEND_FROM_EMAIL": "resend_from_email",
            "RESEND_FROM_NAME": "resend_from_name",
        }

        for env_key, config_key in env_mappings.items():
            env_value = os.environ.get(env_key)
            if env_value:
                # Handle boolean values
                if env_value.lower() in ['true', '1', 'yes']:
                    config[config_key] = True
                elif env_value.lower() in ['false', '0', 'no']:
                    config[config_key] = False
                else:
                    config[config_key] = env_value

        return config

    def _load_leads(self) -> dict:
        if os.path.exists(self.leads_db_path):
            with open(self.leads_db_path, 'r') as f:
                return json.load(f)
        return {}

    def _save_leads(self):
        with open(self.leads_db_path, 'w') as f:
            json.dump(self.leads, f, indent=2)

    def process_landing_page_lead(self, form_data: dict) -> Lead:
        """
        Process a new lead from landing page form submission.
        Called by webhook handler.
        """
        # Determine audience type from form data
        audience_type = self._classify_audience(form_data)

        # Determine interested service
        service = self._determine_service_interest(form_data)

        # Create lead object
        lead_id = f"lead_{datetime.now().strftime('%Y%m%d%H%M%S')}_{form_data.get('email', '')[:5]}"

        lead = Lead(
            id=lead_id,
            email=form_data.get('email', ''),
            first_name=form_data.get('first_name', ''),
            last_name=form_data.get('last_name', ''),
            company=form_data.get('company', ''),
            title=form_data.get('title', ''),
            linkedin_url=form_data.get('linkedin_url'),
            audience_type=audience_type,
            interested_service=service,
            status=LeadStatus.NEW,
            score=0,
            source=form_data.get('source', 'landing_page'),
            created_at=datetime.now().isoformat(),
            last_contacted=None,
            next_action="initial_outreach",
            next_action_date=datetime.now().isoformat(),
            notes=[]
        )

        # Score the lead
        lead.score = self.scorer.calculate_score(lead)

        # Save to local database
        self.leads[lead_id] = lead.to_dict()
        self._save_leads()

        # Sync to Attio CRM
        if self.config.get("attio_enabled", False):
            attio_id = self.attio.create_or_update_person(lead)
            lead.attio_id = attio_id
            self.leads[lead_id]['attio_id'] = attio_id
            self._save_leads()

        # Queue initial outreach
        self._queue_outreach(lead)

        print(f"[AGENT] New lead processed: {lead.email} | Score: {lead.score} | Service: {service.value}")

        return lead

    def _classify_audience(self, form_data: dict) -> AudienceType:
        """Classify lead into audience segment based on form data."""
        title = form_data.get('title', '').lower()
        company = form_data.get('company', '').lower()

        if any(term in title for term in ['founder', 'ceo', 'co-founder', 'owner']):
            # Check if B2B or B2C based on company/industry
            industry = form_data.get('industry', '').lower()
            if any(term in industry for term in ['consumer', 'retail', 'ecommerce', 'd2c']):
                return AudienceType.B2C_FOUNDER
            return AudienceType.B2B_FOUNDER

        if any(term in title for term in ['investor', 'partner', 'vc', 'venture']):
            return AudienceType.VC_INVESTOR

        if any(term in title for term in ['consultant', 'coach', 'advisor', 'freelance']):
            return AudienceType.CONSULTANT_COACH

        return AudienceType.B2B_FOUNDER  # Default

    def _determine_service_interest(self, form_data: dict) -> ServiceType:
        """Determine which service the lead is interested in."""
        service_field = form_data.get('interested_in', '').lower()

        if 'linkedin' in service_field or 'presence' in service_field or 'zag' in service_field:
            return ServiceType.LINKEDIN_PRESENCE
        if 'research' in service_field or 'validation' in service_field or 'voice' in service_field:
            return ServiceType.CUSTOMER_VOICE_RESEARCH

        # Default based on page source
        source = form_data.get('source', '').lower()
        if 'linkedin' in source:
            return ServiceType.LINKEDIN_PRESENCE

        return ServiceType.CUSTOMER_VOICE_RESEARCH

    def _queue_outreach(self, lead: Lead):
        """Queue the appropriate outreach sequence for a lead."""
        sequence = self.outreach.get_sequence(
            service=lead.interested_service,
            audience=lead.audience_type
        )

        # Store the sequence steps in lead notes
        lead.notes.append({
            "timestamp": datetime.now().isoformat(),
            "action": "sequence_assigned",
            "sequence": sequence.name,
            "steps": len(sequence.steps)
        })

    def run_daily_outreach(self):
        """
        Execute daily outreach tasks:
        - Send scheduled emails/messages
        - Follow up on engaged leads
        - Update lead statuses
        """
        print(f"\n[AGENT] Running daily outreach - {datetime.now().strftime('%Y-%m-%d')}")

        today = datetime.now().date()
        outreach_count = 0

        for lead_id, lead_data in self.leads.items():
            if lead_data.get('next_action_date'):
                action_date = datetime.fromisoformat(lead_data['next_action_date']).date()

                if action_date <= today and lead_data['status'] not in ['won', 'lost']:
                    self._execute_outreach_step(lead_id, lead_data)
                    outreach_count += 1

        print(f"[AGENT] Completed {outreach_count} outreach actions")
        return outreach_count

    def _execute_outreach_step(self, lead_id: str, lead_data: dict):
        """Execute the next outreach step for a lead."""
        service = ServiceType(lead_data['interested_service'])
        audience = AudienceType(lead_data['audience_type'])
        step = lead_data.get('next_action', 'initial_outreach')

        # Get personalized message
        message = self.outreach.generate_message(
            service=service,
            audience=audience,
            lead_data=lead_data,
            step=step
        )

        print(f"\n[OUTREACH] To: {lead_data['email']}")
        print(f"[OUTREACH] Subject: {message['subject']}")
        print(f"[OUTREACH] Channel: {message['channel']}")

        # Send email if channel is email and Resend is configured
        email_sent = False
        email_result = None

        if message['channel'] == 'email' and self.config.get("resend_enabled", False):
            email_result = self.resend.send_outreach_email(
                to=lead_data['email'],
                subject=message['subject'],
                body=message['body'],
                lead_id=lead_id,
                sequence_step=step
            )
            email_sent = email_result.success
            if email_sent:
                print(f"[OUTREACH] Email sent! ID: {email_result.message_id}")
            else:
                print(f"[OUTREACH] Email failed: {email_result.error}")
        elif message['channel'] in ['linkedin_message', 'linkedin_connection']:
            print(f"[OUTREACH] LinkedIn action required (manual): {message['channel']}")
        else:
            print(f"[OUTREACH] Preview: {message['body'][:100]}...")

        # Determine next step in sequence
        next_steps = {
            'initial_outreach': ('follow_up_1', 3),
            'follow_up_1': ('follow_up_2', 5),
            'follow_up_2': ('breakup', 7),
            'breakup': (None, 0)
        }
        next_action, delay_days = next_steps.get(step, (None, 0))

        # Update lead status
        self.leads[lead_id]['status'] = 'contacted'
        self.leads[lead_id]['last_contacted'] = datetime.now().isoformat()
        self.leads[lead_id]['next_action'] = next_action
        if next_action:
            self.leads[lead_id]['next_action_date'] = (datetime.now() + timedelta(days=delay_days)).isoformat()
        else:
            self.leads[lead_id]['next_action_date'] = None

        # Log the outreach
        note = {
            "timestamp": datetime.now().isoformat(),
            "action": "outreach_sent",
            "message_type": step,
            "channel": message['channel'],
            "email_sent": email_sent
        }
        if email_result and email_result.message_id:
            note["email_id"] = email_result.message_id

        self.leads[lead_id]['notes'].append(note)
        self._save_leads()

        # Sync status to Attio
        if self.config.get("attio_enabled", False) and lead_data.get('attio_id'):
            self.attio.update_person_status(lead_data['attio_id'], 'contacted')

    def get_pipeline_summary(self) -> dict:
        """Get summary of current lead pipeline."""
        summary = {
            "total_leads": len(self.leads),
            "by_status": {},
            "by_service": {},
            "by_audience": {},
            "high_priority": []
        }

        for lead_id, lead_data in self.leads.items():
            status = lead_data.get('status', 'new')
            service = lead_data.get('interested_service', 'unknown')
            audience = lead_data.get('audience_type', 'unknown')

            summary["by_status"][status] = summary["by_status"].get(status, 0) + 1
            summary["by_service"][service] = summary["by_service"].get(service, 0) + 1
            summary["by_audience"][audience] = summary["by_audience"].get(audience, 0) + 1

            if lead_data.get('score', 0) >= 70:
                summary["high_priority"].append({
                    "name": f"{lead_data['first_name']} {lead_data['last_name']}",
                    "company": lead_data['company'],
                    "score": lead_data['score']
                })

        return summary

    def add_manual_lead(self, lead_data: dict) -> Lead:
        """Add a lead manually (from LinkedIn prospecting, etc.)"""
        lead_data['source'] = lead_data.get('source', 'manual_entry')
        return self.process_landing_page_lead(lead_data)


# CLI interface for testing
if __name__ == "__main__":
    agent = LeadGenerationAgent()

    # Example: Process a test lead
    test_lead = {
        "email": "sarah@techstartup.com",
        "first_name": "Sarah",
        "last_name": "Chen",
        "company": "TechStartup Inc",
        "title": "CEO & Founder",
        "linkedin_url": "https://linkedin.com/in/sarahchen",
        "interested_in": "linkedin_presence",
        "source": "linkedin_landing_page"
    }

    print("\n=== Lead Generation Agent ===\n")
    lead = agent.process_landing_page_lead(test_lead)

    print("\n--- Pipeline Summary ---")
    summary = agent.get_pipeline_summary()
    print(json.dumps(summary, indent=2))
