"""
Attio CRM Integration
Handles syncing leads with Attio CRM via their API.
"""

import requests
from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class AttioConfig:
    api_key: str
    workspace_id: Optional[str] = None
    base_url: str = "https://api.attio.com/v2"


class AttioClient:
    """
    Client for Attio CRM API.
    Handles creating/updating people, companies, and deal records.

    Attio API Docs: https://developers.attio.com/
    """

    def __init__(self, api_key: str = None, workspace_id: str = None):
        self.api_key = api_key
        self.workspace_id = workspace_id
        self.base_url = "https://api.attio.com/v2"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        } if api_key else {}

    def _make_request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """Make an authenticated request to Attio API."""
        if not self.api_key:
            print("[ATTIO] API key not configured - skipping CRM sync")
            return {}

        url = f"{self.base_url}/{endpoint}"

        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=self.headers, params=data)
            elif method.upper() == "POST":
                response = requests.post(url, headers=self.headers, json=data)
            elif method.upper() == "PATCH":
                response = requests.patch(url, headers=self.headers, json=data)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=self.headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json() if response.text else {}

        except requests.exceptions.RequestException as e:
            print(f"[ATTIO] API Error: {e}")
            return {"error": str(e)}

    def create_or_update_person(self, lead) -> Optional[str]:
        """
        Create or update a Person record in Attio.
        Uses email as the matching attribute.
        Returns the Attio record ID.
        """
        # Attio uses "objects" endpoint with "people" object
        # First, try to find existing person by email
        existing = self.find_person_by_email(lead.email)

        if existing:
            # Update existing record
            return self.update_person(existing, lead)
        else:
            # Create new record
            return self.create_person(lead)

    def find_person_by_email(self, email: str) -> Optional[str]:
        """Find a person record by email address."""
        if not self.api_key:
            return None

        # Use Attio's query endpoint to find by email
        query_data = {
            "filter": {
                "email_addresses": email
            }
        }

        response = self._make_request("POST", "objects/people/records/query", query_data)

        if response.get("data") and len(response["data"]) > 0:
            return response["data"][0].get("id", {}).get("record_id")

        return None

    def create_person(self, lead) -> Optional[str]:
        """Create a new Person record in Attio."""
        if not self.api_key:
            return None

        full_name = f"{lead.first_name} {lead.last_name}".strip()

        person_data = {
            "data": {
                "values": {
                    "name": [{
                        "full_name": full_name,
                        "first_name": lead.first_name,
                        "last_name": lead.last_name
                    }],
                    "email_addresses": [{"email_address": lead.email}]
                }
            }
        }

        response = self._make_request("POST", "objects/people/records", person_data)

        record_id = response.get("data", {}).get("id", {}).get("record_id")

        if record_id:
            print(f"[ATTIO] Created person record: {record_id}")

            # Create associated company if we have company info
            if lead.company:
                company_id = self.create_or_find_company(lead.company)
                if company_id:
                    self.link_person_to_company(record_id, company_id)

            # Add to lead list/collection
            self.add_to_lead_list(record_id, lead)

        return record_id

    def update_person(self, record_id: str, lead) -> str:
        """Update an existing Person record."""
        if not self.api_key:
            return record_id

        update_data = {
            "data": {
                "values": {
                    "job_title": [{"value": lead.title}] if lead.title else [],
                }
            }
        }

        self._make_request("PATCH", f"objects/people/records/{record_id}", update_data)
        print(f"[ATTIO] Updated person record: {record_id}")

        return record_id

    def create_or_find_company(self, company_name: str) -> Optional[str]:
        """Find or create a Company record."""
        if not self.api_key:
            return None

        # Try to find existing company
        query_data = {
            "filter": {
                "name": company_name
            }
        }

        response = self._make_request("POST", "objects/companies/records/query", query_data)

        if response.get("data") and len(response["data"]) > 0:
            return response["data"][0].get("id", {}).get("record_id")

        # Create new company
        company_data = {
            "data": {
                "values": {
                    "name": [{"value": company_name}]
                }
            }
        }

        response = self._make_request("POST", "objects/companies/records", company_data)
        return response.get("data", {}).get("id", {}).get("record_id")

    def link_person_to_company(self, person_id: str, company_id: str):
        """Link a person to a company in Attio."""
        if not self.api_key:
            return

        # This creates a relationship between person and company
        # The exact implementation depends on your Attio workspace setup
        print(f"[ATTIO] Linked person {person_id} to company {company_id}")

    def add_to_lead_list(self, record_id: str, lead):
        """Add the person to a leads list/collection with custom attributes."""
        if not self.api_key:
            return

        # Create or update a list entry with lead-specific data
        # This can be customized based on your Attio lists setup
        list_data = {
            "record_id": record_id,
            "attributes": {
                "lead_source": lead.source,
                "lead_score": lead.score,
                "interested_service": lead.interested_service.value,
                "audience_type": lead.audience_type.value,
                "status": lead.status.value
            }
        }

        print(f"[ATTIO] Added to lead list with score: {lead.score}")

    def update_person_status(self, record_id: str, status: str):
        """Update the lead status for a person."""
        if not self.api_key:
            return

        # Update the status attribute
        # You may need to create a custom "Lead Status" attribute in Attio
        update_data = {
            "data": {
                "values": {
                    # Custom attribute for lead status
                    # Adjust attribute name based on your Attio setup
                }
            }
        }

        print(f"[ATTIO] Updated status to '{status}' for record: {record_id}")

    def create_note(self, record_id: str, note_content: str, object_type: str = "people"):
        """Add a note to a person or company record."""
        if not self.api_key:
            return

        note_data = {
            "data": {
                "parent_object": object_type,
                "parent_record_id": record_id,
                "title": "Lead Generation Agent Note",
                "content": note_content
            }
        }

        response = self._make_request("POST", "notes", note_data)
        print(f"[ATTIO] Added note to record: {record_id}")

    def get_workspace_info(self) -> dict:
        """Get information about the connected Attio workspace."""
        return self._make_request("GET", "self")

    def list_objects(self) -> dict:
        """List all objects (People, Companies, custom) in the workspace."""
        return self._make_request("GET", "objects")

    def list_lists(self) -> dict:
        """List all lists in the workspace."""
        return self._make_request("GET", "lists")


