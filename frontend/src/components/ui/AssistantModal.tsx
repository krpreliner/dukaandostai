import React, { useState, useEffect, useRef } from 'react';
import {
  X,
  Send,
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  Bot,
  User,
  Sparkles,
  Trash2,
  Wrench,
  Loader2,
  HelpCircle,
  TrendingUp,
  AlertTriangle,
  Package
} from 'lucide-react';
import { sendAssistantChat, getAssistantHistory, clearAssistantHistory } from '../../services/api';
import { ChatMessageData } from '../../types';
import { useLanguage } from '../../contexts/LanguageContext';

interface AssistantModalProps {
  isOpen: boolean;
  onClose: () => void;
}

// Quick starter prompt pills for Sharma Ji in Hindi & English
const STARTER_PROMPTS_HI = [
  { label: '📊 आज की बिक्री और मुनाफ़ा', query: 'आज की कुल बिक्री और मुनाफ़ा कितना हुआ है?' },
  { label: '⚠️ कम स्टॉक का अलर्ट', query: 'कौनसे किराना सामान का स्टॉक कम है?' },
  { label: '👥 सुस्त ग्राहक सूची', query: 'कौनसे ग्राहक पिछले 30 दिन से दुकान नहीं आए?' },
  { label: '📈 10,000 लक्ष्य रणनीति', query: 'नेट मुनाफ़े को 8,000 से 10,000 ले जाने के लिए क्या करना चाहिए?' }
];

const STARTER_PROMPTS_EN = [
  { label: '📊 Today’s Sales & Net Profit', query: 'What is today’s total sales and net profit summary?' },
  { label: '⚠️ Low Stock Alerts', query: 'Which grocery inventory items are low in stock?' },
  { label: '👥 Dormant Customer List', query: 'Which customers have been inactive for over 30 days?' },
  { label: '📈 ₹10,000 Profit Strategy', query: 'How can we bridge monthly net income from ₹8,000 to ₹10,000?' }
];

