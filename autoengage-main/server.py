import os
import sys
import random
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

# Ensure current folder is in the python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Load environment variables from .env first
load_dotenv(os.path.join(current_dir, ".env"))

# Ensure GROQ_API_KEY is present to prevent langchain-groq from throwing at import time
if not os.environ.get("GROQ_API_KEY"):
    os.environ["GROQ_API_KEY"] = "gsk_simulation_key_autoengage_fallback_12345"

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
    return {"message": "Brand profile updated successfully", "brand": BRAND}

@app.post("/api/chat")
async def chat_with_agent(request: ChatRequest):
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
        
        # Max 5 iterations to prevent infinite loops
        for iteration in range(5):
            response = llm_with_tools.invoke(messages)
            
            # Check for tool calls
            tool_calls = response.additional_kwargs.get("tool_calls", [])
            if not tool_calls:
                break
                
            messages.append(response)
            
            for tc in tool_calls:
                t_id = tc.get("id")
                func = tc.get("function", {})
                t_name = func.get("name")
                
                # Parse arguments safely
                import json
                try:
                    t_args = json.loads(func.get("arguments", "{}")) if isinstance(func.get("arguments"), str) else func.get("arguments")
                except:
                    t_args = {}
                
                # Execute tool
                if t_name in tool_map:
                    try:
                        t_res = tool_map[t_name].invoke(t_args)
                    except Exception as e:
                        t_res = f"Error during tool execution: {str(e)}"
                else:
                    t_res = f"Tool {t_name} not found."
                
                executed_tool_logs.append(
                    f"🔧 כלי הופעל: {t_name}\nפרמטרים: {json.dumps(t_args, ensure_ascii=False)}\nתוצאה: {str(t_res)[:400]}..."
                )
                
                messages.append(ToolMessage(content=str(t_res), tool_call_id=t_id))
        
        return {
            "response": response.content if response.content else "בוצעה הפעולה בהצלחה.",
            "tool_calls": executed_tool_logs
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Fallback responses
        fallback_responses = [
            "שלום! נראה שמפתח ה-API של Groq לא הוגדר בצורה מלאה או שישנה שגיאת חיבור (401). וודא שמפתח ה-Groq שהזנת בקובץ ה-`.env` תקין ופעיל.",
            "היי, אני במצב הדגמה מקומי כרגע בשל שגיאת מפתח Groq. אנא וודא שמפתח ה-API תקין ושהקובץ נטען כהלכה.",
        ]
        return {
            "response": random.choice(fallback_responses) + f"\n\n*(שגיאת מערכת: {str(e)})*",
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
