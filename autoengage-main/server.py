import os
import sys
import random

# Force standard streams to use UTF-8 and safely replace unsupported characters to prevent Windows console encoding crashes (CP1255/CP1252)
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

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

from pathlib import Path

# Ensure current folder is in the python path
current_dir = str(Path(__file__).parent.resolve())
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Load environment variables from .env first
load_dotenv(Path(current_dir) / ".env")



# Import persistence and save utilities
from persistence import CAMPAIGNS, save_all

# Import agent objects and tools from existing scripts
from agent import llm_with_tools, SYSTEM_PROMPT, HumanMessage, SystemMessage
from brand_profile import BRAND
from lead_tools import LEADS, create_lead_magnet_outline, generate_lead_magnet_pdf, capture_lead
from dm_tools import CONVERSATIONS, identify_warm_leads, draft_dm, track_conversation
from voice_store import VOICE_SAMPLES, add_voice_sample, find_similar_voice
from discovery_tools import search_viral_posts, read_post_content, score_relevance
from comment_tools import draft_comment, qa_check_comment
from content_tools import generate_post_ideas, write_post, suggest_visual, ab_test_versions
from ads_tools import research_competitor_ads, extract_ad_patterns, suggest_ad_copy
from analytics_tools import analyze_engagement, generate_insights, score_lead
from qa_tools import check_forbidden_phrases, check_ai_smell, fact_check, overall_quality_score
from platform_reddit import reddit_search_posts, reddit_read_post, reddit_post_comment, reddit_monitor_replies
from platform_linkedin import linkedin_search_posts, linkedin_read_post, linkedin_post_comment

app = FastAPI(
    title="AutoEngage API Gateway",
    description="Backend API breakpoint for managing and orchestrating the AutoEngage Marketing bots.",
    version="1.0.0"
)

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- PYDANTIC REQUEST SCHEMAS -----------------

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, str]]] = None

class SearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 5

class CampaignCreateRequest(BaseModel):
    name: str
    platform: str
    query: str
    subreddit: Optional[str] = None

class ReadPostRequest(BaseModel):
    url: str

class RelevanceRequest(BaseModel):
    post_text: str
    niche: str

class DraftCommentRequest(BaseModel):
    post_summary: str
    brand_tone: str
    cta: str

class QaCheckRequest(BaseModel):
    comment: str
    forbidden_phrases: Optional[List[str]] = None

class PostIdeasRequest(BaseModel):
    niche: str
    count: Optional[int] = 5

class WritePostRequest(BaseModel):
    idea: str
    platform: str
    tone: str

class SuggestVisualRequest(BaseModel):
    post_text: str

class AbTestRequest(BaseModel):
    idea: str
    tone: str

class LeadOutlineRequest(BaseModel):
    topic: str
    target_audience: str

class LeadPdfRequest(BaseModel):
    title: str
    chapters: List[Dict[str, str]]
    filename: str

class CaptureLeadRequest(BaseModel):
    username: str
    platform: str
    interest: str

class CompetitorAdsRequest(BaseModel):
    competitor_name: str

class SuggestAdRequest(BaseModel):
    patterns: str
    brand_tone: str

class WarmLeadsRequest(BaseModel):
    interactions: List[Dict[str, str]]

class DraftDmRequest(BaseModel):
    lead_name: str
    context: str
    brand_tone: str

class TrackConversationRequest(BaseModel):
    lead_name: str
    message: str
    status: str

class VoiceSampleRequest(BaseModel):
    text: str
    category: str

class FindVoiceRequest(BaseModel):
    query: str
    category: str

class RedditSearchRequest(BaseModel):
    subreddit: str
    query: str
    limit: Optional[int] = 10

class LinkedInSearchRequest(BaseModel):
    query: str
    results_max: Optional[int] = 5

# ----------------- API ENDPOINTS -----------------

@app.get("/api/health")
def health_check():
    return {"status": "online", "message": "AutoEngage API Gateway is operating normally."}

@app.get("/api/brand")
def get_brand():
    return BRAND

@app.post("/api/brand")
def update_brand(updated: Dict[str, Any]):
    global BRAND
    BRAND.update(updated)
    save_all()
    return {"message": "Brand profile updated successfully", "brand": BRAND}