export const AssistantModal: React.FC<AssistantModalProps> = ({ isOpen, onClose }) => {
  const { language, setLanguage } = useLanguage();
  const [messages, setMessages] = useState<ChatMessageData[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [speakingId, setSpeakingId] = useState<number | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<any>(null);

  // Auto scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      loadHistory();
    } else {
      stopSpeaking();
      stopListening();
    }
  }, [isOpen]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const loadHistory = async () => {
    try {
      const data = await getAssistantHistory('SESSION_DEFAULT');
      if (Array.isArray(data)) {
        setMessages(data);
      } else if (data && data.messages) {
        setMessages(data.messages);
      }
    } catch (err) {
      console.error('Error fetching chat history:', err);
    }
  };

  const handleClearHistory = async () => {
    if (!window.confirm('Clear all conversation history with DukaanDost AI?')) return;
    try {
      await clearAssistantHistory('SESSION_DEFAULT');
      setMessages([]);
      stopSpeaking();
    } catch (err) {
      console.error('Error clearing chat history:', err);
    }
  };

  const handleSend = async (textToSend?: string) => {
    const text = (textToSend || inputText).trim();
    if (!text || isLoading) return;

    const userMsg: ChatMessageData = {
      role: 'user',
      content: text,
      timestamp: new Date().toISOString()
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputText('');
    setIsLoading(true);

    try {
      const res = await sendAssistantChat(text, 'SESSION_DEFAULT', language);
      const assistantMsg: ChatMessageData = {
        role: 'assistant',
        content: res.content || res.response || 'Namaste Sharma Ji!',
        tools_used: res.tools_used || [],
        suggested_actions: res.suggested_actions || [],
        provider: res.provider || 'Groq',
        model: res.model || 'qwen/qwen3.8-27b',
        latency_ms: res.latency_ms || 0,
        timestamp: new Date().toISOString()
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      console.error('Error sending message:', err);
      const errorMsg: ChatMessageData = {
        role: 'assistant',
        content: 'Maaf kijiye Sharma Ji, kuch takneeki samasya aayi. Kripya punah koshish karein.',
        timestamp: new Date().toISOString()
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  // ----------------------------------------------------
  // Speech-to-Text (STT) via Web Speech API
  // ----------------------------------------------------
  const toggleListening = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  const startListening = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert('Speech recognition is not supported in this browser. Please use Chrome, Edge, or Brave.');
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.lang = language === 'hi' ? 'hi-IN' : 'en-IN';
      recognition.continuous = false;
      recognition.interimResults = false;

      recognition.onstart = () => {
        setIsListening(true);
      };

      recognition.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        if (transcript) {
          setInputText((prev) => (prev ? `${prev} ${transcript}` : transcript));
        }
      };

      recognition.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (err) {
      console.error('Failed to start speech recognition:', err);
      setIsListening(false);
    }
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
    }
    setIsListening(false);
  };

  // ----------------------------------------------------
  // Text-to-Speech (TTS) via W3C Web Speech API
  // ----------------------------------------------------
  const playSpeech = (text: string, index: number) => {
    if (!window.speechSynthesis) {
      alert('Text-to-speech is not supported in this browser.');
      return;
    }

    if (speakingId === index) {
      stopSpeaking();
      return;
    }

    window.speechSynthesis.cancel();

    const isHindi = language === 'hi';
    const cleanText = text
      .replace(/[*#_`]/g, '')
      .replace(/₹\s*/g, isHindi ? ' रुपये ' : ' Rupees ')
      .replace(/\bRs\.?\s*/gi, isHindi ? ' रुपये ' : ' Rupees ')
      .replace(/%/g, isHindi ? ' प्रतिशत ' : ' percent ')
      .replace(/\bunits\b/gi, isHindi ? 'पैकेट' : 'units')
      .replace(/\bCOGS\b/gi, isHindi ? 'लागत' : 'cost of goods')
      .replace(/\bvs\b/gi, isHindi ? 'के मुकाबले' : 'versus')
      .trim();

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = isHindi ? 'hi-IN' : 'en-IN';
    utterance.rate = 0.94;
    utterance.pitch = 1.0;

    const voices = window.speechSynthesis.getVoices();
    if (isHindi) {
      const hindiVoice =
        voices.find((v) => v.lang === 'hi-IN' || v.lang.startsWith('hi')) ||
        voices.find((v) => v.name.toLowerCase().includes('hindi')) ||
        voices.find((v) => v.lang === 'en-IN');
      if (hindiVoice) utterance.voice = hindiVoice;
    } else {
      const enVoice =
        voices.find((v) => v.lang === 'en-IN' || v.name.toLowerCase().includes('india')) ||
        voices.find((v) => v.lang.startsWith('en'));
      if (enVoice) utterance.voice = enVoice;
    }

    utterance.onend = () => {
      setSpeakingId(null);
    };

    utterance.onerror = () => {
      setSpeakingId(null);
    };

    setSpeakingId(index);
    window.speechSynthesis.speak(utterance);
  };

  const stopSpeaking = () => {
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }
    setSpeakingId(null);
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/60 backdrop-blur-xs z-40 transition-opacity"
        onClick={onClose}
      />

      {/* Slide-over Drawer */}
      <div className="fixed inset-y-0 right-0 w-full sm:w-[500px] z-50 bg-[#0A0A0A] border-l border-white/[0.1] shadow-2xl flex flex-col transform transition-transform duration-300 ease-in-out">
        {/* Drawer Header */}
        <div className="p-4 px-6 border-b border-white/[0.08] bg-[#0E0E0E] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-[#22D3EE]/15 border border-[#22D3EE]/30 flex items-center justify-center text-[#22D3EE] shadow-sm">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-base font-semibold text-white tracking-tight">
                  DukaanDost AI Business Partner
                </h2>
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" title="Live Groq AI Connected" />
              </div>
              <p className="text-[11px] text-neutral-400">
                Sharma Ji's 24/7 Kirana Operations Assistant • Hindi & Hinglish
              </p>
            </div>
          </div>

          <div className="flex items-center gap-1.5">
            {/* Assistant Drawer Language Toggle */}
            <div className="flex items-center p-0.5 bg-[#171717] border border-white/[0.08] rounded-lg text-xs mr-1">
              <button
                onClick={() => setLanguage('hi')}
                title="हिंदी में बात करें"
                className={`px-2 py-0.5 rounded text-[10px] font-semibold transition-all cursor-pointer ${
                  language === 'hi' ? 'bg-[#22D3EE] text-black shadow-xs' : 'text-neutral-400 hover:text-white'
                }`}
              >
                हिंदी
              </button>
              <button
                onClick={() => setLanguage('en')}
                title="Switch to English"
                className={`px-2 py-0.5 rounded text-[10px] font-semibold transition-all cursor-pointer ${
                  language === 'en' ? 'bg-[#22D3EE] text-black shadow-xs' : 'text-neutral-400 hover:text-white'
                }`}
              >
                EN
              </button>
            </div>

            <button
              onClick={handleClearHistory}
              title="Clear chat history"
              className="p-2 rounded-lg text-neutral-400 hover:text-red-400 hover:bg-neutral-800/80 transition-colors"
            >
              <Trash2 className="w-4 h-4" />
            </button>
            <button
              onClick={onClose}
              title="Close Assistant"
              className="p-2 rounded-lg text-neutral-400 hover:text-white hover:bg-neutral-800/80 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Message Thread Body */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
          {messages.length === 0 ? (
            <div className="py-8 text-center space-y-6">
              <div className="w-16 h-16 rounded-2xl bg-[#141414] border border-white/[0.08] flex items-center justify-center mx-auto text-[#22D3EE]">
                <Bot className="w-8 h-8" />
              </div>
              <div>
                <h3 className="text-base font-semibold text-white">
                  {language === 'hi' ? 'नमस्ते शर्मा जी! 🙏' : 'Namaste Sharma Ji! 🙏'}
                </h3>
                <p className="text-xs text-neutral-400 max-w-xs mx-auto mt-1 leading-relaxed">
                  {language === 'hi'
                    ? 'मैं आपका AI व्यापार साथी हूँ। बिक्री, स्टॉक, उधारी, ग्राहक या मुनाफ़े के बारे में कुछ भी पूछिए।'
                    : 'I am your AI Business Partner. Ask anything about sales, low inventory, customer retention, or profit goals.'}
                </p>
              </div>

              {/* Starter Quick Actions */}
              <div className="space-y-2 pt-2">
                <span className="text-[11px] font-semibold text-neutral-500 uppercase tracking-wider">
                  {language === 'hi' ? 'सीधे पूछें (Quick Prompts):' : 'Quick Starter Prompts:'}
                </span>
                <div className="grid grid-cols-1 gap-2 text-left">
                  {(language === 'hi' ? STARTER_PROMPTS_HI : STARTER_PROMPTS_EN).map((prompt, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSend(prompt.query)}
                      className="p-3 rounded-xl bg-[#121212] hover:bg-[#181818] border border-white/[0.06] hover:border-[#22D3EE]/40 text-xs text-neutral-300 hover:text-white transition-all text-left flex items-center justify-between group cursor-pointer"
                    >
                      <span>{prompt.label}</span>
                      <span className="text-[11px] text-neutral-500 group-hover:text-[#22D3EE] transition-colors">
                        Ask &rarr;
                      </span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            messages.map((msg, index) => {
              const isAssistant = msg.role === 'assistant';

              return (
                <div
                  key={index}
                  className={`flex gap-3 ${isAssistant ? 'justify-start' : 'justify-end'}`}
                >
                  {isAssistant && (
                    <div className="w-7 h-7 rounded-lg bg-[#22D3EE]/10 border border-[#22D3EE]/20 flex items-center justify-center text-[#22D3EE] flex-shrink-0 mt-1">
                      <Bot className="w-4 h-4" />
                    </div>
                  )}

                  <div
                    className={`max-w-[85%] rounded-2xl p-4 text-xs leading-relaxed space-y-2 ${
                      isAssistant
                        ? 'bg-[#141414] border border-white/[0.08] text-neutral-200'
                        : 'bg-[#1C2833] border border-[#22D3EE]/30 text-white shadow-sm'
                    }`}
                  >
                    {/* Header info for assistant messages */}
                    {isAssistant && (
                      <div className="flex items-center justify-between pb-1 border-b border-white/[0.04] mb-2 text-[10px] text-neutral-500">
                        <div className="flex items-center gap-1.5">
                          <span className="font-semibold text-neutral-400">DukaanDost AI</span>
                          {msg.latency_ms && (
                            <span>• {msg.latency_ms}ms</span>
                          )}
                        </div>
                        <button
                          onClick={() => playSpeech(msg.content, index)}
                          title={speakingId === index ? "Stop voice" : "Read aloud (Hindi/English)"}
                          className={`p-1 rounded hover:bg-white/[0.06] transition-colors ${
                            speakingId === index ? 'text-[#22D3EE]' : 'text-neutral-400 hover:text-white'
                          }`}
                        >
                          {speakingId === index ? (
                            <VolumeX className="w-3.5 h-3.5 animate-pulse" />
                          ) : (
                            <Volume2 className="w-3.5 h-3.5" />
                          )}
                        </button>
                      </div>
                    )}

                    {/* Tool badges if any tool was executed */}
                    {isAssistant && msg.tools_used && msg.tools_used.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 pt-0.5">
                        {msg.tools_used.map((tool, tIdx) => (
                          <span
                            key={tIdx}
                            className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono bg-[#22D3EE]/10 text-[#22D3EE] border border-[#22D3EE]/20"
                          >
                            <Wrench className="w-2.5 h-2.5" />
                            {tool}
                          </span>
                        ))}
                      </div>
                    )}

                    {/* Message content */}
                    <p className="whitespace-pre-line text-neutral-100">{msg.content}</p>

                    {/* Follow-up suggestion action chips */}
                    {isAssistant && msg.suggested_actions && msg.suggested_actions.length > 0 && (
                      <div className="pt-2 border-t border-white/[0.06] space-y-1.5">
                        <span className="text-[10px] text-neutral-500 font-medium">Suggested queries:</span>
                        <div className="flex flex-wrap gap-1.5">
                          {msg.suggested_actions.map((action, aIdx) => (
                            <button
                              key={aIdx}
                              onClick={() => handleSend(action)}
                              className="px-2.5 py-1 rounded-lg bg-[#1B1B1B] hover:bg-[#222222] border border-white/[0.08] hover:border-[#22D3EE]/40 text-[11px] text-[#22D3EE] hover:text-cyan-300 transition-all text-left cursor-pointer"
                            >
                              {action}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {!isAssistant && (
                    <div className="w-7 h-7 rounded-lg bg-white/[0.1] border border-white/[0.2] flex items-center justify-center text-white flex-shrink-0 mt-1">
                      <User className="w-4 h-4" />
                    </div>
                  )}
                </div>
              );
            })
          )}

          {isLoading && (
            <div className="flex gap-3 justify-start">
              <div className="w-7 h-7 rounded-lg bg-[#22D3EE]/10 border border-[#22D3EE]/20 flex items-center justify-center text-[#22D3EE] flex-shrink-0 mt-1">
                <Bot className="w-4 h-4" />
              </div>
              <div className="bg-[#141414] border border-white/[0.08] rounded-2xl p-4 text-xs text-neutral-400 flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin text-[#22D3EE]" />
                <span>Sharma Ji, main aapka data check kar raha hoon...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <div className="p-4 border-t border-white/[0.08] bg-[#0E0E0E]">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex items-center gap-2"
          >
            {/* Mic speech-to-text button */}
            <button
              type="button"
              onClick={toggleListening}
              title={isListening ? "Listening... click to stop" : "Voice input (Speak in Hindi or English)"}
              className={`p-2.5 rounded-xl border transition-all cursor-pointer ${
                isListening
                  ? 'bg-red-500/20 border-red-500 text-red-400 animate-pulse'
                  : 'bg-[#161616] border-white/[0.08] hover:border-[#22D3EE]/40 text-neutral-400 hover:text-white'
              }`}
            >
              {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
            </button>

            {/* Query input field */}
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder={
                language === 'hi'
                  ? "पूछिए: 'आज कितनी बिक्री हुई?' या 'स्टॉक अलर्ट्स'..."
                  : "Ask: 'What is today\'s sales?' or 'Low stock alerts'..."
              }
              disabled={isLoading}
              className="flex-1 bg-[#141414] border border-white/[0.08] focus:border-[#22D3EE] rounded-xl px-3.5 py-2.5 text-xs text-white placeholder-neutral-500 focus:outline-none transition-colors"
            />

            {/* Send button */}
            <button
              type="submit"
              disabled={!inputText.trim() || isLoading}
              className={`p-2.5 rounded-xl font-semibold text-xs transition-all flex items-center justify-center cursor-pointer ${
                !inputText.trim() || isLoading
                  ? 'bg-neutral-800 text-neutral-600 cursor-not-allowed'
                  : 'bg-[#22D3EE] hover:bg-[#06b6d4] text-black shadow-md shadow-[#22D3EE]/20'
              }`}
            >
              <Send className="w-4 h-4" />
            </button>
          </form>

          <div className="flex items-center justify-between text-[10px] text-neutral-500 mt-2 px-1">
            <span>Powered by Groq Cloud & Deterministic Tools</span>
            <span>Supports Hindi, Hinglish & English voice</span>
          </div>
        </div>
      </div>
    </>
  );
};
