"""
Outreach Sequences for Zag Marketing Services
Personalized email/LinkedIn message templates for each service and audience type.
"""

from dataclasses import dataclass
from typing import List, Dict
from enum import Enum


class ServiceType(Enum):
    LINKEDIN_PRESENCE = "linkedin_presence"
    CUSTOMER_VOICE_RESEARCH = "customer_voice_research"


class AudienceType(Enum):
    B2B_FOUNDER = "b2b_founder"
    B2C_FOUNDER = "b2c_founder"
    VC_INVESTOR = "vc_investor"
    CONSULTANT_COACH = "consultant_coach"


@dataclass
class OutreachStep:
    name: str
    delay_days: int
    channel: str  # email, linkedin_message, linkedin_connection
    subject_template: str
    body_template: str


@dataclass
class OutreachSequence:
    name: str
    service: ServiceType
    audience: AudienceType
    steps: List[OutreachStep]


class OutreachManager:
    """Manages outreach sequences and generates personalized messages."""

    def __init__(self):
        self.sequences = self._build_sequences()

    def _build_sequences(self) -> Dict[str, OutreachSequence]:
        sequences = {}

        # ===========================================
        # LINKEDIN PRESENCE SERVICE SEQUENCES
        # ===========================================

        # For B2B Founders
        sequences["linkedin_b2b_founder"] = OutreachSequence(
            name="LinkedIn Presence - B2B Founders",
            service=ServiceType.LINKEDIN_PRESENCE,
            audience=AudienceType.B2B_FOUNDER,
            steps=[
                OutreachStep(
                    name="initial_outreach",
                    delay_days=0,
                    channel="email",
                    subject_template="Quick question about {company}'s LinkedIn strategy",
                    body_template="""Hi {first_name},

I noticed you're building something interesting at {company}.

Here's what I've observed working with B2B founders: the ones who consistently win deals aren't always the loudest - they're the ones whose LinkedIn presence feels genuinely them while building trust with their ideal buyers.

Most founders I talk to are stuck between:
- Posting generic "thought leadership" that sounds like everyone else
- Staying silent because they don't know what to say
- Trying to go viral when what they actually need is to connect with 50 right people

I help founders build a LinkedIn presence that feels like you - not a personal branding consultant's version of you. Each week you get actionable tools to work on, not vague advice.

Would it be worth 15 minutes to explore if this could help {company}'s growth?

{signature}"""
                ),
                OutreachStep(
                    name="follow_up_1",
                    delay_days=3,
                    channel="email",
                    subject_template="Re: Quick question about {company}'s LinkedIn strategy",
                    body_template="""Hi {first_name},

Wanted to share something that might resonate:

One of my clients (B2B SaaS founder) went from posting once a month to building a genuine presence that attracted 3 enterprise leads in 6 weeks. The difference wasn't posting more - it was knowing exactly what to say and when.

The "Join the Zag" program gives you weekly actionable tools, not generic tips. You'll know exactly what to work on each week.

Open to a quick chat?

{signature}"""
                ),
                OutreachStep(
                    name="follow_up_2",
                    delay_days=5,
                    channel="linkedin_message",
                    subject_template="",
                    body_template="""{first_name} - saw your recent work at {company}.

I help B2B founders build LinkedIn presence that actually converts (without feeling salesy).

Worth connecting?"""
                ),
                OutreachStep(
                    name="breakup",
                    delay_days=7,
                    channel="email",
                    subject_template="Closing the loop",
                    body_template="""Hi {first_name},

I'll keep this short - I know you're busy building {company}.

If LinkedIn isn't a priority right now, totally get it. But if you ever want to explore building a presence that brings the right people to you (instead of chasing them), the door's always open.

Wishing you all the best,
{signature}"""
                )
            ]
        )

        # For B2C Founders
        sequences["linkedin_b2c_founder"] = OutreachSequence(
            name="LinkedIn Presence - B2C Founders",
            service=ServiceType.LINKEDIN_PRESENCE,
            audience=AudienceType.B2C_FOUNDER,
            steps=[
                OutreachStep(
                    name="initial_outreach",
                    delay_days=0,
                    channel="email",
                    subject_template="Thought about {company}'s founder story",
                    body_template="""Hi {first_name},

Consumer brands with a strong founder story tend to build communities, not just customer bases.

I help founders like you build a LinkedIn presence that:
- Attracts investors who get your vision
- Builds credibility for retail/partnership conversations
- Creates a founder narrative that resonates with your audience

The "Join the Zag" program gives you weekly actionable tools - each week you'll know exactly what to work on to build presence that feels authentically you.

Interested in learning more?

{signature}"""
                ),
                OutreachStep(
                    name="follow_up_1",
                    delay_days=3,
                    channel="email",
                    subject_template="Re: Thought about {company}'s founder story",
                    body_template="""Hi {first_name},

Quick follow-up: I know as a consumer brand founder, your focus is probably on product and customers (as it should be).

But here's the thing - the founders who build authentic LinkedIn presence often find it becomes a channel for:
- Retail buyer conversations
- Investor warm intros
- Partnership opportunities

15 minutes to explore if this makes sense for {company}?

{signature}"""
                )
            ]
        )

        # For VC Investors
        sequences["linkedin_vc_investor"] = OutreachSequence(
            name="LinkedIn Presence - VC Investors",
            service=ServiceType.LINKEDIN_PRESENCE,
            audience=AudienceType.VC_INVESTOR,
            steps=[
                OutreachStep(
                    name="initial_outreach",
                    delay_days=0,
                    channel="email",
                    subject_template="Helping your portfolio founders stand out",
                    body_template="""Hi {first_name},

I work with B2B founders on building LinkedIn presence that attracts customers and talent - without the cringe-worthy personal branding tactics.

Wondering if this might be valuable for any of your portfolio companies?

The "Join the Zag" program gives founders weekly actionable tools. It's designed for busy founders who don't want to become "content creators" but do want their expertise to attract opportunities.

Happy to share more details or jump on a quick call.

{signature}"""
                ),
                OutreachStep(
                    name="follow_up_1",
                    delay_days=4,
                    channel="linkedin_message",
                    subject_template="",
                    body_template="""Hi {first_name} - I help B2B founders build authentic LinkedIn presence (the kind that attracts deals, not just likes).

Thought this might be valuable for your portfolio. Worth connecting?"""
                )
            ]
        )

        # For Consultants/Coaches
        sequences["linkedin_consultant"] = OutreachSequence(
            name="LinkedIn Presence - Consultants",
            service=ServiceType.LINKEDIN_PRESENCE,
            audience=AudienceType.CONSULTANT_COACH,
            steps=[
                OutreachStep(
                    name="initial_outreach",
                    delay_days=0,
                    channel="email",
                    subject_template="Your LinkedIn could be your best sales channel",
                    body_template="""Hi {first_name},

As a {title}, your expertise is your product. But here's the challenge: how do you showcase that expertise without sounding like every other consultant on LinkedIn?

I help consultants and coaches build presence that:
- Positions you as the obvious choice for your ideal clients
- Creates inbound opportunities (so you're not always chasing)
- Feels like you, not a personal brand template

The "Join the Zag" program gives you weekly actionable tools. No fluff - just clear actions to take each week.

Worth 15 minutes to explore?

{signature}"""
                ),
                OutreachStep(
                    name="follow_up_1",
                    delay_days=3,
                    channel="email",
                    subject_template="Re: Your LinkedIn could be your best sales channel",
                    body_template="""Hi {first_name},

One thing I hear from consultants: "I know LinkedIn could work for me, I just don't know where to start."

That's exactly why I created a structured approach - each week you get specific tools to work on. No guessing, no random posting and hoping.

Would a quick chat be helpful?

{signature}"""
                )
            ]
        )

        # ===========================================
        # CUSTOMER VOICE RESEARCH SEQUENCES
        # ===========================================

        # For B2B Founders
        sequences["research_b2b_founder"] = OutreachSequence(
            name="Customer Voice Research - B2B Founders",
            service=ServiceType.CUSTOMER_VOICE_RESEARCH,
            audience=AudienceType.B2B_FOUNDER,
            steps=[
                OutreachStep(
                    name="initial_outreach",
                    delay_days=0,
                    channel="email",
                    subject_template="Before you build it - a question",
                    body_template="""Hi {first_name},

How confident are you that what you're building at {company} is exactly what your market needs?

I run Customer Voice Research and Market Validation - essentially, we talk to your target customers so you don't have to guess what they want.

Here's what you get:
- Deep interviews with your ideal customer profile
- Patterns and insights you can actually act on
- Validation (or redirection) before you invest more resources

Most founders I work with say the same thing after: "I wish I'd done this 6 months ago."

Would it be worth a conversation to explore if this could help {company}?

{signature}"""
                ),
                OutreachStep(
                    name="follow_up_1",
                    delay_days=3,
                    channel="email",
                    subject_template="Re: Before you build it - a question",
                    body_template="""Hi {first_name},

Quick story: Worked with a B2B founder who was about to spend 4 months building a feature their customers didn't actually want.

Customer Voice Research helped them pivot to what the market was actually asking for. Saved them months and launched to immediate traction.

Happy to share how this might apply to {company}.

{signature}"""
                ),
                OutreachStep(
                    name="follow_up_2",
                    delay_days=5,
                    channel="linkedin_message",
                    subject_template="",
                    body_template="""{first_name} - I help founders validate product direction through customer research. Before building, it helps to know you're building the right thing.

Worth connecting to share how this works?"""
                ),
                OutreachStep(
                    name="breakup",
                    delay_days=7,
                    channel="email",
                    subject_template="Last note on market validation",
                    body_template="""Hi {first_name},

I'll leave you with this thought:

The cost of customer research = a few thousand dollars and a couple weeks
The cost of building the wrong thing = months of work and potentially the business

If you ever want to de-risk your product decisions with real customer insights, I'm here.

All the best with {company},
{signature}"""
                )
            ]
        )

        # For B2C Founders
        sequences["research_b2c_founder"] = OutreachSequence(
            name="Customer Voice Research - B2C Founders",
            service=ServiceType.CUSTOMER_VOICE_RESEARCH,
            audience=AudienceType.B2C_FOUNDER,
            steps=[
                OutreachStep(
                    name="initial_outreach",
                    delay_days=0,
                    channel="email",
                    subject_template="Understanding your consumer better",
                    body_template="""Hi {first_name},

Consumer brands live and die by how well they understand their customers. Data tells you what they do - but do you know why?

I run Customer Voice Research - we conduct deep-dive interviews with your target consumers to uncover:
- What actually drives purchase decisions
- The language they use (gold for your marketing)
- Unmet needs your competitors are missing

This isn't focus groups or surveys. It's real conversations that give you insights you can act on.

Worth exploring for {company}?

{signature}"""
                ),
                OutreachStep(
                    name="follow_up_1",
                    delay_days=4,
                    channel="email",
                    subject_template="Re: Understanding your consumer better",
                    body_template="""Hi {first_name},

One thing Customer Voice Research consistently uncovers: the gap between what brands think their customers care about vs. what they actually care about.

For consumer brands, closing that gap is the difference between marketing that works and marketing that doesn't.

15 minutes to discuss how this could help {company}?

{signature}"""
                )
            ]
        )

        # For VC Investors
        sequences["research_vc_investor"] = OutreachSequence(
            name="Customer Voice Research - VC Investors",
            service=ServiceType.CUSTOMER_VOICE_RESEARCH,
            audience=AudienceType.VC_INVESTOR,
            steps=[
                OutreachStep(
                    name="initial_outreach",
                    delay_days=0,
                    channel="email",
                    subject_template="Market validation for your portfolio",
                    body_template="""Hi {first_name},

Do your portfolio companies validate product decisions with real customer research, or are they building on assumptions?

I run Customer Voice Research - we conduct structured interviews with target customers to validate (or redirect) product direction.

For portfolio companies, this means:
- Faster PMF by building what customers actually want
- Reduced pivot risk
- Customer insights that inform go-to-market

Happy to share how this has helped other startups - might be valuable for your companies.

{signature}"""
                )
            ]
        )

        # For Consultants/Coaches
        sequences["research_consultant"] = OutreachSequence(
            name="Customer Voice Research - Consultants",
            service=ServiceType.CUSTOMER_VOICE_RESEARCH,
            audience=AudienceType.CONSULTANT_COACH,
            steps=[
                OutreachStep(
                    name="initial_outreach",
                    delay_days=0,
                    channel="email",
                    subject_template="Offer this to your clients?",
                    body_template="""Hi {first_name},

As a {title}, you probably see this pattern: clients who build products/services without validating with their target market first.

I run Customer Voice Research - deep-dive customer interviews that validate product direction and uncover market opportunities.

Two ways we could work together:
1. I handle research for your clients who need it
2. We white-label the service under your brand

Worth a conversation to explore?

{signature}"""
                )
            ]
        )

        return sequences

    def get_sequence(self, service: ServiceType, audience: AudienceType) -> OutreachSequence:
        """Get the appropriate sequence for a service/audience combination."""
        service_prefix = "linkedin" if service == ServiceType.LINKEDIN_PRESENCE else "research"

        audience_suffix = {
            AudienceType.B2B_FOUNDER: "b2b_founder",
            AudienceType.B2C_FOUNDER: "b2c_founder",
            AudienceType.VC_INVESTOR: "vc_investor",
            AudienceType.CONSULTANT_COACH: "consultant"
        }.get(audience, "b2b_founder")

        key = f"{service_prefix}_{audience_suffix}"
        return self.sequences.get(key, self.sequences["linkedin_b2b_founder"])

    def generate_message(self, service: ServiceType, audience: AudienceType,
                         lead_data: dict, step: str = "initial_outreach") -> dict:
        """Generate a personalized message for a lead."""
        sequence = self.get_sequence(service, audience)

        # Find the step
        outreach_step = None
        for s in sequence.steps:
            if s.name == step:
                outreach_step = s
                break

        if not outreach_step:
            outreach_step = sequence.steps[0]

        # Personalize the message
        signature = """Best,
[Your Name]
[Your Title]

P.S. Reply to this email anytime - I read and respond to every message."""

        replacements = {
            "{first_name}": lead_data.get("first_name", "there"),
            "{last_name}": lead_data.get("last_name", ""),
            "{company}": lead_data.get("company", "your company"),
            "{title}": lead_data.get("title", "your role"),
            "{signature}": signature
        }

        subject = outreach_step.subject_template
        body = outreach_step.body_template

        for key, value in replacements.items():
            subject = subject.replace(key, value)
            body = body.replace(key, value)

        return {
            "subject": subject,
            "body": body,
            "channel": outreach_step.channel,
            "step_name": outreach_step.name
        }


# Test the sequences
if __name__ == "__main__":
    manager = OutreachManager()

    test_lead = {
        "first_name": "Sarah",
        "last_name": "Chen",
        "company": "TechStartup Inc",
        "title": "CEO & Founder"
    }

    print("=== LinkedIn Presence - B2B Founder Sequence ===\n")
    message = manager.generate_message(
        ServiceType.LINKEDIN_PRESENCE,
        AudienceType.B2B_FOUNDER,
        test_lead
    )
    print(f"Subject: {message['subject']}")
    print(f"Channel: {message['channel']}")
    print(f"\n{message['body']}")

    print("\n" + "="*50 + "\n")

    print("=== Customer Voice Research - B2B Founder Sequence ===\n")
    message = manager.generate_message(
        ServiceType.CUSTOMER_VOICE_RESEARCH,
        AudienceType.B2B_FOUNDER,
        test_lead
    )
    print(f"Subject: {message['subject']}")
    print(f"Channel: {message['channel']}")
    print(f"\n{message['body']}")