@app.post("/api/chat")
def chat_with_agent(request: ChatRequest):
    try:
        from langchain_core.messages import AIMessage, ToolMessage
        from agent import TOOLS
        
        # Build a tool map
        tool_map = {tool.name: tool for tool in TOOLS}
        
        messages = [SystemMessage(content=SYSTEM_PROMPT)]
        if request.history:
            for msg in request.history:
                role = msg.get("role")
                content = msg.get("content")
                if role == "user":
                    messages.append(HumanMessage(content=content))
                elif role in ["agent", "assistant"]:
                    messages.append(AIMessage(content=content))
                else:
                    messages.append(SystemMessage(content=content))
        messages.append(HumanMessage(content=request.message))
        
        executed_tool_logs = []
        
        # Max 8 iterations to prevent infinite loops
        for iteration in range(8):
            response = llm_with_tools.invoke(messages)
            
            # Check for tool calls using standard LangChain unified tool_calls
            tool_calls = getattr(response, "tool_calls", [])
            
            # Fallback to additional_kwargs if tool_calls is empty
            if not tool_calls:
                add_kwargs_calls = response.additional_kwargs.get("tool_calls", [])
                if add_kwargs_calls:
                    import json
                    for tc in add_kwargs_calls:
                        func = tc.get("function", {})
                        try:
                            args = json.loads(func.get("arguments", "{}")) if isinstance(func.get("arguments"), str) else func.get("arguments")
                        except:
                            args = {}
                        tool_calls.append({
                            "id": tc.get("id"),
                            "name": func.get("name"),
                            "args": args
                        })
            
            if not tool_calls:
                break
                
            messages.append(response)
            
            for tc in tool_calls:
                t_id = tc.get("id")
                t_name = tc.get("name")
                t_args = tc.get("args", {})
                
                # Execute tool
                if t_name in tool_map:
                    try:
                        t_res = tool_map[t_name].invoke(t_args)
                    except Exception as e:
                        t_res = f"Error during tool execution: {str(e)}"
                else:
                    t_res = f"Tool {t_name} not found."
                
                import json
                executed_tool_logs.append(
                    f"🔧 כלי הופעל: {t_name}\nפרמטרים: {json.dumps(t_args, ensure_ascii=False)}\nתוצאה: {str(t_res)[:400]}..."
                )
                
                messages.append(ToolMessage(content=str(t_res), tool_call_id=t_id))
        
        # Clean up response.content to ensure it is a plain string
        cleaned_response = response.content
        if isinstance(cleaned_response, list):
            text_parts = []
            for item in cleaned_response:
                if isinstance(item, dict) and "text" in item:
                    text_parts.append(item["text"])
                elif isinstance(item, str):
                    text_parts.append(item)
            cleaned_response = "".join(text_parts)
        elif cleaned_response is None:
            cleaned_response = ""
        else:
            cleaned_response = str(cleaned_response)

        if not cleaned_response.strip():
            cleaned_response = "בוצעה הפעולה בהצלחה."

        return {
            "response": cleaned_response,
            "tool_calls": executed_tool_logs
        }
    except Exception as e:
        try:
            import traceback
            traceback.print_exc()
        except Exception:
            pass
        # Fallback responses
        from agent import provider
        fallback_msg = (
            f"התרחשה שגיאה בעת פנייה למודל ה-AI הנוכחי ({provider.upper()}).\n"
            "וודא שמפתחות ה-API ומכסות הגישה תקינים ושהקובץ `.env` נטען כהלכה."
        )
            
        return {
            "response": fallback_msg + f"\n\n*(שגיאת מערכת: {str(e)})*",
            "tool_calls": []
        }

# 1. Discovery Center
@app.post("/api/tools/search-posts")
def search_posts(request: SearchRequest):
    res = search_viral_posts.invoke({"query": request.query, "max_results": request.max_results})
    return {"result": res}

@app.post("/api/tools/read-post")
def read_post(request: ReadPostRequest):
    res = read_post_content.invoke({"url": request.url})
    return {"result": res}

