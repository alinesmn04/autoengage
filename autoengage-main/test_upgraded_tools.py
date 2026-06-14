import os
import sys
import json
from dotenv import load_dotenv

# Force standard streams to use UTF-8 and safely replace unsupported characters
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")
    except Exception:
        pass

# Import upgraded tools
from comment_tools import draft_comment, qa_check_comment
from content_tools import generate_post_ideas, write_post, suggest_visual, ab_test_versions
from lead_tools import create_lead_magnet_outline, write_cta_for_lead_magnet
from ads_tools import research_competitor_ads, extract_ad_patterns, suggest_ad_copy
from dm_tools import draft_dm
from analytics_tools import generate_insights
from qa_tools import check_ai_smell, fact_check
from platform_reddit import reddit_search_posts, reddit_read_post, reddit_monitor_replies
from platform_linkedin import linkedin_search_posts, linkedin_read_post

def run_tests():
    print("=================== STARTING TOOL VERIFICATION ===================")
    
    # 1. Comment tools
    print("\n--- Testing draft_comment ---")
    comm = draft_comment.invoke({"post_summary": "CRM manual updates are slow and error-prone.", "brand_tone": "friendly", "cta": "Get our free PDF guide"})
    print("Result:", comm)
    
    print("\n--- Testing qa_check_comment ---")
    qa = qa_check_comment.invoke({"comment": comm, "phrases_forbidden": ["guaranteed", "buy now"]})
    print("Result:", json.dumps(qa, indent=2))
    
    # 2. Content tools
    print("\n--- Testing generate_post_ideas ---")
    ideas = generate_post_ideas.invoke({"niche": "AI automation for law firms", "count": 3})
    print("Result:", ideas)
    
    print("\n--- Testing write_post ---")
    post = write_post.invoke({"idea": "How AI can draft legal summaries", "platform": "linkedin", "tone": "professional"})
    print("Result:", post)
    
    print("\n--- Testing suggest_visual ---")
    visuals = suggest_visual.invoke({"post_text": post})
    print("Result:", visuals)
    
    print("\n--- Testing ab_test_versions ---")
    ab = ab_test_versions.invoke({"idea": "Save 5 hours a week in CRM sync", "tone": "direct"})
    print("Result:", json.dumps(ab, indent=2))
    
    # 3. Lead tools
    print("\n--- Testing create_lead_magnet_outline ---")
    outline = create_lead_magnet_outline.invoke({"topic": "AI marketing", "target_audience": "small agencies"})
    print("Result:", json.dumps(outline, indent=2))
    
    # 4. Ads tools
    print("\n--- Testing research_competitor_ads ---")
    ads_rep = research_competitor_ads.invoke({"competitor_name": "Zapier"})
    print("Result:", ads_rep[:300] + "...")
    
    # 5. DM tools
    print("\n--- Testing draft_dm ---")
    dm = draft_dm.invoke({"lead_name": "John", "context": "liked our comment on LinkedIn", "brand_tone": "casual"})
    print("Result:", dm)
    
    # 6. Analytics tools
    print("\n--- Testing generate_insights ---")
    insights = generate_insights.invoke({"analytics": "Best performing post: 'No-Code tutorial'. Likes: 120, Comments: 35."})
    print("Result:", json.dumps(insights, indent=2))
    
    # 7. QA tools
    print("\n--- Testing check_ai_smell ---")
    smell = check_ai_smell.invoke({"text": "This is a revolutionary game-changer next level cutting-edge tool!"})
    print("Result:", json.dumps(smell, indent=2))
    
    # 8. Platform tools
    print("\n--- Testing reddit_search_posts ---")
    r_posts = reddit_search_posts.invoke({"subreddit": "solopreneur", "query": "make.com integrations"})
    print("Result:", json.dumps(r_posts, indent=2))
    
    print("\n--- Testing linkedin_search_posts ---")
    l_posts = linkedin_search_posts.invoke({"query": "AI automation"})
    print("Result:", json.dumps(l_posts, indent=2))
    
    print("\n=================== VERIFICATION COMPLETE ===================")

if __name__ == "__main__":
    run_tests()
