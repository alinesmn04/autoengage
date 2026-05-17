import React, { useState, useEffect, useRef } from 'react';
import { 
  Menu,
  Plus, 
  Send, 
  Settings, 
  X,
  MessageSquare, 
  Compass, 
  PenTool, 
  ClipboardCheck, 
  FileText, 
  Target, 
  UserCheck,
  Sparkles,
  Terminal,
  ChevronDown,
  ChevronUp,
  HelpCircle,
  FileDown
} from 'lucide-react';
import './App.css';

const API_BASE = 'http://127.0.0.1:8000';

export default function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [activeSettingsTab, setActiveSettingsTab] = useState('Brand');
  const [apiOnline, setApiOnline] = useState(false);
  const [checkingApi, setCheckingApi] = useState(true);
  
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

  // Sidebar Chats Lists State
  const [chats, setChats] = useState([
    {
      id: 'new-chat',
      title: 'שיחה חדשה',
      messages: [
        { role: 'agent', content: '🤖 שלום! אני AutoEngage — סוכן השיווק האוטונומי שלך. כיצד אוכל לעזור לקדם את העסק שלך היום? תוכל להתייעץ איתי, לנתח פוסטים ויראליים או לבנות מובילי לידים!' }
      ]
    },
    {
      id: 'chat-1',
      title: '💬 שירותי אוטומציה עסקית',
      messages: [
        { role: 'user', content: 'מהו פרופיל המותג שלי וכיצד נוכל לשווק אוטומציות?' },
        { role: 'agent', content: 'פרופיל המותג שלך הוא TechFlow, הנישה היא אוטומציית AI לעסקים קטנים. הדרך הטובה ביותר לשווק היא להעניק ערך קודם: לסרוק פוסטים ברשת, להציע תגובות בעלות ערך גבוה, ולמשוך לידים באמצעות מדריכי PDF איכותיים.' }
      ]
    },
    {
      id: 'chat-2',
      title: '💬 סריקת פוסטים ברדיט',
      messages: [
        { role: 'user', content: 'סרוק לי פוסטים ברדיט בנושא אוטומציה' },
        { role: 'agent', content: 'ביצעתי סריקה ב-r/solopreneur. מצאתי פוסטים המדברים על קשיים בניהול לקוחות ידני ב-CRM. הצעתי תגובה המדגישה חיסכון בזמן ושילוב CTA להורדת המדריך השיווקי שלך.', toolCalls: ['🔧 כלי הופעל: reddit_search_posts\nתוצאה: מצאתי 3 פוסטים רלוונטיים בנושא Make.com ו-CRM.'] }
      ]
    },
    {
      id: 'chat-3',
      title: '💬 מחקר מודעות מתחרה: Zapier',
      messages: [
        { role: 'user', content: 'חקור את מודעות המתחרה Zapier' },
        { role: 'agent', content: 'ניתחתי את סגנונות הפרסום של Zapier. הם מתמקדים בחיסכון בזמן, פשטות קוד (No-Code), ותבניות מוכנות מראש. הנה מתווה מודעה מומלץ עבורך המבוסס על דפוסים אלו:\n\n"נמאס לך להעתיק לידים ידנית? TechFlow בונה עבורך אוטומציות CRM חכמות ב-15 דקות ללא שורת קוד אחת. קבל את מדריך האוטומציה החינמי שלנו!"', toolCalls: ['🔧 כלי הופעל: research_competitor_ads\nתוצאה: מפרסמים מודעות ויזואליות פשוטות המדגישות No-Code.'] }
      ]
    },
    {
      id: 'dm-1',
      title: '✉️ פנייה ל-Sarah Connor',
      messages: [
        { role: 'user', content: 'נסח לי הודעת DM לשרה קונור שכתבה שהיא צריכה אוטומציה' },
        { role: 'agent', content: 'הנה טיוטת הודעה מותאמת אישית לשרה קונור:\n\n"היי שרה, שמתי לב שהגבת על הפוסט שלנו בנושא אוטומציית Make.com ושאת מחפשת פתרון לצוואר הבקבוק בעסק. נשמח לשתף איתך את מדריך האוטומציה המלא שלנו בחינם 😊"', toolCalls: ['🔧 כלי הופעל: draft_dm\nתוצאה: הודעה אישית מנוסחת היטב'] }
      ]
    }
  ]);

  const [activeChatId, setActiveChatId] = useState('new-chat');
  const [currentMessage, setCurrentMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [openToolsIndex, setOpenToolsIndex] = useState({}); // toggle accordion per message
  const chatBottomRef = useRef(null);

  // Settings Drawer Inputs
  const [newVoiceText, setNewVoiceText] = useState('I believe that most people overcomplicate AI. You do not need to build complex neural networks. All you need is a simple webhook, an OpenAI API call, and a structured database.');
  const [newVoiceCategory, setNewVoiceCategory] = useState('Educational');
  const [voiceSearchQuery, setVoiceSearchQuery] = useState('simple automation');
  const [voiceSearchCategory, setVoiceSearchCategory] = useState('Educational');
  const [voiceSearchResults, setVoiceSearchResults] = useState([]);

  // Check API health
  const checkHealth = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/health`);
      if (res.ok) {
        setApiOnline(true);
        fetchBrand();
        fetchLeads();
        fetchConversations();
        fetchVoiceSamples();
      } else {
        setApiOnline(false);
      }
    } catch (e) {
      setApiOnline(false);
    } finally {
      setCheckingApi(false);
    }
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  // Scroll active chat scroll pane
  useEffect(() => {
    chatBottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chats, activeChatId, loading]);

  const fetchBrand = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/brand`);
      if (res.ok) {
        const data = await res.json();
        setBrand(data);
      }
    } catch(e) {}
  };

  const fetchLeads = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/leads`);
      if (res.ok) {
        const data = await res.json();
        setLeads(data);
      }
    } catch(e) {}
  };

  const fetchConversations = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/conversations`);
      if (res.ok) {
        const data = await res.json();
        setConversations(data);
      }
    } catch(e) {}
  };

  const fetchVoiceSamples = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/voice-samples`);
      if (res.ok) {
        const data = await res.json();
        setVoiceSamples(data);
      }
    } catch(e) {}
  };

  // Create a brand new Chat session
  const handleNewChat = () => {
    const newId = `chat-${Date.now()}`;
    const newSession = {
      id: newId,
      title: '💬 שיחה חדשה',
      messages: [
        { role: 'agent', content: '🤖 שלום! אני AutoEngage — סוכן השיווק האוטונומי שלך. כיצד אוכל לעזור לקדם את העסק שלך היום? תוכל להתייעץ איתי, לנתח פוסטים ויראליים או לבנות מובילי לידים!' }
      ]
    };
    setChats(prev => [newSession, ...prev]);
    setActiveChatId(newId);
    setIsSidebarOpen(true);
  };

  // Submit text message in the chat
  const handleSendMessage = async (textToSend) => {
    const userMsg = typeof textToSend === 'string' ? textToSend : currentMessage;
    if (!userMsg.trim()) return;

    // Find current active chat index
    const chatIndex = chats.findIndex(c => c.id === activeChatId);
    if (chatIndex === -1) return;

    // Append User Message to chats list
    const updatedChats = [...chats];
    const targetChat = { ...updatedChats[chatIndex] };
    
    // Update title from default "שיחה חדשה" if it is the first message
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
        let reply = "שרת ה-API כרגע במצב סימולציה מקומית. כדי לקבל מענה חי משרת ה-Groq שלך, וודא שביצעת הרצה ל-server.py ושמפתח ה-API תקין.";
        targetChat.messages = [...targetChat.messages, { role: 'agent', content: reply }];
        updatedChats[chatIndex] = targetChat;
        setChats([...updatedChats]);
        setLoading(false);
      }, 1200);
      return;
    }

    try {
      // Build conversation history logs (exclude initial welcome)
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
        
        // Refresh leads list or DMs log automatically if tool triggered
        fetchLeads();
        fetchConversations();
      } else {
        throw new Error();
      }
    } catch(err) {
      targetChat.messages = [...targetChat.messages, { 
        role: 'agent', 
        content: 'שגיאה בתקשורת עם השרת או שמפתח ה-Groq שסיפקת החזיר שגיאת הרשאה 401. אנא וודא שהגדרת GROQ_API_KEY תקין בקובץ ה-`.env` והרצת מחדש את השרת.' 
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

  // Submit Brand profile updates
  const handleUpdateBrand = (e) => {
    if (e) e.preventDefault();
    if (!apiOnline) {
      alert("פרופיל המותג עודכן מקומית (API מנותק)");
      return;
    }

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
      alert("פרופיל המותג נשמר וסונכרן בהצלחה בשרת!");
    })
    .catch(() => {
      alert("שגיאה בעדכון פרופיל המותג.");
    });
  };

  // Add sample voice sample
  const handleAddVoice = (e) => {
    if (e) e.preventDefault();
    if (!apiOnline) {
      setVoiceSamples(prev => [{ text: newVoiceText, category: newVoiceCategory }, ...prev]);
      setNewVoiceText('');
      alert("הסגנון נשמר מקומית (API מנותק)");
      return;
    }

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
      alert("סגנון הכתיבה נוסף בהצלחה למאגר ה-Voice Store של הסוכן!");
    })
    .catch(() => {
      alert("שגיאה בהוספת דגימת הקול.");
    });
  };

  // Search similar writing samples
  const handleSearchVoice = () => {
    if (!apiOnline) {
      const results = voiceSamples.filter(v => v.category === voiceSearchCategory);
      setVoiceSearchResults(results.length > 0 ? results : [{ text: `דגימה מדמה בקטגוריית ${voiceSearchCategory} התואמת לחיפוש: ${voiceSearchQuery}`, category: voiceSearchCategory }]);
      return;
    }

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
      alert("שגיאה בחיפוש דגימות קול.");
    });
  };

  // Get current active chat session messages
  const activeChat = chats.find(c => c.id === activeChatId) || chats[0];

  return (
    <div className="app-container">
      {/* API Status indicator */}
      <div className={`api-toast ${apiOnline ? 'online' : 'offline'}`}>
        <span className="dot"></span>
        {apiOnline ? 'שרת ה-API מחובר (Live)' : 'סימולציה מקומית (API מנותק)'}
      </div>

      {/* Slideout Sidebar of Previous Chats */}
      <div className={`sidebar ${isSidebarOpen ? '' : 'collapsed'}`}>
        <div className="sidebar-header">
          <div className="sidebar-logo-group">
            <div className="sidebar-logo">AE</div>
            <div className="sidebar-title">AutoEngage</div>
          </div>
        </div>

        {/* New Chat Trigger button */}
        <button className="new-chat-btn" onClick={handleNewChat}>
          <Plus size={18} /> שיחה חדשה
        </button>

        {/* Previous Chat lists */}
        <div className="sidebar-category-header">שיחות פעילות (Chats)</div>
        <ul className="sidebar-menu">
          {chats.filter(c => !c.id.startsWith('dm')).map(c => (
            <li key={c.id}>
              <button 
                className={`sidebar-item-btn ${activeChatId === c.id ? 'active' : ''}`}
                onClick={() => setActiveChatId(c.id)}
              >
                <MessageSquare size={16} style={{ flexShrink: 0 }} />
                <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{c.title}</span>
              </button>
            </li>
          ))}
        </ul>

        {/* Outreach DMs logs */}
        <div className="sidebar-category-header">הודעות ישירות (Outreach DMs)</div>
        <ul className="sidebar-menu" style={{ flex: 'none', height: '140px', overflowY: 'auto' }}>
          {chats.filter(c => c.id.startsWith('dm')).map(c => (
            <li key={c.id}>
              <button 
                className={`sidebar-item-btn ${activeChatId === c.id ? 'active' : ''}`}
                onClick={() => setActiveChatId(c.id)}
              >
                <Plus size={14} style={{ flexShrink: 0, color: 'var(--secondary)' }} />
                <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{c.title}</span>
              </button>
            </li>
          ))}
        </ul>

        {/* Settings button at the footer */}
        <div className="sidebar-footer">
          <button 
            className="sidebar-item-btn active" 
            style={{ borderLeft: 'none', background: 'linear-gradient(135deg, rgba(139,92,246,0.1), rgba(255,255,255,0.01))', color: '#fff' }}
            onClick={() => setIsSettingsOpen(true)}
          >
            <Settings size={18} /> פרופיל וסגנונות כתיבה
          </button>
        </div>
      </div>

      {/* Main Chat Content Panel */}
      <div className="main-content">
        <div className="workspace-header">
          {/* Hamburger Sidebar Trigger */}
          <button className="hamburger-btn" onClick={() => setIsSidebarOpen(!isSidebarOpen)}>
            <Menu size={22} />
          </button>

          <div className="workspace-title">
            <h2>סוכן שיווק AI אוטונומי</h2>
            <p>שוחח ישירות עם סוכן ה-AI. הסוכן מחובר ל-35 כלי שיווק, האזנה, ופרסום ברשת ומפעיל אותם אוטומטית בהתאם לצורך!</p>
          </div>
        </div>

        <div className="workspace-body">
          <div className="chat-workspace">
            <div className="chat-panel">
              
              {/* If New Chat with only initial message, show Gemini/GPT Welcome Grid */}
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
                    <div key={idx} className={`message ${msg.role}`}>
                      <div className="chat-avatar">
                        {msg.role === 'user' ? '👤' : '🤖'}
                      </div>
                      <div className="message-bubble-wrapper">
                        <div className="message-bubble">
                          {msg.content}
                        </div>

                        {/* Collapsible log showing background AI tool operations executed */}
                        {msg.toolCalls && msg.toolCalls.length > 0 && (
                          <div className="tool-call-accordion">
                            <div className="tool-call-header" onClick={() => toggleToolLogs(idx)}>
                              <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                                <Terminal size={12} />
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
                            <div className="typing-indicator">
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

              {/* Botton pill chat bar */}
              <div className="chat-input-area">
                <form className="chat-input-pill-wrapper" onSubmit={(e) => { e.preventDefault(); handleSendMessage(); }}>
                  <input 
                    type="text" 
                    placeholder="הקלד כאן הודעה להנחיית סוכן ה-AI (למשל: נסח פוסט, חקור מתחרים, סרוק רדיט...)" 
                    value={currentMessage}
                    onChange={(e) => setCurrentMessage(e.target.value)}
                  />
                  <button className="send-pill-btn" type="submit" disabled={loading || !currentMessage.trim()}>
                    <Send size={18} style={{ transform: 'rotate(-45deg) translate(2px, -2px)' }} />
                  </button>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Settings Overlay Drawer Panel (Slideout from the right) */}
      <div 
        className={`settings-overlay-backdrop ${isSettingsOpen ? 'open' : ''}`}
        onClick={() => setIsSettingsOpen(false)}
      ></div>
      
      <div className={`settings-overlay ${isSettingsOpen ? 'open' : ''}`}>
        <div className="settings-overlay-header">
          <h3><Settings size={20} /> פרופיל וסגנון כתיבה (Brand & Voice)</h3>
          <button className="close-drawer-btn" onClick={() => setIsSettingsOpen(false)}>
            <X size={20} />
          </button>
        </div>

        {/* Drawer Tabs Navigation */}
        <div style={{ display: 'flex', background: 'rgba(255,255,255,0.02)', borderBottom: '1px solid var(--border-color)' }}>
          <button 
            style={{ flex: 1, padding: '14px', border: 'none', background: activeSettingsTab === 'Brand' ? 'rgba(139,92,246,0.1)' : 'none', color: activeSettingsTab === 'Brand' ? 'var(--primary)' : 'var(--text-muted)', borderBottom: activeSettingsTab === 'Brand' ? '2px solid var(--primary)' : 'none', cursor: 'pointer', fontWeight: 'bold' }}
            onClick={() => setActiveSettingsTab('Brand')}
          >
            פרופיל מותג
          </button>
          <button 
            style={{ flex: 1, padding: '14px', border: 'none', background: activeSettingsTab === 'Voice' ? 'rgba(139,92,246,0.1)' : 'none', color: activeSettingsTab === 'Voice' ? 'var(--primary)' : 'var(--text-muted)', borderBottom: activeSettingsTab === 'Voice' ? '2px solid var(--primary)' : 'none', cursor: 'pointer', fontWeight: 'bold' }}
            onClick={() => setActiveSettingsTab('Voice')}
          >
            מאגר קולות כתיבה
          </button>
          <button 
            style={{ flex: 1, padding: '14px', border: 'none', background: activeSettingsTab === 'Leads' ? 'rgba(139,92,246,0.1)' : 'none', color: activeSettingsTab === 'Leads' ? 'var(--primary)' : 'var(--text-muted)', borderBottom: activeSettingsTab === 'Leads' ? '2px solid var(--primary)' : 'none', cursor: 'pointer', fontWeight: 'bold' }}
            onClick={() => setActiveSettingsTab('Leads')}
          >
            לידים ושיחות DMs
          </button>
        </div>

        <div className="settings-overlay-body">
          
          {/* TAB A: BRAND SETTINGS */}
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
                  value={brand.forbidden_phrases.join(', ')} 
                  onChange={(e) => setBrand({ ...brand, forbidden_phrases: e.target.value.split(',').map(s => s.trim()) })}
                />
              </div>

              <button className="btn" type="submit" style={{ width: '100%' }}>
                שמור סנכרן פרופיל מותג בשרת
              </button>
            </form>
          )}

          {/* TAB B: VOICE STORE */}
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
                    <option>Educational</option>
                    <option>Casual</option>
                    <option>Technical</option>
                    <option>Storytelling</option>
                  </select>
                </div>
                <button className="btn btn-secondary" type="submit" style={{ width: '100%' }}>
                  הוסף דגימת סגנון למאגר
                </button>
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
                      <option>Educational</option>
                      <option>Casual</option>
                      <option>Technical</option>
                      <option>Storytelling</option>
                    </select>
                  </div>
                </div>
                <button className="btn btn-outline" type="button" onClick={handleSearchVoice} style={{ width: '100%' }}>
                  חפש דגימות סגנון דומות
                </button>

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

          {/* TAB C: LEADS AND OUTREACH REGISTER */}
          {activeSettingsTab === 'Leads' && (
            <div>
              <h4 style={{ color: '#fff', marginBottom: '10px', fontSize: '0.95rem' }}>מאגר לידים שנתפסו בערוצים</h4>
              <div className="data-table-wrapper" style={{ marginBottom: '24px' }}>
                <table>
                  <thead>
                    <tr>
                      <th>שם משתמש</th>
                      <th>ערוץ</th>
                      <th>מדריך מבוקש</th>
                    </tr>
                  </thead>
                  <tbody>
                    {leads.length === 0 ? (
                      <tr>
                        <td colSpan="3" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>טרם נלכדו לידים במאגר.</td>
                      </tr>
                    ) : (
                      leads.map((l, i) => (
                        <tr key={i}>
                          <td style={{ fontWeight: '600' }}>@{l.username}</td>
                          <td><span className="badge warning" style={{ background: l.platform === 'Reddit' ? 'rgba(249,90,5,0.1)' : 'rgba(10,102,194,0.1)', color: l.platform === 'Reddit' ? '#f95a05' : '#0a66c2' }}>{l.platform}</span></td>
                          <td style={{ color: 'var(--text-muted)' }}>{l.interest}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>

              <h4 style={{ color: '#fff', marginBottom: '10px', fontSize: '0.95rem' }}>יומן שיחות DMs פעיל</h4>
              <div className="data-table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>לקוח</th>
                      <th>תוכן הודעה</th>
                      <th>סטטוס</th>
                    </tr>
                  </thead>
                  <tbody>
                    {conversations.length === 0 ? (
                      <tr>
                        <td colSpan="3" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>טרם תועדו שיחות DMs במאגר.</td>
                      </tr>
                    ) : (
                      conversations.map((c, i) => (
                        <tr key={i}>
                          <td style={{ fontWeight: '600' }}>{c.lead_name}</td>
                          <td style={{ fontSize: '0.8rem', color: 'var(--text-muted)', maxWidth: '160px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{c.message}</td>
                          <td><span className={`badge ${c.status === 'Sent' ? 'warning' : 'success'}`}>{c.status}</span></td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}