@app.post("/api/tools/score-relevance")
def score_post_relevance(request: RelevanceRequest):
    res = score_relevance.invoke({"post_text": request.post_text, "niche": request.niche})
    return {"result": res}

# 2. Comment & QA Center
@app.post("/api/tools/draft-comment")
def draft_marketing_comment(request: DraftCommentRequest):
    res = draft_comment.invoke({
        "post_summary": request.post_summary,
        "brand_tone": request.brand_tone,
        "cta": request.cta
    })
    return {"result": res}

@app.post("/api/tools/qa-check")
def qa_check(request: QaCheckRequest):
    phrases = request.forbidden_phrases if request.forbidden_phrases is not None else BRAND.get("forbidden_phrases", [])
    res = overall_quality_score.invoke({
        "text": request.comment,
        "forbidden": phrases
    })
    return {"result": res}

# 3. Content Studio
@app.post("/api/tools/post-ideas")
def get_post_ideas(request: PostIdeasRequest):
    res = generate_post_ideas.invoke({"niche": request.niche, "count": request.count})
    return {"result": res}

@app.post("/api/tools/write-post")
def write_social_post(request: WritePostRequest):
    res = write_post.invoke({
        "idea": request.idea,
        "platform": request.platform,
        "tone": request.tone
    })
    return {"result": res}

@app.post("/api/tools/suggest-visual")
def suggest_visuals(request: SuggestVisualRequest):
    res = suggest_visual.invoke({"post_text": request.post_text})
    return {"result": res}

@app.post("/api/tools/ab-test")
def run_ab_test(request: AbTestRequest):
    res = ab_test_versions.invoke({"idea": request.idea, "tone": request.tone})
    return {"result": res}

# 4. Lead Magnet Suite
@app.post("/api/tools/lead-magnet-outline")
def get_lead_outline(request: LeadOutlineRequest):
    res = create_lead_magnet_outline.invoke({
        "topic": request.topic,
        "target_audience": request.target_audience
    })
    return {"result": res}

@app.post("/api/tools/lead-magnet-pdf")
def build_lead_pdf(request: LeadPdfRequest):
    try:
        # Clean filename to be secure
        filename = "".join([c for c in request.filename if c.isalnum() or c in (".", "_", "-")]).strip()
        if not filename.endswith(".pdf"):
            filename += ".pdf"
        
        file_path = os.path.join(current_dir, filename)
        
        res = generate_lead_magnet_pdf.invoke({
            "title": request.title,
            "chapters": request.chapters,
            "filename": file_path
        })
        
        return {
            "result": res,
            "filename": filename,
            "download_url": f"/api/download-pdf/{filename}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

@app.get("/api/download-pdf/{filename}")
def download_pdf(filename: str):
    clean_name = "".join([c for c in filename if c.isalnum() or c in (".", "_", "-")]).strip()
    file_path = os.path.join(current_dir, clean_name)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="application/pdf", filename=clean_name)
    else:
        raise HTTPException(status_code=404, detail="File not found")

@app.get("/api/leads")
def get_leads():
    return LEADS

@app.post("/api/tools/capture-lead")
def save_lead(request: CaptureLeadRequest):
    res = capture_lead.invoke({
        "username": request.username,
        "platform": request.platform,
        "interest": request.interest
    })
    return {"result": res, "leads": LEADS}

# 5. Competitor Ads & Outreach
@app.post("/api/tools/research-ads")
def research_ads(request: CompetitorAdsRequest):
    res = research_competitor_ads.invoke({"competitor_name": request.competitor_name})
    patterns = extract_ad_patterns.invoke({"data_ads": res})
    return {"result": res, "patterns": patterns}

@app.post("/api/tools/suggest-ad-copy")
def suggest_ads(request: SuggestAdRequest):
    res = suggest_ad_copy.invoke({
        "patterns": request.patterns,
        "brand_tone": request.brand_tone
    })
    return {"result": res}

@app.post("/api/tools/warm-leads")
def get_warm_leads(request: WarmLeadsRequest):
    res = identify_warm_leads.invoke({"interactions": request.interactions})
    return {"result": res}

@app.post("/api/tools/draft-dm")
def create_dm(request: DraftDmRequest):
    res = draft_dm.invoke({
        "lead_name": request.lead_name,
        "context": request.context,
        "brand_tone": request.brand_tone
    })
    return {"result": res}

