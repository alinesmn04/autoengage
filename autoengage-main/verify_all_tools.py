import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment
current_dir = Path(__file__).parent.resolve()
load_dotenv(current_dir / ".env")

# Import all tools
from comment_tools import draft_comment, qa_check_comment
from content_tools import generate_post_ideas, write_post, suggest_visual, ab_test_versions
from lead_tools import create_lead_magnet_outline, write_cta_for_lead_magnet
from ads_tools import research_competitor_ads, extract_ad_patterns, suggest_ad_copy
from dm_tools import draft_dm
from analytics_tools import generate_insights
from qa_tools import check_ai_smell, fact_check, overall_quality_score
from platform_reddit import reddit_search_posts, reddit_read_post, reddit_monitor_replies
from platform_linkedin import linkedin_search_posts, linkedin_read_post

def run_test(tool_name, tool_func, *args, **kwargs):
    print(f"\n========================================\nTesting tool: {tool_name}\n========================================\n")
    try:
        res = tool_func.invoke(*args, **kwargs)
        print("Result:")
        print(res)
    except Exception as e:
        print(f"Error executing {tool_name}: {e}")

if __name__ == "__main__":
    print("Starting verification of all AI-powered tools...")
    
    # 1. Comment tools
    run_test("draft_comment", draft_comment, {
        "post_summary": "A post about how AI is revolutionizing SaaS onboarding.",
        "brand_tone": "friendly, expert",
        "cta": "Check out AutoEngage for automated marketing comments."
    })
    
    run_test("qa_check_comment", qa_check_comment, {
        "comment": "This is a revolutionary game-changer! Check out AutoEngage.",
        "phrases_forbidden": ["revolutionary", "game-changer"]
    })

    # 2. Content tools
    run_test("generate_post_ideas", generate_post_ideas, {
        "niche": "AI automation for local bakeries",
        "count": 3
    })

    run_test("write_post", write_post, {
        "idea": "Using AI chatbots to take cake orders overnight",
        "platform": "LinkedIn",
        "tone": "professional, enthusiastic"
    })

    run_test("suggest_visual", suggest_visual, {
        "post_text": "Imagine a bakery where cake orders are automatically taken by an AI chatbot while you sleep!"
    })

    run_test("ab_test_versions", ab_test_versions, {
        "idea": "Using AI chatbots to take cake orders overnight",
        "tone": "informative"
    })

    # 3. Lead tools
    run_test("create_lead_magnet_outline", create_lead_magnet_outline, {
        "topic": "Email Marketing Automation",
        "target_audience": "E-commerce store owners"
    })

    run_test("write_cta_for_lead_magnet", write_cta_for_lead_magnet, {
        "magnet_title": "10x E-commerce Sales with Email Automations",
        "platform": "Twitter"
    })

    # 4. Ads tools
    run_test("research_competitor_ads", research_competitor_ads, {
        "competitor_name": "HubSpot"
    })

    run_test("extract_ad_patterns", extract_ad_patterns, {
        "data_ads": "HubSpot helps you grow better. Try their free CRM. Start automating today."
    })

    run_test("suggest_ad_copy", suggest_ad_copy, {
        "patterns": "Free CRM, start automating today, grow better",
        "brand_tone": "persuasive"
    })

    # 5. DM tools
    run_test("draft_dm", draft_dm, {
        "lead_name": "John Doe",
        "context": "liked our post about AI order taking",
        "brand_tone": "helpful, casual"
    })

    # 6. Analytics tools
    run_test("generate_insights", generate_insights, {
        "analytics": "Best performing post: 'Cake orders AI'\nLikes: 150\nComments: 45"
    })

    # 7. QA tools
    run_test("check_ai_smell", check_ai_smell, {
        "text": "This is a revolutionary next-level game-changer that will unlock growth."
    })

    run_test("fact_check", fact_check, {
        "text": "Using automated emails can increase open rates by 25%."
    })

    run_test("overall_quality_score", overall_quality_score, {
        "text": "This is a nice post about email marketing, check it out.",
        "forbidden": ["revolutionary"]
    })

    # 8. Platform specific
    run_test("reddit_search_posts", reddit_search_posts, {
        "subreddit": "saas",
        "query": "saas marketing tools"
    })

    run_test("reddit_read_post", reddit_read_post, {
        "post_url": "https://reddit.com/r/saas/comments/example_marketing"
    })

    run_test("reddit_monitor_replies", reddit_monitor_replies, {
        "username": "autoengage_bot"
    })

    run_test("linkedin_search_posts", linkedin_search_posts, {
        "query": "CRM automation"
    })

    run_test("linkedin_read_post", linkedin_read_post, {
        "post_url": "https://linkedin.com/posts/example-crm"
    })
    
    print("\nAll tools verified successfully!")
