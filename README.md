# Lead Generation Agent for Zag Marketing Services

Automated lead generation system for two core services:
1. **Build a LinkedIn Presence that feels like you - Join the Zag** - Weekly actionable tools
2. **Customer Voice Research and Market Validation** - Deep customer insights

## Features

- **Lead Capture**: Webhook endpoints for Webflow, Typeform, Tally, and custom forms
- **Lead Scoring**: Automatic scoring based on title, company, source, and engagement
- **Personalized Outreach**: Tailored email/LinkedIn sequences for each service and audience
- **Attio CRM Integration**: Automatic sync of leads to Attio
- **Automated Scheduling**: Daily outreach runs and reporting

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure the Agent
Edit `config.json`:
```json
{
  "attio_api_key": "YOUR_ATTIO_API_KEY",
  "attio_enabled": true,
  "email_signature": {
    "name": "Your Name",
    "title": "Your Title"
  }
}
```

### 3. Run the Webhook Server
```bash
python webhook_server.py
```
Server starts at `http://localhost:5000`

### 4. Start the Scheduler (for automated outreach)
```bash
python scheduler.py
```

## Webhook Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /webhook/lead` | Generic JSON lead submission |
| `POST /webhook/webflow` | Webflow form integration |
| `POST /webhook/typeform` | Typeform integration |
| `POST /webhook/tally` | Tally form integration |
| `POST /webhook/generic` | Auto-maps any JSON format |

### Example Lead Submission
```bash
curl -X POST http://localhost:5000/webhook/lead \
  -H "Content-Type: application/json" \
  -d '{
    "email": "sarah@startup.com",
    "first_name": "Sarah",
    "last_name": "Chen",
    "company": "TechStartup Inc",
    "title": "CEO & Founder",
    "linkedin_url": "https://linkedin.com/in/sarahchen",
    "interested_in": "linkedin_presence",
    "source": "linkedin_landing_page"
  }'
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/leads` | GET | List all leads |
| `/api/leads/<id>` | GET | Get specific lead |
| `/api/leads/add` | POST | Manually add lead |
| `/api/pipeline` | GET | Pipeline summary |
| `/api/outreach/run` | POST | Trigger outreach manually |
| `/api/outreach/preview/<id>` | GET | Preview next message |

## Target Audiences

The agent has tailored sequences for:
- **B2B Founders/CEOs** - Focus on sales & pipeline growth
- **B2C Founders** - Emphasis on brand story & investor relations
- **VC Investors** - Portfolio value proposition
- **Consultants/Coaches** - Inbound lead generation

## Lead Scoring

Leads are scored 0-100 based on:
- **Title** (0-30 pts): CEO/Founder = 30, Director = 18, Manager = 12
- **Company** (0-20 pts): Startup/SaaS indicators
- **Source** (0-20 pts): Referral = 20, LinkedIn Organic = 18
- **LinkedIn Profile** (0-15 pts): Has URL = 10

Score tiers:
- **Hot** (80-100): Immediate priority
- **Warm** (60-79): Active nurture
- **Cool** (40-59): Long-term nurture
- **Cold** (0-39): Low priority

## Outreach Sequences

Each service has a 4-step sequence:
1. **Initial Outreach** (Day 0) - Personalized intro email
2. **Follow-up 1** (Day 3) - Value-add content
3. **Follow-up 2** (Day 8) - LinkedIn connection
4. **Breakup** (Day 15) - Final touch

## Attio CRM Setup

1. Go to Attio Settings > Developers > API Keys
2. Create a new API key with People, Companies, and Lists access
3. Add to `config.json` as `attio_api_key`
4. Set `attio_enabled` to `true`

## Connecting Landing Pages

### Webflow
1. Go to your form settings
2. Add webhook: `https://your-domain.com/webhook/webflow`

### Typeform
1. Connect > Webhooks
2. Add endpoint: `https://your-domain.com/webhook/typeform`

### Tally
1. Integrations > Webhooks
2. URL: `https://your-domain.com/webhook/tally`

## File Structure

```
lead-gen-agent/
├── agent.py              # Main orchestration agent
├── outreach_sequences.py # Email/LinkedIn templates
├── attio_integration.py  # Attio CRM client
├── lead_scoring.py       # Scoring logic
├── webhook_server.py     # Flask webhook server
├── scheduler.py          # Automated task runner
├── config.json           # Configuration
├── leads_database.json   # Local lead storage
└── requirements.txt      # Python dependencies
```

## Production Deployment

For production, use gunicorn:
```bash
gunicorn webhook_server:app -w 4 -b 0.0.0.0:5000
```

Consider:
- Adding proper logging
- Using environment variables for secrets
- Setting up HTTPS via reverse proxy (nginx)
- Running scheduler as a systemd service

## Customizing Outreach Templates

Edit `outreach_sequences.py` to customize:
- Email subject lines
- Message body content
- Sequence timing
- Channel (email vs LinkedIn)