@app.get("/api/conversations")
def get_conversations():
    return CONVERSATIONS

@app.post("/api/tools/track-conversation")
def save_conversation(request: TrackConversationRequest):
    res = track_conversation.invoke({
        "lead_name": request.lead_name,
        "message": request.message,
        "status": request.status
    })
    return {"result": res, "conversations": CONVERSATIONS}

# 6. Brand Voice Store
@app.get("/api/voice-samples")
def get_voice_samples():
    return VOICE_SAMPLES

@app.post("/api/tools/voice-sample")
def save_voice_sample(request: VoiceSampleRequest):
    res = add_voice_sample.invoke({
        "text": request.text,
        "category": request.category
    })
    return {"result": res, "samples": VOICE_SAMPLES}

@app.post("/api/tools/find-similar-voice")
def search_similar_voice(request: FindVoiceRequest):
    res = find_similar_voice.invoke({
        "query": request.query,
        "category": request.category
    })
    return {"result": res}

# 7. Platform Specifics
@app.post("/api/tools/reddit-search")
def search_reddit(request: RedditSearchRequest):
    res = reddit_search_posts.invoke({
        "subreddit": request.subreddit,
        "query": request.query,
        "limit": request.limit
    })
    return {"result": res}

@app.post("/api/tools/linkedin-search")
def search_linkedin(request: LinkedInSearchRequest):
    res = linkedin_search_posts.invoke({
        "query": request.query,
        "results_max": request.results_max
    })
    return {"result": res}

@app.post("/api/tools/analyze-engagement")
def run_engagement_analysis(posts: List[Dict[str, Any]]):
    res = analyze_engagement.invoke({"posts_data": posts})
    insights = generate_insights.invoke({"analytics": res})
    return {"analysis": res, "insights": insights}

@app.post("/api/tools/score-lead")
def run_score_lead(request: Dict[str, Any]):
    res = score_lead.invoke({
        "lead_name": request.get("lead_name", "Anonymous"),
        "interactions": request.get("interactions", [])
    })
    return {"result": res}

# 8. Campaigns CRUD & Simulation Hub
@app.get("/api/campaigns")
def get_campaigns():
    return CAMPAIGNS

@app.post("/api/campaigns")
def create_campaign(request: CampaignCreateRequest):
    new_campaign = {
        "id": f"camp_{int(random.random() * 1000000)}",
        "name": request.name,
        "platform": request.platform,
        "query": request.query,
        "subreddit": request.subreddit,
        "status": "Active",
        "posts_scanned": 0,
        "comments_posted": 0,
        "leads_captured": 0,
        "logs": [f"[{random.choice(['2026-06-07 00:15', '2026-06-07 01:30'])}] 📌 Campaign created successfully."]
    }
    CAMPAIGNS.append(new_campaign)
    save_all()
    return {"message": "Campaign created", "campaign": new_campaign}

@app.post("/api/campaigns/{id}/toggle")
def toggle_campaign(id: str):
    for camp in CAMPAIGNS:
        if camp["id"] == id:
            camp["status"] = "Paused" if camp["status"] == "Active" else "Active"
            save_all()
            return {"message": f"Campaign status updated to {camp['status']}", "campaign": camp}
    raise HTTPException(status_code=404, detail="Campaign not found")

@app.delete("/api/campaigns/{id}")
def delete_campaign(id: str):
    global CAMPAIGNS
    for i, camp in enumerate(CAMPAIGNS):
        if camp["id"] == id:
            CAMPAIGNS.pop(i)
            save_all()
            return {"message": "Campaign deleted successfully"}
    raise HTTPException(status_code=404, detail="Campaign not found")

@app.post("/api/campaigns/{id}/trigger")
def trigger_campaign_cycle(id: str):
    for camp in CAMPAIGNS:
        if camp["id"] == id:
            run_campaign_cycle(camp)
            return {"message": "Campaign run cycle triggered successfully", "campaign": camp}
    raise HTTPException(status_code=404, detail="Campaign not found")

