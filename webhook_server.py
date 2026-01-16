"""
Webhook Server for Landing Page Lead Capture
Receives form submissions and processes them through the lead generation agent.

Supports integrations with:
- Direct form submissions
- Webflow forms
- Typeform
- Tally
- Carrd
- Custom landing pages
"""

from flask import Flask, request, jsonify
from functools import wraps
import json
import hmac
import hashlib
import os
from datetime import datetime

from agent import LeadGenerationAgent

app = Flask(__name__)
agent = LeadGenerationAgent()

# Configuration
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "your-webhook-secret")


def verify_signature(f):
    """Decorator to verify webhook signatures."""
    @wraps(f)
    def decorated(*args, **kwargs):
        signature = request.headers.get("X-Webhook-Signature", "")

        if WEBHOOK_SECRET != "your-webhook-secret":
            expected = hmac.new(
                WEBHOOK_SECRET.encode(),
                msg=request.data,
                digestmod=hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(expected, signature):
                return jsonify({"error": "Invalid signature"}), 401

        return f(*args, **kwargs)
    return decorated


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agent": "lead-generation-agent"
    })


@app.route("/webhook/lead", methods=["POST"])
@verify_signature
def receive_lead():
    """
    Main webhook endpoint for receiving leads.
    Accepts JSON payload with lead data.
    """
    try:
        data = request.json

        # Map common field variations
        form_data = normalize_form_data(data)

        # Process through agent
        lead = agent.process_landing_page_lead(form_data)

        return jsonify({
            "success": True,
            "lead_id": lead.id,
            "score": lead.score,
            "message": f"Lead {lead.email} processed successfully"
        }), 200

    except Exception as e:
        print(f"[WEBHOOK ERROR] {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/webhook/webflow", methods=["POST"])
