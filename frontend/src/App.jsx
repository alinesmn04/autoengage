import { useState, useEffect, useRef } from 'react';
import { 
  Menu,
  Plus, 
  Send, 
  Settings, 
  X,
  MessageSquare, 
  Terminal,
  ChevronDown,
  ChevronUp,
  BarChart3,
  Users,
  Radio,
  FileText,
  Trash2,
  Play,
  Pause,
  Mail,
  Zap,
  Globe,
  Cpu,
  BookOpen,
  CheckCircle,
  AlertTriangle
} from 'lucide-react';
import './App.css';

const API_BASE = 'http://127.0.0.1:8000';

export default function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [apiOnline, setApiOnline] = useState(false);
  
  // Brand Profile State
  const [brand, setBrand] = useState({
    name: "TechFlow",
    niche: "AI automation for small businesses",
    tone: "Professional but friendly",
    target_audience: "Small business owners, freelancers, and entrepreneurs",
    unique_value: "We make AI simple and practical for everyday business tasks",
    forbidden_phrases: ["buy now", "limited time", "guaranteed"],
    cta_default: "Comment GUIDE for our free automation guide",
    website: "https://techflow.example.com"
  });

  // Data logs loaded from API
  const [leads, setLeads] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [voiceSamples, setVoiceSamples] = useState([]);
  const [campaigns, setCampaigns] = useState([]);
  const [selectedCampId, setSelectedCampId] = useState(null);

  // Dashboard Statistics
  const [dashboardStats, setDashboardStats] = useState({
    total_leads: 0,
    active_campaigns: 0,
    total_dms_sent: 0,
    posts_scanned: 0,
    comments_posted: 0,
    platforms_breakdown: {},
    recent_logs: [],
    engagement_rate: 0
  });

  // Chat Sessions state
  const [chats, setChats] = useState([
    {
      id: 'new-chat',
      title: 'שיחה חדשה',
      messages: [
        { role: 'agent', content: '🤖 שלום! אני AutoEngage — סוכן השיווק האוטונומי שלך. כיצד אוכל לעזור לקדם את העסק שלך היום? תוכל להתייעץ איתי, לנתח פוסטים ויראליים או לבנות מובילי לידים!' }
      ]
    }
  ]);
  const [activeChatId, setActiveChatId] = useState('new-chat');
  const [currentMessage, setCurrentMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [openToolsIndex, setOpenToolsIndex] = useState({});
  const chatBottomRef = useRef(null);

  // Campaign Wizard State
  const [isCreatingCamp, setIsCreatingCamp] = useState(false);
  const [newCampName, setNewCampName] = useState('');
  const [newCampPlatform, setNewCampPlatform] = useState('Reddit');
  const [newCampQuery, setNewCampQuery] = useState('');
  const [newCampSubreddit, setNewCampSubreddit] = useState('solopreneur');
  const [triggeringCampId, setTriggeringCampId] = useState(null);

  // Lead DM Outreach State
  const [selectedLeadForDm, setSelectedLeadForDm] = useState(null);
  const [draftedDmText, setDraftedDmText] = useState('');
  const [draftingDmLoading, setDraftingDmLoading] = useState(false);

  // Settings Voice Store state
  const [activeSettingsTab, setActiveSettingsTab] = useState('Brand');
  const [newVoiceText, setNewVoiceText] = useState('I believe that most people overcomplicate AI. You do not need to build complex neural networks. All you need is a simple webhook, an OpenAI API call, and a structured database.');
  const [newVoiceCategory, setNewVoiceCategory] = useState('Educational');
  const [voiceSearchQuery, setVoiceSearchQuery] = useState('simple automation');
  const [voiceSearchCategory, setVoiceSearchCategory] = useState('Educational');
  const [voiceSearchResults, setVoiceSearchResults] = useState([]);

  // Lead PDF outlines state
  const [pdfTopic, setPdfTopic] = useState('Email Marketing Automation');
  const [pdfAudience, setPdfAudience] = useState('E-commerce store owners');
  const [pdfGenerating, setPdfGenerating] = useState(false);
  const [generatedPdfResult, setGeneratedPdfResult] = useState(null);

  async function fetchBrand() {
    try {
      const res = await fetch(`${API_BASE}/api/brand`);
      if (res.ok) {
        const data = await res.json();
        setBrand(data);
      }
    } catch (error) {
      console.error(error);
    }
  }

  async function fetchLeads() {
    try {
      const res = await fetch(`${API_BASE}/api/leads`);
      if (res.ok) {
        const data = await res.json();
        setLeads(data);
      }
    } catch (error) {
      console.error(error);
    }
  }

  async function fetchConversations() {
    try {
      const res = await fetch(`${API_BASE}/api/conversations`);
      if (res.ok) {
        const data = await res.json();
        setConversations(data);
      }
    } catch (error) {
      console.error(error);
    }
  }

  async function fetchVoiceSamples() {
    try {
      const res = await fetch(`${API_BASE}/api/voice-samples`);
      if (res.ok) {
        const data = await res.json();
        setVoiceSamples(data);
      }
    } catch (error) {
      console.error(error);
    }
  }

  async function fetchCampaigns() {
    try {
      const res = await fetch(`${API_BASE}/api/campaigns`);
      if (res.ok) {
        const data = await res.json();
        setCampaigns(data);
        if (data.length > 0 && !selectedCampId) {
          setSelectedCampId(data[0].id);
        }
      }
    } catch (error) {
      console.error(error);
    }
  }

  async function fetchDashboardStats() {
    try {
      const res = await fetch(`${API_BASE}/api/dashboard/stats`);
      if (res.ok) {
        const data = await res.json();
        setDashboardStats(data);
      }
    } catch (error) {
      console.error(error);
    }
  }

  async function checkHealth() {
    try {
      const res = await fetch(`${API_BASE}/api/health`);
      if (res.ok) {
        setApiOnline(true);
        fetchBrand();
        fetchLeads();
        fetchConversations();
        fetchVoiceSamples();
        fetchCampaigns();
        fetchDashboardStats();
      } else {
        setApiOnline(false);
      }
    } catch {
      setApiOnline(false);
    }
  }

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 8000);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (activeTab === 'chat') {
      chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chats, activeTab, loading]);

  // Create new chat
  const handleNewChat = () => {
    const newId = `chat-${Date.now()}`;
    const newSession = {
      id: newId,
      title: 'שיחה חדשה',
      messages: [
        { role: 'agent', content: '🤖 שלום! אני AutoEngage — סוכן השיווק האוטונומי שלך. כיצד אוכל לעזור לקדם את העסק שלך היום? תוכל להתייעץ איתי, לנתח פוסטים ויראליים או לבנות מובילי לידים!' }
      ]
    };
    setChats(prev => [newSession, ...prev]);
    setActiveChatId(newId);
    setActiveTab('chat');
  };

  // Submit chat message
  const handleSendMessage = async (textToSend) => {
    const userMsg = typeof textToSend === 'string' ? textToSend : currentMessage;
    if (!userMsg.trim()) return;

    const chatIndex = chats.findIndex(c => c.id === activeChatId);
    if (chatIndex === -1) return;

    const updatedChats = [...chats];
    const targetChat = { ...updatedChats[chatIndex] };
    
    if (targetChat.title === 'שיחה חדשה' || targetChat.title === '💬 שיחה חדשה') {
      targetChat.title = `💬 ${userMsg.substring(0, 24)}${userMsg.length > 24 ? '...' : ''}`;
    }

    targetChat.messages = [...targetChat.messages, { role: 'user', content: userMsg }];
    updatedChats[chatIndex] = targetChat;
    setChats(updatedChats);
    setCurrentMessage('');
    setLoading(true);

    if (!apiOnline) {
      setTimeout(() => {
        let reply = "שרת ה-API כרגע במצב סימולציה מקומית. הפעל את server.py בשרת על מנת לחבר את סוכן ה-AI שלך!";
        targetChat.messages = [...targetChat.messages, { role: 'agent', content: reply }];
        updatedChats[chatIndex] = targetChat;
        setChats([...updatedChats]);
        setLoading(false);
      }, 1000);
      return;
    }

    try {
      const history = targetChat.messages.slice(1, -1).map(m => ({
        role: m.role === 'user' ? 'user' : 'agent',
        content: m.content
      }));

      const res = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg, history })
      });

      if (res.ok) {
        const data = await res.json();
        targetChat.messages = [...targetChat.messages, { 
          role: 'agent', 
          content: data.response,
          toolCalls: data.tool_calls || []
        }];
        updatedChats[chatIndex] = targetChat;
        setChats([...updatedChats]);
        
        fetchLeads();
        fetchConversations();
        fetchDashboardStats();
      } else {
        throw new Error();
      }
    } catch {
      targetChat.messages = [...targetChat.messages, { 
        role: 'agent', 
        content: 'שגיאה בתקשורת עם השרת או שמפתח ה-Gemini שסיפקת אינו תקין. אנא וודא שהגדרת GEMINI_API_KEY תקין בשרת.' 
      }];
      updatedChats[chatIndex] = targetChat;
      setChats([...updatedChats]);
    } finally {
      setLoading(false);
    }
  };

  const toggleToolLogs = (index) => {
    setOpenToolsIndex(prev => ({ ...prev, [index]: !prev[index] }));
  };

  // Campaigns CRUD Handlers
  const handleCreateCampaign = async (e) => {
    e.preventDefault();
    if (!newCampName.trim() || !newCampQuery.trim()) return;

    try {
      const res = await fetch(`${API_BASE}/api/campaigns`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newCampName,
          platform: newCampPlatform,
          query: newCampQuery,
          subreddit: newCampPlatform === 'Reddit' ? newCampSubreddit : ''
        })
      });
      if (res.ok) {
        const data = await res.json();
        setNewCampName('');
        setNewCampQuery('');
        setIsCreatingCamp(false);
        alert('הקמפיין נוצר בהצלחה!');
        fetchCampaigns();
        fetchDashboardStats();
        if (data.campaign) {
          setSelectedCampId(data.campaign.id);
        }
      }
    } catch (error) {
      alert('שגיאה ביצירת הקמפיין.');
    }
  };

  const handleToggleCampaign = async (id) => {
    try {
      const res = await fetch(`${API_BASE}/api/campaigns/${id}/toggle`, {
        method: 'POST'
      });
      if (res.ok) {
        fetchCampaigns();
        fetchDashboardStats();
      }
    } catch (error) {
      console.error(error);
    }
  };

  const handleDeleteCampaign = async (id) => {
    if (!confirm('האם אתה בטוח שברצונך למחוק קמפיין זה?')) return;
    try {
      const res = await fetch(`${API_BASE}/api/campaigns/${id}`, {
        method: 'DELETE'
      });
      if (res.ok) {
        fetchCampaigns();
        fetchDashboardStats();
        if (selectedCampId === id) {
          setSelectedCampId(null);
        }
      }
    } catch (error) {
      console.error(error);
    }
  };

  const handleTriggerCampaign = async (id) => {
    setTriggeringCampId(id);
    try {
      const res = await fetch(`${API_BASE}/api/campaigns/${id}/trigger`, {
        method: 'POST'
      });
      if (res.ok) {
        await fetchCampaigns();
        await fetchDashboardStats();
        alert('סבב שיווק אוטונומי הושלם בהצלחה! הלוגים התעדכנו בפיד.');
      } else {
        alert('שגיאה במהלך ריצת הקמפיין. וודא שמפתח ה-API תקין.');
      }
    } catch (error) {
      console.error(error);
    } finally {
      setTriggeringCampId(null);
    }
  };

  // Lead Management & DM Handlers
  const handleDraftDmForLead = async (lead) => {
    setSelectedLeadForDm(lead);
    setDraftingDmLoading(true);
    setDraftedDmText('');
    try {
      const res = await fetch(`${API_BASE}/api/tools/draft-dm`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          lead_name: lead.username,
          context: lead.interest || 'He commented on our post.',
          brand_tone: brand.tone
        })
      });
      if (res.ok) {
        const data = await res.json();
        setDraftedDmText(data.result);
      }
    } catch (error) {
      setDraftedDmText("שגיאה בניסוח ההודעה האוטומטית.");
    } finally {
      setDraftingDmLoading(false);
    }
  };

  const handleSendDm = async () => {
    if (!selectedLeadForDm || !draftedDmText.trim()) return;
    try {
      const res = await fetch(`${API_BASE}/api/tools/track-conversation`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          lead_name: selectedLeadForDm.username,
          message: draftedDmText,
          status: 'Sent'
        })
      });
      if (res.ok) {
        alert(`הודעת ה-DM נשלחה ותועדה בהצלחה ל-@${selectedLeadForDm.username}!`);
        setSelectedLeadForDm(null);
        setDraftedDmText('');
        fetchConversations();
        fetchDashboardStats();
      }
    } catch (error) {
      alert('שגיאה ברישום השיחה.');
    }
  };

  // Brand Update
  const handleUpdateBrand = (e) => {
    if (e) e.preventDefault();
    fetch(`${API_BASE}/api/brand`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(brand)
    })
    .then(res => {
      if (res.ok) return res.json();
      throw new Error();
    })
    .then(data => {
      setBrand(data.brand);
      alert("פרופיל המותג עודכן ונשמר בהצלחה בדיסק!");
    })
    .catch(() => {
      alert("שגיאה בעדכון פרופיל המותג.");
    });
  };

  // Voice Store Handlers
  const handleAddVoice = (e) => {
    if (e) e.preventDefault();
    fetch(`${API_BASE}/api/tools/voice-sample`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: newVoiceText, category: newVoiceCategory })
    })
    .then(res => {
      if (res.ok) return res.json();
      throw new Error();
    })
    .then(data => {
      setVoiceSamples(data.samples);
      setNewVoiceText('');
      alert("סגנון הכתיבה התווסף בהצלחה למאגר!");
    })
    .catch(() => {
      alert("שגיאה בהוספת דגימה.");
    });
  };

  const handleSearchVoice = () => {
    fetch(`${API_BASE}/api/tools/find-similar-voice`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: voiceSearchQuery, category: voiceSearchCategory })
    })
    .then(res => {
      if (res.ok) return res.json();
      throw new Error();
    })
    .then(data => {
      setVoiceSearchResults(data.result);
    })
    .catch(() => {
      alert("שגיאה בחיפוש.");
    });
  };

  // Generate Premium PDF Lead Magnet
  const handleGeneratePdf = async (e) => {
    e.preventDefault();
    setPdfGenerating(true);
    setGeneratedPdfResult(null);
    try {
      // Step 1: Create outline using AI
      const outlineRes = await fetch(`${API_BASE}/api/tools/lead-magnet-outline`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic: pdfTopic,
          target_audience: pdfAudience
        })
      });
      
      if (!outlineRes.ok) throw new Error("Failed generating outline");
      const outlineData = await outlineRes.json();
      const outline = outlineData.result;

      // Step 2: Build PDF using FPDF
      const pdfRes = await fetch(`${API_BASE}/api/tools/lead-magnet-pdf`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: outline.title,
          chapters: outline.chapters,
          filename: `${pdfTopic.toLowerCase().replace(/[^a-z0-9]/g, '_')}_guide.pdf`
        })
      });

      if (!pdfRes.ok) throw new Error("Failed building PDF");
      const pdfData = await pdfRes.json();
      
      setGeneratedPdfResult({
        title: outline.title,
        downloadUrl: `${API_BASE}${pdfData.download_url}`,
        filename: pdfData.filename
      });
    } catch (error) {
      alert(`שגיאה בייצור מדריך ה-PDF: ${error.message}`);
    } finally {
      setPdfGenerating(false);
    }
  };

  const activeChat = chats.find(c => c.id === activeChatId) || chats[0];
  const selectedCampaign = campaigns.find(c => c.id === selectedCampId);

  return (
    <div className="app-container" dir="rtl">
      {/* API Status toast */}
      <div className={`api-toast ${apiOnline ? 'online' : 'offline'}`}>
        <span className="dot"></span>
        {apiOnline ? 'חיבור שרת פעיל (Live)' : 'סימולציה מקומית (API מנותק)'}
      </div>

      {/* Sidebar Navigation */}
      <div className={`sidebar ${isSidebarOpen ? '' : 'collapsed'}`}>
        <div className="sidebar-header">
          <div className="sidebar-logo-group">
            <div className="sidebar-logo">AE</div>
            <div className="sidebar-title">AutoEngage</div>
          </div>
        </div>

        {/* Primary Tabs */}
        <div className="sidebar-category-header">תפריט ראשי</div>
        <ul className="sidebar-menu" style={{ flex: 'none' }}>
          <li>
            <button 
              className={`sidebar-item-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
              onClick={() => setActiveTab('dashboard')}
            >
              <BarChart3 size={16} />
              <span>לוח בקרה (Stats)</span>
            </button>
          </li>
          <li>
            <button 
              className={`sidebar-item-btn ${activeTab === 'chat' ? 'active' : ''}`}
              onClick={() => setActiveTab('chat')}
            >
              <MessageSquare size={16} />
              <span>צ'אט סוכן (AI Chat)</span>
            </button>
          </li>
          <li>
            <button 
              className={`sidebar-item-btn ${activeTab === 'campaigns' ? 'active' : ''}`}
              onClick={() => setActiveTab('campaigns')}
            >
              <Radio size={16} />
              <span>קמפיינים (Autopilot)</span>
            </button>
          </li>
          <li>
            <button 
              className={`sidebar-item-btn ${activeTab === 'leads' ? 'active' : ''}`}
              onClick={() => setActiveTab('leads')}
            >
              <Users size={16} />
              <span>מרכז לידים (Leads)</span>
            </button>
          </li>
          <li>
            <button 
              className={`sidebar-item-btn ${activeTab === 'pdf-studio' ? 'active' : ''}`}
              onClick={() => setActiveTab('pdf-studio')}
            >
              <BookOpen size={16} />
              <span>PDF Studio (Lead Magnets)</span>
            </button>
          </li>
          <li>
            <button 
              className={`sidebar-item-btn ${activeTab === 'settings' ? 'active' : ''}`}
              onClick={() => setActiveTab('settings')}
            >
              <Settings size={16} />
              <span>הגדרות סגנון ומותג</span>
            </button>
          </li>
        </ul>

        {/* Contextual chat panel list in sidebar when in Chat Tab */}
        {activeTab === 'chat' && (
          <>
            <div className="sidebar-category-header">שיחות פתוחות</div>
            <button className="new-chat-btn" onClick={handleNewChat}>
              <Plus size={18} /> שיחה חדשה
            </button>
            <ul className="sidebar-menu">
              {chats.map(c => (
                <li key={c.id}>
                  <button 
                    className={`sidebar-item-btn ${activeChatId === c.id ? 'active' : ''}`}
                    onClick={() => setActiveChatId(c.id)}
                  >
                    <MessageSquare size={14} style={{ flexShrink: 0 }} />
                    <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{c.title}</span>
                  </button>
                </li>
              ))}
            </ul>
          </>
        )}

        <div className="sidebar-footer">
          <div className="system-identity">
            <Cpu size={14} style={{ color: 'var(--primary)' }} />
            <span>סוכן גרסה 2.0 (מצב מפלצת)</span>
          </div>
        </div>
      </div>

      {/* Main Content Workspace */}
      <div className="main-content">
        <div className="workspace-header">
          <button className="hamburger-btn" onClick={() => setIsSidebarOpen(!isSidebarOpen)}>
            <Menu size={22} />
          </button>

          <div className="workspace-title">
            {activeTab === 'dashboard' && <h2>לוח בקרה שיווקי (Marketing Dashboard)</h2>}
            {activeTab === 'chat' && <h2>שיחה עם סוכן ה-AI (Agent Console)</h2>}
            {activeTab === 'campaigns' && <h2>קמפיינים אוטומטיים (Autopilot campaigns)</h2>}
            {activeTab === 'leads' && <h2>מרכז לידים והודעות outreach (Leads Hub)</h2>}
            {activeTab === 'pdf-studio' && <h2>סטודיו מובילי לידים (Premium Lead Magnets)</h2>}
            {activeTab === 'settings' && <h2>הגדרות מותג וקולות (Brand & Voice profile)</h2>}
            <p>מערכת ניהול שיווק והאזנה לרשתות חברתיות מונעת AI באופן מלא בדיסק.</p>
          </div>
        </div>

        <div className="workspace-body">
          
          {/* VIEW 1: DASHBOARD VIEW */}
          {activeTab === 'dashboard' && (
            <div className="dashboard-container">
              {/* Metrics cards row */}
              <div className="stats-grid">
                <div className="stat-card">
                  <div className="stat-icon purple"><Users size={20} /></div>
                  <div className="stat-content">
                    <span className="stat-label">סה"כ לידים</span>
                    <span className="stat-value">{dashboardStats.total_leads}</span>
                  </div>
                </div>

                <div className="stat-card">
                  <div className="stat-icon teal"><Radio size={20} /></div>
                  <div className="stat-content">
                    <span className="stat-label">קמפיינים פעילים</span>
                    <span className="stat-value">{dashboardStats.active_campaigns}</span>
                  </div>
                </div>

                <div className="stat-card">
                  <div className="stat-icon blue"><Mail size={20} /></div>
                  <div className="stat-content">
                    <span className="stat-label">הודעות DM שנרשמו</span>
                    <span className="stat-value">{dashboardStats.total_dms_sent}</span>
                  </div>
                </div>

                <div className="stat-card">
                  <div className="stat-icon orange"><Globe size={20} /></div>
                  <div className="stat-content">
                    <span className="stat-label">פוסטים שנסרקו</span>
                    <span className="stat-value">{dashboardStats.posts_scanned}</span>
                  </div>
                </div>

                <div className="stat-card">
                  <div className="stat-icon green"><CheckCircle size={20} /></div>
                  <div className="stat-content">
                    <span className="stat-label">תגובות שפורסמו</span>
                    <span className="stat-value">{dashboardStats.comments_posted}</span>
                  </div>
                </div>
              </div>

              {/* Graphic Row */}
              <div className="dashboard-charts-row">
                <div className="dashboard-chart-card">
                  <h3>פילוח לידים לפי ערוץ פרסום</h3>
                  <div className="chart-wrapper circle-charts">
                    <div className="circular-progress-group">
                      <div className="circle-container">
                        <svg className="circle-svg" viewBox="0 0 36 36">
                          <path className="circle-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                          <path className="circle-fill reddit" strokeDasharray={`${Math.min(100, Math.max(0, (dashboardStats.platforms_breakdown.Reddit || 0) / (dashboardStats.total_leads || 1) * 100))}, 100`} d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                        </svg>
                        <div className="circle-percentage">
                          {Math.round((dashboardStats.platforms_breakdown.Reddit || 0) / (dashboardStats.total_leads || 1) * 100)}%
                        </div>
                      </div>
                      <span className="circle-label">Reddit Engagement</span>
                    </div>

                    <div className="circular-progress-group">
                      <div className="circle-container">
                        <svg className="circle-svg" viewBox="0 0 36 36">
                          <path className="circle-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                          <path className="circle-fill linkedin" strokeDasharray={`${Math.min(100, Math.max(0, (dashboardStats.platforms_breakdown.LinkedIn || 0) / (dashboardStats.total_leads || 1) * 100))}, 100`} d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                        </svg>
                        <div className="circle-percentage">
                          {Math.round((dashboardStats.platforms_breakdown.LinkedIn || 0) / (dashboardStats.total_leads || 1) * 100)}%
                        </div>
                      </div>
                      <span className="circle-label">LinkedIn Engagement</span>
                    </div>
                  </div>
                  <div className="chart-legend">
                    <span className="legend-item"><span className="legend-dot reddit"></span>Reddit: {dashboardStats.platforms_breakdown.Reddit || 0} לידים</span>
                    <span className="legend-item"><span className="legend-dot linkedin"></span>LinkedIn: {dashboardStats.platforms_breakdown.LinkedIn || 0} לידים</span>
                  </div>
                </div>

                <div className="dashboard-chart-card">
                  <h3>קצב מעורבות שבועי (Weekly Growth)</h3>
                  <div className="chart-wrapper bar-charts">
                    {/* Simulated visual bar chart */}
                    <div className="bar-group">
                      <div className="bar-track"><div className="bar-fill" style={{ height: '35%' }}></div></div>
                      <span className="bar-label">שבוע 1</span>
                    </div>
                    <div className="bar-group">
                      <div className="bar-track"><div className="bar-fill" style={{ height: '52%' }}></div></div>
                      <span className="bar-label">שבוע 2</span>
                    </div>
                    <div className="bar-group">
                      <div className="bar-track"><div className="bar-fill" style={{ height: '45%' }}></div></div>
                      <span className="bar-label">שבוע 3</span>
                    </div>
                    <div className="bar-group">
                      <div className="bar-track"><div className="bar-fill" style={{ height: '68%' }}></div></div>
                      <span className="bar-label">שבוע 4</span>
                    </div>
                    <div className="bar-group">
                      <div className="bar-track"><div className="bar-fill" style={{ height: `${dashboardStats.engagement_rate}%` }}></div></div>
                      <span className="bar-label">נוכחי</span>
                    </div>
                  </div>
                  <p className="bar-caption">אחוז לידים חמים ושיחות מעורבות מתוך סך הלידים: <strong>{dashboardStats.engagement_rate}%</strong></p>
                </div>
              </div>

              {/* Feed of recent campaign activities */}
              <div className="recent-activity-card">
                <h3>פיד פעילות חי מקמפיינים (Live Campaign Activity Feed)</h3>
                <div className="activity-feed-list">
                  {dashboardStats.recent_logs.length === 0 ? (
                    <div className="no-activity">טרם הופעלו קמפיינים אוטומטיים במערכת. לחץ על 'קמפיינים' בתפריט הצדדי על מנת להתחיל!</div>
                  ) : (
                    dashboardStats.recent_logs.map((item, idx) => (
                      <div key={idx} className="activity-feed-item">
                        <span className="activity-tag">{item.campaign}</span>
                        <span className="activity-text">{item.log}</span>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          )}

          {/* VIEW 2: AI AGENT CHAT VIEW */}
          {activeTab === 'chat' && (
            <div className="chat-workspace" style={{ height: '100%' }}>
              <div className="chat-panel">
                {activeChat.messages.length === 1 && !loading ? (
                  <div className="welcome-container">
                    <div className="welcome-logo-glow">AE</div>
                    <h1 className="welcome-title">כיצד אוכל לעזור לך היום?</h1>
                    <p className="welcome-subtitle">הנחה את סוכן השיווק האוטונומי AutoEngage לכתוב תוכן, לנתח מתחרים או לייצר מדריכי מובילי לידים (Lead Magnets) מבוססי AI בזמן אמת.</p>
                    
                    <div className="welcome-grid">
                      <div className="welcome-card" onClick={() => handleSendMessage("נסח לי פוסט מקצועי ללינקדאין המציג מקרה בוחן (Case Study) של עסק שחסך 20 שעות בשבוע באמצעות מעבר לאוטומציה של CRM")}>
                        <div className="welcome-card-header">🚀 פוסט לינקדאין ויראלי</div>
                        <div className="welcome-card-body">נסח פוסט מבוסס מקרה בוחן (Case Study) על חיסכון של 20 שעות שבועיות.</div>
                      </div>

                      <div className="welcome-card" onClick={() => handleSendMessage("בצע מחקר מודעות וסגנונות פרסום על המתחרה Zapier, ותציג לי את 3 דפוסי השיווק המובילים שלהם")}>
                        <div className="welcome-card-header">🔍 חקירת מודעות מתחרים</div>
                        <div className="welcome-card-body">סרוק והפק דפוסי כתיבה וקריאייטיב מהמתחרה הגדולה ביותר שלך.</div>
                      </div>

                      <div className="welcome-card" onClick={() => handleSendMessage("תעזור לי לתכנן את הפרקים ומבנה התוכן עבור מדריך PDF שיווקי (Lead Magnet) בנושא אוטומציית אימיילים לבעלי סוכנויות")}>
                        <div className="welcome-card-header">📘 מתווה מדריך PDF שיווקי</div>
                        <div className="welcome-card-body">בנה פרקים ותקצירים מלאים עבור ספרון מוביל לידים להורדה.</div>
                      </div>

                      <div className="welcome-card" onClick={() => handleSendMessage("נסח לי תגובה מקצועית ואותנטית לפוסט שמדבר על קשיים בניהול לקוחות ידני, ותשלב קריאה לפעולה אלגנטית (CTA) לקבלת מדריך האוטומציה שלי")}>
                        <div className="welcome-card-header">💬 ניסוח תגובת ערך (QA Approved)</div>
                        <div className="welcome-card-body">נסח תגובה איכותית המשלבת קריאה עדינה לפעולה להגברת מעורבות.</div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="chat-messages">
                    {activeChat.messages.map((msg, idx) => (
                      <div key={idx} className={`message ${msg.role === 'user' ? 'user' : 'agent'}`}>
                        <div className="chat-avatar">
                          {msg.role === 'user' ? '👤' : '🤖'}
                        </div>
                        <div className="message-bubble-wrapper">
                          <div className="message-bubble">
                            {msg.content}
                          </div>

                          {/* Tool execution logs */}
                          {msg.toolCalls && msg.toolCalls.length > 0 && (
                            <div className="tool-call-accordion">
                              <div className="tool-call-header" onClick={() => toggleToolLogs(idx)}>
                                <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                  <Terminal size={12} style={{ marginLeft: '6px' }} />
                                  {openToolsIndex[idx] ? 'הסתר פעולות כלי AI פנימיים' : '🔧 כלי AI פעל ברקע (לחץ להרחבה)'}
                                </span>
                                {openToolsIndex[idx] ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                              </div>
                              {openToolsIndex[idx] && (
                                <div className="tool-call-body">
                                  {msg.toolCalls.join('\n\n')}
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                    
                    {loading && (
                      <div className="message agent">
                        <div className="chat-avatar">🤖</div>
                        <div className="message-bubble-wrapper">
                          <div className="message-bubble" style={{ background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-color)' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                              <div className="typing-indicator" style={{ marginLeft: '10px' }}>
                                <span className="typing-dot"></span>
                                <span className="typing-dot"></span>
                                <span className="typing-dot"></span>
                              </div>
                              <span>הסוכן מעבד כעת את הכלים ומגבש תשובה...</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                    <div ref={chatBottomRef}></div>
                  </div>
                )}

                {/* Input bar */}
                <div className="chat-input-area">
                  <form className="chat-input-pill-wrapper" onSubmit={(e) => { e.preventDefault(); handleSendMessage(); }}>
                    <input 
                      type="text" 
                      placeholder="הקלד כאן הודעה להנחיית סוכן ה-AI (למשל: נסח פוסט, חקור מתחרים, סרוק רדיט...)" 
                      value={currentMessage}
                      onChange={(e) => setCurrentMessage(e.target.value)}
                    />
                    <button className="send-pill-btn" type="submit" disabled={loading || !currentMessage.trim()}>
                      <Send size={18} style={{ transform: 'rotate(135deg) translate(-2px, 2px)' }} />
                    </button>
                  </form>
                </div>
              </div>
            </div>
          )}

          {/* VIEW 3: CAMPAIGNS HUB VIEW */}
          {activeTab === 'campaigns' && (
            <div className="campaigns-workspace">
              
              {/* Campaign list & controls on the left */}
              <div className="campaigns-list-panel">
                <div className="panel-header">
                  <h3>הקמפיינים שלי</h3>
                  <button className="btn btn-sm" onClick={() => setIsCreatingCamp(true)}>
                    <Plus size={16} /> קמפיין חדש
                  </button>
                </div>

                <div className="campaigns-grid-items">
                  {campaigns.length === 0 ? (
                    <div className="no-campaigns-msg">לא נמצאו קמפיינים במערכת. צור קמפיין חדש כדי להתחיל.</div>
                  ) : (
                    campaigns.map(c => (
                      <div 
                        key={c.id} 
                        className={`campaign-list-card ${selectedCampId === c.id ? 'selected' : ''}`}
                        onClick={() => setSelectedCampId(c.id)}
                      >
                        <div className="camp-card-meta">
                          <span className={`badge ${c.platform === 'Reddit' ? 'reddit' : 'linkedin'}`}>
                            {c.platform}
                          </span>
                          <span className={`badge-status ${c.status === 'Active' ? 'active' : 'paused'}`}>
                            {c.status === 'Active' ? 'פעיל' : 'מושהה'}
                          </span>
                        </div>
                        <h4>{c.name}</h4>
                        <p className="query-desc">שאילתה: <strong>{c.query}</strong></p>
                        <div className="camp-card-stats">
                          <span>🔍 Scanned: {c.posts_scanned}</span>
                          <span>💬 Comments: {c.comments_posted}</span>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* Campaign details & run panel on the right */}
              <div className="campaign-detail-panel">
                {selectedCampaign ? (
                  <div className="campaign-detail-content">
                    <div className="campaign-detail-header">
                      <div>
                        <h2>{selectedCampaign.name}</h2>
                        <span className="camp-meta-text">פלטפורמה: <strong>{selectedCampaign.platform}</strong> | מילת מפתח: <strong>{selectedCampaign.query}</strong></span>
                      </div>
                      
                      <div className="campaign-actions">
                        <button 
                          className="btn btn-outline" 
                          onClick={() => handleToggleCampaign(selectedCampaign.id)}
                        >
                          {selectedCampaign.status === 'Active' ? <Pause size={16} /> : <Play size={16} />}
                          <span>{selectedCampaign.status === 'Active' ? 'השהה קמפיין' : 'הפעל קמפיין'}</span>
                        </button>
                        
                        <button 
                          className="btn"
                          disabled={triggeringCampId === selectedCampaign.id}
                          onClick={() => handleTriggerCampaign(selectedCampaign.id)}
                        >
                          {triggeringCampId === selectedCampaign.id ? (
                            <div className="loader-spinner"></div>
                          ) : (
                            <Zap size={16} />
                          )}
                          <span>{triggeringCampId === selectedCampaign.id ? 'מריץ סבב AI...' : 'הרץ סבב קמפיין כעת'}</span>
                        </button>

                        <button 
                          className="btn-danger-icon"
                          onClick={() => handleDeleteCampaign(selectedCampaign.id)}
                          title="מחק קמפיין"
                        >
                          <Trash2 size={18} />
                        </button>
                      </div>
                    </div>

                    {/* Campaign status metrics grid */}
                    <div className="campaign-detail-stats">
                      <div className="metric-box">
                        <span className="label">פוסטים שנסרקו</span>
                        <span className="value">{selectedCampaign.posts_scanned}</span>
                      </div>
                      <div className="metric-box">
                        <span className="label">תגובות ערך שפורסמו</span>
                        <span className="value">{selectedCampaign.comments_posted}</span>
                      </div>
                      <div className="metric-box">
                        <span className="label">לידים שנלכדו בקמפיין</span>
                        <span className="value">{selectedCampaign.leads_captured}</span>
                      </div>
                    </div>

                    {/* Campaign Live Terminal Logs */}
                    <div className="campaign-terminal-logs">
                      <div className="terminal-header">
                        <Terminal size={14} style={{ marginLeft: '6px' }} />
                        <span>יומן ריצה חי של סוכן ה-AI (Campaign Automation Terminal)</span>
                      </div>
                      <div className="terminal-body">
                        {selectedCampaign.logs && selectedCampaign.logs.length > 0 ? (
                          selectedCampaign.logs.map((log, lIdx) => (
                            <div key={lIdx} className="terminal-line">{log}</div>
                          ))
                        ) : (
                          <div className="terminal-line muted">אין תיעוד ריצה עבור קמפיין זה. לחץ על 'הרץ סבב קמפיין כעת' כדי להתחיל סריקה.</div>
                        )}
                      </div>
                    </div>

                  </div>
                ) : (
                  <div className="no-campaign-selected">
                    <Radio size={48} className="pulse-icon" />
                    <h3>אנא בחר קמפיין מרשימת הקמפיינים או צור קמפיין חדש כדי לראות פרטים.</h3>
                  </div>
                )}
              </div>

              {/* Create Campaign Modal Backdrop & Form */}
              {isCreatingCamp && (
                <div className="modal-backdrop">
                  <div className="modal-content-card">
                    <div className="modal-header">
                      <h3>יצירת קמפיין האזנה ושיווק אוטונומי</h3>
                      <button className="close-btn" onClick={() => setIsCreatingCamp(false)}><X size={20} /></button>
                    </div>
                    <form onSubmit={handleCreateCampaign}>
                      <div className="form-group">
                        <label>שם הקמפיין</label>
                        <input 
                          type="text" 
                          required 
                          placeholder="למשל: אוטומציה CRM ברדיט"
                          value={newCampName} 
                          onChange={(e) => setNewCampName(e.target.value)} 
                        />
                      </div>

                      <div className="form-row">
                        <div className="form-group">
                          <label>פלטפורמת שיווק</label>
                          <select 
                            value={newCampPlatform} 
                            onChange={(e) => setNewCampPlatform(e.target.value)}
                          >
                            <option value="Reddit">Reddit</option>
                            <option value="LinkedIn">LinkedIn</option>
                          </select>
                        </div>

                        {newCampPlatform === 'Reddit' && (
                          <div className="form-group">
                            <label>סאב-רדיט (Subreddit)</label>
                            <input 
                              type="text" 
                              required 
                              placeholder="solopreneur / saas / sales"
                              value={newCampSubreddit} 
                              onChange={(e) => setNewCampSubreddit(e.target.value)} 
                            />
                          </div>
                        )}
                      </div>

                      <div className="form-group">
                        <label>שאילתה לחיפוש (מילות מפתח ממוקדות)</label>
                        <input 
                          type="text" 
                          required 
                          placeholder="למשל: make CRM bottleneck or automate CRM"
                          value={newCampQuery} 
                          onChange={(e) => setNewCampQuery(e.target.value)} 
                        />
                      </div>

                      <div className="modal-footer-actions">
                        <button type="button" className="btn btn-secondary" onClick={() => setIsCreatingCamp(false)}>ביטול</button>
                        <button type="submit" className="btn">צור קמפיין והתחל</button>
                      </div>
                    </form>
                  </div>
                </div>
              )}

            </div>
          )}

          {/* VIEW 4: LEAD HUB VIEW */}
          {activeTab === 'leads' && (
            <div className="leads-workspace">
              
              <div className="leads-panel">
                <div className="panel-header">
                  <h3>מאגר לידים חמים (Captured Leads)</h3>
                  <p>לידים אלו זוהו אוטומטית על ידי סוכן ה-AI כבעלי רלוונטיות ועניין בהצעת הערך של המותג שלך.</p>
                </div>

                <div className="data-table-wrapper">
                  <table>
                    <thead>
                      <tr>
                        <th>שם משתמש</th>
                        <th>פלטפורמה</th>
                        <th>רמת עניין (Lead Score)</th>
                        <th>נושא / מדריך מבוקש</th>
                        <th>פנייה ישירה (Outreach)</th>
                      </tr>
                    </thead>
                    <tbody>
                      {leads.length === 0 ? (
                        <tr>
                          <td colSpan="5" style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '24px' }}>טרם נלכדו לידים במערכת. הרץ קמפיינים אוטומטיים על מנת לצוד לידים!</td>
                        </tr>
                      ) : (
                        leads.map((l, i) => {
                          // Calculate lead heat score based on interest/mocking
                          let score = 30; // cold
                          if (l.interest && (l.interest.toLowerCase().includes("guide") || l.interest.toLowerCase().includes("pdf") || l.interest.includes("מדריך"))) {
                            score = 85; // hot
                          } else if (l.interest) {
                            score = 55; // warm
                          }
                          
                          return (
                            <tr key={i}>
                              <td style={{ fontWeight: '600' }}>@{l.username}</td>
                              <td>
                                <span className={`badge ${l.platform === 'Reddit' ? 'reddit' : 'linkedin'}`}>
                                  {l.platform}
                                </span>
                              </td>
                              <td>
                                <span className={`badge ${score >= 80 ? 'success' : score >= 50 ? 'warning' : 'danger'}`}>
                                  {score >= 80 ? `🔥 Hot (${score})` : score >= 50 ? `⚡ Warm (${score})` : `❄️ Cold (${score})`}
                                </span>
                              </td>
                              <td style={{ color: 'var(--text-muted)' }}>{l.interest}</td>
                              <td>
                                <button className="btn btn-sm btn-outline" onClick={() => handleDraftDmForLead(l)}>
                                  <Mail size={14} style={{ marginLeft: '4px' }} /> נסח DM ב-AI
                                </button>
                              </td>
                            </tr>
                          );
                        })
                      )}
                    </tbody>
                  </table>
                </div>

                {/* Conversation outreach registry log */}
                <div className="panel-header" style={{ marginTop: '30px' }}>
                  <h3>יומן פניות והודעות שנשלחו (Outreach Conversations Log)</h3>
                </div>

                <div className="data-table-wrapper">
                  <table>
                    <thead>
                      <tr>
                        <th>לקוח יעד</th>
                        <th>תוכן הודעת הפנייה (Outreach Text)</th>
                        <th>סטטוס רישום</th>
                      </tr>
                    </thead>
                    <tbody>
                      {conversations.length === 0 ? (
                        <tr>
                          <td colSpan="3" style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '20px' }}>טרם תועדו הודעות outreach במאגר.</td>
                        </tr>
                      ) : (
                        conversations.map((c, i) => (
                          <tr key={i}>
                            <td style={{ fontWeight: '600' }}>@{c.lead_name}</td>
                            <td style={{ fontSize: '0.82rem', color: 'var(--text-muted)', maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{c.message}</td>
                            <td><span className="badge success">{c.status}</span></td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>

              </div>

              {/* Outreach DM drafting overlay modal */}
              {selectedLeadForDm && (
                <div className="modal-backdrop">
                  <div className="modal-content-card" style={{ maxWidth: '650px' }}>
                    <div className="modal-header">
                      <h3>ניסוח פנייה מותאמת אישית ל-@{selectedLeadForDm.username}</h3>
                      <button className="close-btn" onClick={() => setSelectedLeadForDm(null)}><X size={20} /></button>
                    </div>
                    <div>
                      {draftingDmLoading ? (
                        <div className="dm-drafting-loader">
                          <div className="loader-spinner"></div>
                          <span>סוכן ה-AI מנתח את הפרופיל והאינטראקציה ומנסח פנייה מותאמת אישית...</span>
                        </div>
                      ) : (
                        <div>
                          <div className="form-group">
                            <label>הצעת הודעה (הסוכן השתמש בקול המותג שלך):</label>
                            <textarea 
                              value={draftedDmText} 
                              onChange={(e) => setDraftedDmText(e.target.value)}
                              rows="6"
                            />
                          </div>

                          <div className="modal-footer-actions">
                            <button className="btn btn-secondary" onClick={() => handleDraftDmForLead(selectedLeadForDm)}>
                              <Zap size={14} style={{ marginLeft: '4px' }} /> נסח מחדש
                            </button>
                            <button className="btn" onClick={handleSendDm}>
                              <Send size={14} style={{ marginLeft: '4px', transform: 'rotate(180deg)' }} /> שלח ותעד פנייה
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

            </div>
          )}

          {/* VIEW 5: PDF STUDIO */}
          {activeTab === 'pdf-studio' && (
            <div className="pdf-studio-container">
              <div className="pdf-studio-workspace">
                <div className="pdf-form-section">
                  <h3>מנוע ייצור מדריכי שיווק (Lead Magnet Studio)</h3>
                  <p>סוכן ה-AI יבנה פרקים מלאים, ינסח תוכן ערך איכותי ולאחר מכן ייצר קובץ PDF מעוצב ברמת פרימיום עם שוליים, לוגו ועמוד שער מותאם אישית.</p>
                  
                  <form onSubmit={handleGeneratePdf}>
                    <div className="form-group">
                      <label>נושא המדריך השיווקי (Topic)</label>
                      <input 
                        type="text" 
                        required 
                        value={pdfTopic} 
                        onChange={(e) => setPdfTopic(e.target.value)} 
                        placeholder="למשל: Email Marketing CRM Automation"
                      />
                    </div>

                    <div className="form-group">
                      <label>קהל יעד (Target Audience)</label>
                      <input 
                        type="text" 
                        required 
                        value={pdfAudience} 
                        onChange={(e) => setPdfAudience(e.target.value)} 
                        placeholder="למשל: owners of marketing agencies"
                      />
                    </div>

                    <button className="btn" type="submit" disabled={pdfGenerating}>
                      {pdfGenerating ? (
                        <div className="loader-spinner"></div>
                      ) : (
                        <BookOpen size={16} />
                      )}
                      <span>{pdfGenerating ? 'הסוכן מייצר מתווה וכותב את ה-PDF...' : 'צור מדריך PDF מבוסס AI כעת'}</span>
                    </button>
                  </form>
                </div>

                <div className="pdf-result-section">
                  <h3>המדריך השיווקי האחרון שיוצר</h3>
                  {pdfGenerating ? (
                    <div className="pdf-status-card loading">
                      <div className="pulse-circle"></div>
                      <h4>סוכן ה-AI בתהליך כתיבה...</h4>
                      <p>הסוכן בונה מתווה של 5 פרקים, מפרט כל נושא ובונה קובץ PDF סופר-מעוצב עם שער וקריאה לפעולה (CTA).</p>
                    </div>
                  ) : generatedPdfResult ? (
                    <div className="pdf-status-card success">
                      <div className="success-icon"><CheckCircle size={36} /></div>
                      <h4>{generatedPdfResult.title}</h4>
                      <p>קובץ ה-PDF נוצר ונשמר בהצלחה בדיסק השרת: <strong>{generatedPdfResult.filename}</strong></p>
                      
                      <div className="pdf-download-action">
                        <a 
                          href={generatedPdfResult.downloadUrl} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="btn"
                        >
                          <FileText size={16} />
                          <span>הורד / פתח קובץ PDF</span>
                        </a>
                      </div>
                    </div>
                  ) : (
                    <div className="pdf-status-card empty">
                      <FileText size={48} />
                      <h4>לא נוצר מדריך PDF עדיין</h4>
                      <p>הזן נושא וקהל יעד משמאל ולחץ על יצירה. המערכת תבצע מחקר ותספק קובץ להורדה מיידית.</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* VIEW 6: SETTINGS VIEW */}
          {activeTab === 'settings' && (
            <div className="settings-container">
              <div className="settings-tabs-header">
                <button 
                  className={`settings-tab-btn ${activeSettingsTab === 'Brand' ? 'active' : ''}`}
                  onClick={() => setActiveSettingsTab('Brand')}
                >
                  פרופיל מותג וחברה
                </button>
                <button 
                  className={`settings-tab-btn ${activeSettingsTab === 'Voice' ? 'active' : ''}`}
                  onClick={() => setActiveSettingsTab('Voice')}
                >
                  מאגר קולות כתיבה (Voice Store)
                </button>
              </div>

              <div className="settings-tab-body">
                {activeSettingsTab === 'Brand' && (
                  <form onSubmit={handleUpdateBrand}>
                    <div className="form-row">
                      <div className="form-group">
                        <label>שם העסק / המותג</label>
                        <input type="text" value={brand.name} onChange={(e) => setBrand({ ...brand, name: e.target.value })} />
                      </div>
                      <div className="form-group">
                        <label>כתובת אתר האינטרנט</label>
                        <input type="text" value={brand.website} onChange={(e) => setBrand({ ...brand, website: e.target.value })} />
                      </div>
                    </div>

                    <div className="form-group">
                      <label>נישה עסקית של החברה (Company Niche)</label>
                      <input type="text" value={brand.niche} onChange={(e) => setBrand({ ...brand, niche: e.target.value })} />
                    </div>

                    <div className="form-group">
                      <label>קהל יעד עיקרי</label>
                      <input type="text" value={brand.target_audience} onChange={(e) => setBrand({ ...brand, target_audience: e.target.value })} />
                    </div>

                    <div className="form-group">
                      <label>הצעת ערך ייחודית (USP)</label>
                      <textarea value={brand.unique_value} onChange={(e) => setBrand({ ...brand, unique_value: e.target.value })} />
                    </div>

                    <div className="form-group">
                      <label>קריאה לפעולה מובנית (CTA Default)</label>
                      <input type="text" value={brand.cta_default} onChange={(e) => setBrand({ ...brand, cta_default: e.target.value })} />
                    </div>

                    <div className="form-group">
                      <label>מילות איסור (מחיקה/הוספה באמצעות פסיק)</label>
                      <input 
                        type="text" 
                        value={brand.forbidden_phrases ? brand.forbidden_phrases.join(', ') : ''} 
                        onChange={(e) => setBrand({ ...brand, forbidden_phrases: e.target.value.split(',').map(s => s.trim()) })}
                      />
                    </div>

                    <button className="btn" type="submit">שמור סנכרן פרופיל מותג בדיסק</button>
                  </form>
                )}

                {activeSettingsTab === 'Voice' && (
                  <div>
                    <form onSubmit={handleAddVoice} style={{ background: 'rgba(255,255,255,0.01)', border: '1px solid var(--border-color)', borderRadius: '10px', padding: '16px', marginBottom: '24px' }}>
                      <h4 style={{ color: '#fff', marginBottom: '10px', fontSize: '0.95rem' }}>הוסף דוגמת כתיבה ללימוד הבוט</h4>
                      <div className="form-group">
                        <label>טקסט דוגמה (פוסט שכתבת, תגובה אותנטית וכו')</label>
                        <textarea 
                          required 
                          value={newVoiceText} 
                          onChange={(e) => setNewVoiceText(e.target.value)} 
                          placeholder="הקלד או הדבק כאן דגימת סגנון כתיבה אישי..."
                        />
                      </div>
                      <div className="form-group">
                        <label>קטגוריית סגנון</label>
                        <select value={newVoiceCategory} onChange={(e) => setNewVoiceCategory(e.target.value)}>
                          <option value="Educational">Educational</option>
                          <option value="Casual">Casual</option>
                          <option value="Technical">Technical</option>
                          <option value="Storytelling">Storytelling</option>
                        </select>
                      </div>
                      <button className="btn btn-secondary" type="submit" style={{ width: '100%' }}>הוסף דגימת סגנון למאגר</button>
                    </form>

                    <div>
                      <h4 style={{ color: '#fff', marginBottom: '10px', fontSize: '0.95rem' }}>חיפוש דגימות סגנון דומות</h4>
                      <div className="form-row">
                        <div className="form-group">
                          <label>ביטוי לחיפוש</label>
                          <input type="text" value={voiceSearchQuery} onChange={(e) => setVoiceSearchQuery(e.target.value)} />
                        </div>
                        <div className="form-group">
                          <label>קטגוריה</label>
                          <select value={voiceSearchCategory} onChange={(e) => setVoiceSearchCategory(e.target.value)}>
                            <option value="Educational">Educational</option>
                            <option value="Casual">Casual</option>
                            <option value="Technical">Technical</option>
                            <option value="Storytelling">Storytelling</option>
                          </select>
                        </div>
                      </div>
                      <button className="btn btn-outline" type="button" onClick={handleSearchVoice} style={{ width: '100%' }}>חפש דגימות סגנון דומות</button>

                      {voiceSearchResults.length > 0 && (
                        <div className="samples-grid">
                          {voiceSearchResults.map((samp, idx) => (
                            <div key={idx} className="sample-card">
                              <div className="sample-card-header">📂 קטגוריה: {samp.category}</div>
                              <div className="sample-card-body">"{samp.text}"</div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}