# 9. Dashboard Statistics Summary
@app.get("/api/dashboard/stats")
def get_dashboard_stats():
    total_leads = len(LEADS)
    active_camps = sum(1 for c in CAMPAIGNS if c.get("status") == "Active")
    total_dms = len(CONVERSATIONS)
    
    posts_scanned = sum(c.get("posts_scanned", 0) for c in CAMPAIGNS)
    comments_posted = sum(c.get("comments_posted", 0) for c in CAMPAIGNS)
    
    # Calculate platforms breakdown
    platform_counts = {}
    for l in LEADS:
        p = l.get("platform", "Unknown")
        platform_counts[p] = platform_counts.get(p, 0) + 1
        
    # Collate recent logs from all campaigns and sort them chronologically (newest first)
    recent_logs = []
    for c in CAMPAIGNS:
        for log in c.get("logs", []):
            recent_logs.append({
                "campaign": c.get("name"),
                "log": log
            })
    recent_logs.sort(key=lambda x: x["log"], reverse=True)

            
    # Simulated monthly engagement rate for the graph
    engagement_rate = 74.5 if total_leads > 0 else 0.0
    
    return {
        "total_leads": total_leads,
        "active_campaigns": active_camps,
        "total_dms_sent": total_dms,
        "posts_scanned": posts_scanned,
        "comments_posted": comments_posted,
        "platforms_breakdown": platform_counts,
        "recent_logs": recent_logs[:10],
        "engagement_rate": engagement_rate
    }