def webflow_webhook():
    """
    Webflow form submission webhook.
    Webflow sends form data in a specific format.
    """
    try:
        data = request.json

        # Webflow sends data under 'data' key
        form_data = data.get("data", data)

        # Add source identifier
        form_data["source"] = "webflow"

        # Normalize and process
        normalized = normalize_form_data(form_data)
        lead = agent.process_landing_page_lead(normalized)

        return jsonify({
            "success": True,
            "lead_id": lead.id
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/webhook/typeform", methods=["POST"])
def typeform_webhook():
    """
    Typeform webhook integration.
    Typeform sends answers in a specific nested format.
    """
    try:
        data = request.json

        # Extract answers from Typeform format
        form_response = data.get("form_response", {})
        answers = form_response.get("answers", [])
        definition = form_response.get("definition", {})
        fields = {f["id"]: f for f in definition.get("fields", [])}

        # Map Typeform answers to our format
        form_data = {"source": "typeform"}

        for answer in answers:
            field_id = answer.get("field", {}).get("id")
            field_info = fields.get(field_id, {})
            field_title = field_info.get("title", "").lower()

            # Extract value based on answer type
            value = None
            if "email" in answer:
                value = answer["email"]
            elif "text" in answer:
                value = answer["text"]
            elif "choice" in answer:
                value = answer["choice"].get("label")

            # Map to our field names
            if "email" in field_title:
                form_data["email"] = value
            elif "first" in field_title and "name" in field_title:
                form_data["first_name"] = value
            elif "last" in field_title and "name" in field_title:
                form_data["last_name"] = value
            elif "company" in field_title:
                form_data["company"] = value
            elif "title" in field_title or "role" in field_title:
                form_data["title"] = value
            elif "linkedin" in field_title:
                form_data["linkedin_url"] = value
            elif "interest" in field_title or "service" in field_title:
                form_data["interested_in"] = value

        normalized = normalize_form_data(form_data)
        lead = agent.process_landing_page_lead(normalized)

        return jsonify({
            "success": True,
            "lead_id": lead.id
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/webhook/tally", methods=["POST"])
def tally_webhook():
    """
    Tally form webhook integration.
    """
    try:
        data = request.json

        # Tally sends fields array
        fields = data.get("data", {}).get("fields", [])

        form_data = {"source": "tally"}

        for field in fields:
            label = field.get("label", "").lower()
            value = field.get("value")

            if "email" in label:
                form_data["email"] = value
            elif "first" in label:
                form_data["first_name"] = value
            elif "last" in label:
                form_data["last_name"] = value
            elif "company" in label:
                form_data["company"] = value
            elif "title" in label or "role" in label:
                form_data["title"] = value
            elif "linkedin" in label:
                form_data["linkedin_url"] = value
            elif "interest" in label or "service" in label:
                form_data["interested_in"] = value

        normalized = normalize_form_data(form_data)
        lead = agent.process_landing_page_lead(normalized)

        return jsonify({
            "success": True,
            "lead_id": lead.id
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/webhook/generic", methods=["POST"])
def generic_webhook():
    """
    Generic webhook that accepts any JSON format.
    Attempts to intelligently map fields.
    """
    try:
        data = request.json
        form_data = normalize_form_data(data)
        form_data["source"] = data.get("source", "generic_webhook")

        lead = agent.process_landing_page_lead(form_data)

        return jsonify({
            "success": True,
            "lead_id": lead.id,
            "score": lead.score
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def normalize_form_data(data: dict) -> dict:
    """
    Normalize various field name formats to our standard format.
    Handles common variations in form field naming.
    """
    normalized = {}

    # Field mapping - maps common variations to our standard names
    field_mappings = {
        "email": ["email", "email_address", "emailAddress", "Email", "EMAIL", "e-mail"],
        "first_name": ["first_name", "firstName", "first", "First Name", "fname", "given_name"],
        "last_name": ["last_name", "lastName", "last", "Last Name", "lname", "family_name", "surname"],
        "company": ["company", "company_name", "companyName", "Company", "organization", "org"],
        "title": ["title", "job_title", "jobTitle", "role", "position", "Job Title"],
        "linkedin_url": ["linkedin_url", "linkedinUrl", "linkedin", "LinkedIn", "linkedin_profile"],
        "interested_in": ["interested_in", "interestedIn", "service", "interest", "Service Interest"],
        "source": ["source", "utm_source", "referrer", "lead_source"],
        "industry": ["industry", "Industry", "sector"]
    }

    for standard_name, variations in field_mappings.items():
        for variation in variations:
            if variation in data and data[variation]:
                normalized[standard_name] = data[variation]
                break

    # Handle full name splitting
    if "name" in data and "first_name" not in normalized:
        full_name = data["name"]
        if isinstance(full_name, str):
            parts = full_name.strip().split(" ", 1)
            normalized["first_name"] = parts[0]
            if len(parts) > 1:
                normalized["last_name"] = parts[1]

    # Ensure required fields have defaults
    normalized.setdefault("email", "")
    normalized.setdefault("first_name", "Unknown")
    normalized.setdefault("last_name", "")
    normalized.setdefault("company", "")
    normalized.setdefault("title", "")
    normalized.setdefault("source", "landing_page")

    return normalized


# API Endpoints for Manual Operations

@app.route("/api/leads", methods=["GET"])
def get_leads():
    """Get all leads."""
    return jsonify(agent.leads)


@app.route("/api/leads/<lead_id>", methods=["GET"])
def get_lead(lead_id):
    """Get a specific lead."""
    lead = agent.leads.get(lead_id)
    if lead:
        return jsonify(lead)
    return jsonify({"error": "Lead not found"}), 404


@app.route("/api/leads/add", methods=["POST"])
def add_manual_lead():
    """Manually add a lead."""
    try:
        data = request.json
        lead = agent.add_manual_lead(data)
        return jsonify({
            "success": True,
            "lead_id": lead.id,
            "score": lead.score
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/pipeline", methods=["GET"])
def get_pipeline():
    """Get pipeline summary."""
    summary = agent.get_pipeline_summary()
    return jsonify(summary)


@app.route("/api/outreach/run", methods=["POST"])
def run_outreach():
    """Trigger daily outreach run manually."""
    count = agent.run_daily_outreach()
    return jsonify({
        "success": True,
        "outreach_count": count
    })


@app.route("/api/outreach/preview/<lead_id>", methods=["GET"])
def preview_outreach(lead_id):
    """Preview the next outreach message for a lead."""
    lead_data = agent.leads.get(lead_id)

    if not lead_data:
        return jsonify({"error": "Lead not found"}), 404

    from outreach_sequences import ServiceType, AudienceType

    service = ServiceType(lead_data['interested_service'])
    audience = AudienceType(lead_data['audience_type'])

    message = agent.outreach.generate_message(
        service=service,
        audience=audience,
        lead_data=lead_data,
        step=lead_data.get('next_action', 'initial_outreach')
    )

    return jsonify(message)


if __name__ == "__main__":
    print("\n=== Lead Generation Agent - Webhook Server ===")
    print("\nEndpoints:")
    print("  POST /webhook/lead     - Generic lead submission")
    print("  POST /webhook/webflow  - Webflow form integration")
    print("  POST /webhook/typeform - Typeform integration")
    print("  POST /webhook/tally    - Tally form integration")
    print("  POST /webhook/generic  - Any JSON format")
    print("\n  GET  /api/leads        - List all leads")
    print("  GET  /api/pipeline     - Pipeline summary")
    print("  POST /api/outreach/run - Trigger outreach")
    print("\nStarting server on http://localhost:5000")

    app.run(host="0.0.0.0", port=5000, debug=True)
