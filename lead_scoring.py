"""
Lead Scoring System for Zag Marketing Services
Scores leads based on fit and engagement signals.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List


class LeadScore(Enum):
    HOT = "hot"         # 80-100: Ready for immediate outreach
    WARM = "warm"       # 60-79: Good fit, nurture with content
    COOL = "cool"       # 40-59: Moderate fit, long-term nurture
    COLD = "cold"       # 0-39: Low priority


@dataclass
class ScoringCriteria:
    name: str
    weight: int
    max_points: int


class LeadScorer:
    """
    Scores leads based on:
    - Demographic fit (title, company size, industry)
    - Behavioral signals (engagement, source)
    - Service alignment
    """

    def __init__(self):
        self.scoring_rules = self._build_scoring_rules()

    def _build_scoring_rules(self) -> Dict:
        return {
            # Title/Role Scoring (0-30 points)
            "title_scores": {
                "ceo": 30,
                "founder": 30,
                "co-founder": 30,
                "owner": 28,
                "president": 25,
                "managing director": 25,
                "partner": 25,
                "principal": 22,
                "vp": 20,
                "vice president": 20,
                "director": 18,
                "head of": 18,
                "chief": 25,
                "consultant": 20,
                "coach": 20,
                "advisor": 18,
                "investor": 25,
                "manager": 12,
                "lead": 10,
                "senior": 8,
                "default": 5
            },

            # Company Indicators (0-20 points)
            "company_signals": {
                "startup": 15,
                "ventures": 18,
                "capital": 18,
                "consulting": 15,
                "advisory": 15,
                "studios": 12,
                "labs": 12,
                "tech": 10,
                "saas": 15,
                "ai": 12,
                "default": 5
            },

            # Source Quality (0-20 points)
            "source_scores": {
                "referral": 20,
                "linkedin_organic": 18,
                "linkedin_landing_page": 15,
                "direct": 15,
                "webinar": 15,
                "content_download": 12,
                "linkedin_ad": 10,
                "google_ad": 8,
                "cold_list": 5,
                "manual_entry": 5,
                "default": 5
            },

            # LinkedIn Profile Completeness (0-15 points)
            "linkedin_bonus": {
                "has_url": 10,
                "profile_complete": 5
            },

            # Engagement Signals (0-15 points)
            "engagement_scores": {
                "replied": 15,
                "clicked_link": 10,
                "opened_multiple": 8,
                "opened_once": 5,
                "no_engagement": 0
            }
        }

    def calculate_score(self, lead) -> int:
        """Calculate total lead score (0-100)."""
        score = 0

        # Title Score
        score += self._score_title(lead.title)

        # Company Score
        score += self._score_company(lead.company)

        # Source Score
        score += self._score_source(lead.source)

        # LinkedIn Bonus
        score += self._score_linkedin(lead.linkedin_url)

        # Ensure score is in range
        return min(100, max(0, score))

    def _score_title(self, title: str) -> int:
        """Score based on job title."""
        if not title:
            return self.scoring_rules["title_scores"]["default"]

        title_lower = title.lower()

        # Check for exact matches first
        for key, points in self.scoring_rules["title_scores"].items():
            if key in title_lower:
                return points

        return self.scoring_rules["title_scores"]["default"]

    def _score_company(self, company: str) -> int:
        """Score based on company name signals."""
        if not company:
            return self.scoring_rules["company_signals"]["default"]

        company_lower = company.lower()

        for key, points in self.scoring_rules["company_signals"].items():
            if key in company_lower:
                return points

        return self.scoring_rules["company_signals"]["default"]

    def _score_source(self, source: str) -> int:
        """Score based on lead source."""
        if not source:
            return self.scoring_rules["source_scores"]["default"]

        return self.scoring_rules["source_scores"].get(
            source.lower(),
            self.scoring_rules["source_scores"]["default"]
        )

    def _score_linkedin(self, linkedin_url: str) -> int:
        """Bonus points for having LinkedIn profile."""
        if linkedin_url:
            return self.scoring_rules["linkedin_bonus"]["has_url"]
        return 0

    def update_engagement_score(self, current_score: int, engagement_type: str) -> int:
        """Update score based on engagement."""
        engagement_points = self.scoring_rules["engagement_scores"].get(
            engagement_type.lower(), 0
        )
        return min(100, current_score + engagement_points)

    def get_score_tier(self, score: int) -> LeadScore:
        """Get the tier/category for a score."""
        if score >= 80:
            return LeadScore.HOT
        elif score >= 60:
            return LeadScore.WARM
        elif score >= 40:
            return LeadScore.COOL
        else:
            return LeadScore.COLD

    def get_priority_leads(self, leads: Dict, min_score: int = 60) -> List:
        """Get leads above a certain score threshold."""
        priority = []
        for lead_id, lead_data in leads.items():
            if lead_data.get("score", 0) >= min_score:
                priority.append({
                    "id": lead_id,
                    "name": f"{lead_data.get('first_name', '')} {lead_data.get('last_name', '')}",
                    "company": lead_data.get("company", ""),
                    "score": lead_data.get("score", 0),
                    "tier": self.get_score_tier(lead_data.get("score", 0)).value
                })

        return sorted(priority, key=lambda x: x["score"], reverse=True)

    def explain_score(self, lead) -> Dict:
        """Provide breakdown of how a score was calculated."""
        breakdown = {
            "title_score": {
                "value": self._score_title(lead.title),
                "max": 30,
                "reason": f"Based on title: {lead.title}"
            },
            "company_score": {
                "value": self._score_company(lead.company),
                "max": 20,
                "reason": f"Based on company: {lead.company}"
            },
            "source_score": {
                "value": self._score_source(lead.source),
                "max": 20,
                "reason": f"Based on source: {lead.source}"
            },
            "linkedin_score": {
                "value": self._score_linkedin(lead.linkedin_url),
                "max": 15,
                "reason": "LinkedIn profile provided" if lead.linkedin_url else "No LinkedIn URL"
            },
            "total": {
                "value": self.calculate_score(lead),
                "max": 100,
                "tier": self.get_score_tier(self.calculate_score(lead)).value
            }
        }
        return breakdown


# Audience-specific scoring adjustments
class AudienceScoringModifier:
    """
    Additional scoring modifiers based on audience type.
    Helps prioritize leads that match ideal customer profile.
    """

    MODIFIERS = {
        "b2b_founder": {
            "bonus": 5,
            "priority_services": ["linkedin_presence", "customer_voice_research"]
        },
        "b2c_founder": {
            "bonus": 5,
            "priority_services": ["customer_voice_research", "linkedin_presence"]
        },
        "vc_investor": {
            "bonus": 8,  # Higher bonus - potential for portfolio referrals
            "priority_services": ["linkedin_presence"]
        },
        "consultant_coach": {
            "bonus": 3,
            "priority_services": ["linkedin_presence"]
        }
    }

    @classmethod
    def apply_modifier(cls, base_score: int, audience_type: str, service: str) -> int:
        """Apply audience-specific modifiers to base score."""
        modifier = cls.MODIFIERS.get(audience_type, {"bonus": 0, "priority_services": []})

        adjusted_score = base_score + modifier["bonus"]

        # Extra bonus if interested in their priority service
        if service in modifier["priority_services"]:
            adjusted_score += 3

        return min(100, adjusted_score)


# Test the scoring
if __name__ == "__main__":
    from dataclasses import dataclass
    from typing import Optional

    @dataclass
    class TestLead:
        title: str
        company: str
        source: str
        linkedin_url: Optional[str]

    scorer = LeadScorer()

    test_leads = [
        TestLead("CEO & Founder", "TechStartup Inc", "linkedin_landing_page", "https://linkedin.com/in/test"),
        TestLead("Marketing Manager", "Big Corp", "cold_list", None),
        TestLead("Partner", "Ventures Capital", "referral", "https://linkedin.com/in/partner"),
        TestLead("Consultant", "Self-employed", "linkedin_organic", "https://linkedin.com/in/consultant"),
    ]

    print("=== Lead Scoring Test ===\n")

    for lead in test_leads:
        score = scorer.calculate_score(lead)
        tier = scorer.get_score_tier(score)

        print(f"Lead: {lead.title} at {lead.company}")
        print(f"Source: {lead.source}")
        print(f"Score: {score}/100 ({tier.value.upper()})")

        breakdown = scorer.explain_score(lead)
        print("Breakdown:")
        for key, val in breakdown.items():
            if key != "total":
                print(f"  - {key}: {val['value']}/{val['max']}")
        print()