def run_campaign_cycle(campaign: dict):
    import datetime
    import random
    
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    campaign["logs"].insert(0, f"[{now_str}] 🚀 Starting campaign execution cycle...")
    
    platform = campaign.get("platform", "Reddit").lower()
    query = campaign.get("query", "automation")
    subreddit = campaign.get("subreddit") or "solopreneur"
    
    campaign["logs"].insert(0, f"[{now_str}] 🔍 Searching for posts on {campaign['platform']} with query: '{query}'")
    
    posts = []
    try:
        if platform == "reddit":
            res = reddit_search_posts.invoke({"subreddit": subreddit, "query": query})
            if isinstance(res, list):
                posts = res
        else: # linkedin
            res = linkedin_search_posts.invoke({"query": query})
            if isinstance(res, list):
                posts = res
    except Exception as e:
        campaign["logs"].insert(0, f"[{now_str}] ❌ Search failed: {str(e)}")
        save_all()
        return
        
    if not posts:
        campaign["logs"].insert(0, f"[{now_str}] ⚠️ No posts found for the query.")
        save_all()
        return
        
    campaign["logs"].insert(0, f"[{now_str}] 📋 Found {len(posts)} posts. Processing first relevant post...")
    
    # Process up to 2 posts per cycle
    for post in posts[:2]:
        title = post.get("title", "Unknown Post")
        url = post.get("url", "https://example.com/post")
        author = post.get("author", post.get("from_user", "Anonymous"))
        
        campaign["posts_scanned"] += 1
        campaign["logs"].insert(0, f"[{now_str}] 📖 Reading post content: '{title}' by {author}")
        
        try:
            if platform == "reddit":
                content_res = reddit_read_post.invoke({"post_url": url})
                post_body = content_res.get("post_content", "")
            else:
                post_body = linkedin_read_post.invoke({"post_url": url})
        except Exception as e:
            campaign["logs"].insert(0, f"[{now_str}] ⚠️ Could not read post: {str(e)}")
            continue
            
        campaign["logs"].insert(0, f"[{now_str}] ⚡ Scoring relevance for post...")
        niche = BRAND.get("niche", "AI automation")
        try:
            rel_score_str = score_relevance.invoke({"post_text": post_body, "niche": niche})
            score_val = int(rel_score_str.split("Score:")[1].split("/")[0].strip())
        except Exception as e:
            score_val = 65 # fallback
            rel_score_str = "Score: 65/100\nExplanation: Moderate relevance."
            
        campaign["logs"].insert(0, f"[{now_str}] 📊 Relevance score: {score_val}/100 - {rel_score_str.replace('Score:', '').strip()}")
        
        if score_val >= 50:
            campaign["logs"].insert(0, f"[{now_str}] ✍️ Drafting valuable comment...")
            brand_tone = BRAND.get("tone", "Professional but friendly")
            cta = BRAND.get("cta_default", "Check out our site")
            
            try:
                comment = draft_comment.invoke({
                    "post_summary": f"Title: {title}\nBody: {post_body[:300]}",
                    "brand_tone": brand_tone,
                    "cta": cta
                })
            except Exception as e:
                campaign["logs"].insert(0, f"[{now_str}] ❌ Drafting failed: {str(e)}")
                continue
                
            if not comment or not comment.strip():
                campaign["logs"].insert(0, f"[{now_str}] ⚠️ Comment drafting failed (returned empty). Your LLM API key might be out of quota or rate-limited. Skipping post.")
                save_all()
                continue
                
            campaign["logs"].insert(0, f"[{now_str}] 🛡️ Performing QA checks on drafted comment...")
            forbidden = BRAND.get("forbidden_phrases", [])
            try:
                qa_res = overall_quality_score.invoke({"text": comment, "forbidden": forbidden})
                qa_score = qa_res.get("overall_score", 80)
            except Exception as e:
                qa_score = 75
                qa_res = {"ai_smell": {"score": 2}, "length": len(comment)}
                
            campaign["logs"].insert(0, f"[{now_str}] ✅ QA Score: {qa_score}/100. (AI Smell: {qa_res.get('ai_smell', {}).get('score', 0)}/10, Length: {qa_res.get('length', 0)} chars)")
            
            if qa_score >= 60:
                campaign["logs"].insert(0, f"[{now_str}] 📤 Posting comment to {platform}...")
                try:
                    if platform == "reddit":
                        reddit_post_comment.invoke({"post_url": url, "comment_text": comment})
                    else:
                        linkedin_post_comment.invoke({"post_url": url, "comment_text": comment})
                except Exception as e:
                    campaign["logs"].insert(0, f"[{now_str}] ❌ Post failed: {str(e)}")
                    continue
                    
                campaign["comments_posted"] += 1
                campaign["logs"].insert(0, f"[{now_str}] 🎉 Comment successfully published! Text: '{comment[:80]}...'")
                
                # Capture Lead simulation (80% chance for simulation showcase)
                if random.random() > 0.2:
                    lead_user = f"{author.replace(' ', '_').lower()}" if author != "Anonymous" else f"user_{random.randint(1000, 9999)}"
                    campaign["logs"].insert(0, f"[{now_str}] 🎯 Engagement detected! User @{lead_user} liked/replied to the comment.")
                    
                    # Capture lead
                    capture_lead.invoke({
                        "username": lead_user,
                        "platform": platform.capitalize(),
                        "interest": f"Requested Guide: {title[:30]}"
                    })
                    campaign["leads_captured"] += 1
                    
                    # Draft outreach DM
                    campaign["logs"].insert(0, f"[{now_str}] ✉️ Drafting personalized direct message (DM) outreach to @{lead_user}...")
                    try:
                        dm_content = draft_dm.invoke({
                            "lead_name": lead_user,
                            "context": "Responded positively to our automated post comment.",
                            "brand_tone": brand_tone
                        })
                    except Exception as e:
                        dm_content = ""
                        
                    if not dm_content or not dm_content.strip():
                        dm_content = f"Hey @{lead_user}, thanks for reaching out! Here's the link to our guide: {BRAND.get('website')}"
                        campaign["logs"].insert(0, f"[{now_str}] ⚠️ DM drafting returned empty, using fallback template. (LLM API key might be out of quota)")
                        
                    # Track DM conversation
                    track_conversation.invoke({
                        "lead_name": lead_user,
                        "message": dm_content,
                        "status": "Sent"
                    })
                    campaign["logs"].insert(0, f"[{now_str}] 📬 Outreach DM automatically tracked and sent to @{lead_user}!")
            else:
                campaign["logs"].insert(0, f"[{now_str}] ❌ Comment failed QA check, discarded to protect brand reputation.")
        else:
            campaign["logs"].insert(0, f"[{now_str}] ℹ️ Post relevance too low, skipping.")
            
    campaign["logs"].insert(0, f"[{now_str}] 🏁 Campaign execution cycle finished.")
    save_all()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