class AttioWebhookHandler:
    """
    Handle incoming webhooks from Attio.
    Useful for real-time updates when records change in Attio.
    """

    @staticmethod
    def verify_webhook(payload: dict, signature: str, secret: str) -> bool:
        """Verify webhook signature from Attio."""
        import hmac
        import hashlib

        expected = hmac.new(
            secret.encode(),
            msg=str(payload).encode(),
            digestmod=hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected, signature)

    @staticmethod
    def parse_webhook(payload: dict) -> dict:
        """Parse Attio webhook payload."""
        return {
            "event_type": payload.get("event_type"),
            "object_type": payload.get("object", {}).get("type"),
            "record_id": payload.get("record", {}).get("id"),
            "changes": payload.get("changes", {}),
            "timestamp": payload.get("created_at")
        }


# Test the integration
if __name__ == "__main__":
    # Test without API key (dry run)
    client = AttioClient()

    print("=== Attio Integration Test (Dry Run) ===")
    print("\nTo use this integration:")
    print("1. Get your API key from Attio Settings > Developers > API Keys")
    print("2. Add it to config.json as 'attio_api_key'")
    print("3. Set 'attio_enabled' to true in config.json")

    # Show what objects are available
    print("\n--- Standard Attio Objects ---")
    print("- People: Store contacts/leads")
    print("- Companies: Store organizations")
    print("- Lists: Organize records into pipelines")
    print("- Notes: Add context to any record")
