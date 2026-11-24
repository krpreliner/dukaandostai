import React, { useEffect, useState, useRef } from 'react';
import {
  Sun,
  Volume2,
  VolumeX,
  Pause,
  Play,
  RotateCcw,
  Copy,
  Check,
  Sparkles,
  TrendingUp,
  AlertTriangle,
  Users,
  ArrowRight
} from 'lucide-react';
import { getLatestBriefing, generateFreshBriefing } from '../../services/api';
import { DailyBriefingData } from '../../types';
import { useLanguage } from '../../contexts/LanguageContext';

export const DailyBriefingCard: React.FC = () => {
  const { language, setLanguage } = useLanguage();
  const [briefing, setBriefing] = useState<DailyBriefingData | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [copied, setCopied] = useState(false);
  
  // Audio state
  const [isPlaying, setIsPlaying] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  const fetchBriefing = async () => {
    try {
      const data = await getLatestBriefing();
      setBriefing(data);
    } catch (err) {
      console.error('Error fetching briefing:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBriefing();
    return () => {
      if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
      }
    };
  }, []);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      const data = await generateFreshBriefing();
      setBriefing(data);
      if (window.speechSynthesis) {
        window.speechSynthesis.cancel();
        setIsPlaying(false);
        setIsPaused(false);
      }
    } catch (err) {
      console.error('Error generating briefing:', err);
    } finally {
      setRefreshing(false);
    }
  };

  const handlePlayAudio = () => {
    if (!briefing || !window.speechSynthesis) return;

    if (isPaused) {
      window.speechSynthesis.resume();
      setIsPaused(false);
      setIsPlaying(true);
      return;
    }

    window.speechSynthesis.cancel();

    // Prepare speech text with natural phonetics according to selected language
    const isHindi = language === 'hi';
    const rawScript = isHindi
      ? (briefing.audio_script_hi || briefing.audio_script)
      : (briefing.audio_script_en || briefing.summary_text);

    const cleanScript = rawScript
      .replace(/[*#_`]/g, '')
      .replace(/₹\s*/g, isHindi ? ' रुपये ' : ' Rupees ')
      .replace(/\bRs\.?\s*/gi, isHindi ? ' रुपये ' : ' Rupees ')
      .replace(/%/g, isHindi ? ' प्रतिशत ' : ' percent ')
      .replace(/\bCOGS\b/gi, isHindi ? 'लागत' : 'cost of goods')
      .replace(/\bvs\b/gi, isHindi ? 'के मुकाबले' : 'versus')
      .trim();

    const utterance = new SpeechSynthesisUtterance(cleanScript);
    utterance.lang = isHindi ? 'hi-IN' : 'en-IN';
    utterance.rate = 0.93;
    utterance.pitch = 1.0;

    // Pick authentic voice based on language
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
      setIsPlaying(false);
      setIsPaused(false);
    };

    utterance.onerror = () => {
      setIsPlaying(false);
      setIsPaused(false);
    };

    utteranceRef.current = utterance;
    window.speechSynthesis.speak(utterance);
    setIsPlaying(true);
    setIsPaused(false);
  };

  const handlePauseAudio = () => {
    if (window.speechSynthesis && isPlaying) {
      window.speechSynthesis.pause();
      setIsPaused(true);
      setIsPlaying(false);
    }
  };

  const handleStopAudio = () => {
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
      setIsPlaying(false);
      setIsPaused(false);
    }
  };

  const handleCopy = () => {
    if (!briefing) return;
    navigator.clipboard.writeText(briefing.summary_text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (loading || !briefing) {
    return (
      <div className="bg-[#111111] border border-white/[0.08] rounded-xl p-6 flex items-center justify-between">
        <div className="flex items-center gap-3 text-neutral-400 text-sm">
          <Sun className="w-5 h-5 text-[#22D3EE] animate-spin" />
          <span>Generating AI Daily Business Briefing for Sharma Ji...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-[#111111] border border-white/[0.08] rounded-xl p-6 relative overflow-hidden">
      {/* Background ambient glow */}
      <div className="absolute top-0 right-0 w-80 h-32 bg-[#22D3EE]/5 blur-3xl pointer-events-none" />

      {/* Header bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-white/[0.06] mb-5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-[#22D3EE]/10 border border-[#22D3EE]/20 flex items-center justify-center text-[#22D3EE]">
            <Sun className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-bold text-white tracking-tight">AI Daily Business Briefing</h3>
              <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded bg-[#22D3EE]/15 text-[#22D3EE] border border-[#22D3EE]/30">
                Live Diagnostic
              </span>
            </div>
            <p className="text-xs text-neutral-400">
              {briefing.briefing_date} • Personalized for Sharma General Store, Ranchi
            </p>
          </div>
        </div>

        {/* Audio and action controls */}
        <div className="flex items-center gap-2">
          {/* Card-level Language Switcher */}
          <div className="flex items-center p-0.5 bg-[#171717] border border-white/[0.08] rounded-lg text-xs mr-1">
            <button
              onClick={() => {
                setLanguage('hi');
                if (window.speechSynthesis) window.speechSynthesis.cancel();
                setIsPlaying(false);
              }}
              title="हिंदी में सुनें"
              className={`px-2 py-0.5 rounded text-[11px] font-semibold transition-all cursor-pointer ${
                language === 'hi' ? 'bg-[#22D3EE] text-black shadow-xs' : 'text-neutral-400 hover:text-white'
              }`}
            >
              हिंदी
            </button>
            <button
              onClick={() => {
                setLanguage('en');
                if (window.speechSynthesis) window.speechSynthesis.cancel();
                setIsPlaying(false);
              }}
              title="Listen in English"
              className={`px-2 py-0.5 rounded text-[11px] font-semibold transition-all cursor-pointer ${
                language === 'en' ? 'bg-[#22D3EE] text-black shadow-xs' : 'text-neutral-400 hover:text-white'
              }`}
            >
              English
            </button>
          </div>

          {isPlaying ? (
            <>
              <button
                onClick={handlePauseAudio}
                className="px-3 py-1.5 rounded-lg bg-neutral-800 hover:bg-neutral-700 text-neutral-200 text-xs font-medium flex items-center gap-1.5 transition-colors cursor-pointer"
                title="Pause audio"
              >
                <Pause className="w-3.5 h-3.5 text-[#22D3EE]" />
                <span>Pause</span>
              </button>
              <button
                onClick={handleStopAudio}
                className="px-3 py-1.5 rounded-lg bg-neutral-800 hover:bg-neutral-700 text-neutral-200 text-xs font-medium flex items-center gap-1.5 transition-colors cursor-pointer"
                title="Stop audio"
              >
                <VolumeX className="w-3.5 h-3.5 text-red-400" />
                <span>Stop</span>
              </button>
            </>
          ) : (
            <button
              onClick={handlePlayAudio}
              className="px-3.5 py-1.5 rounded-lg bg-[#22D3EE]/10 hover:bg-[#22D3EE]/20 border border-[#22D3EE]/30 text-[#22D3EE] text-xs font-medium flex items-center gap-1.5 transition-colors cursor-pointer shadow-sm shadow-[#22D3EE]/10"
              title="Listen to briefing read aloud in Hindi/English"
            >
              <Volume2 className="w-4 h-4 text-[#22D3EE]" />
              <span>{isPaused ? 'Resume Audio' : 'Read Aloud'}</span>
            </button>
          )}

          <button
            onClick={handleRefresh}
            disabled={refreshing}
            className="p-1.5 rounded-lg bg-neutral-900 hover:bg-neutral-800 border border-white/[0.08] text-neutral-400 hover:text-white transition-colors cursor-pointer"
            title="Refresh briefing with latest numbers"
          >
            <RotateCcw className={`w-4 h-4 ${refreshing ? 'animate-spin text-[#22D3EE]' : ''}`} />
          </button>

          <button
            onClick={handleCopy}
            className="p-1.5 rounded-lg bg-neutral-900 hover:bg-neutral-800 border border-white/[0.08] text-neutral-400 hover:text-white transition-colors cursor-pointer"
            title="Copy briefing text"
          >
            {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Greeting and highlights banner */}
      <div className="bg-[#141414] border border-white/[0.05] rounded-lg p-4 mb-5">
        <h4 className="text-sm font-semibold text-white mb-1 flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-[#22D3EE]" />
          {language === 'hi' ? 'नमस्ते शर्मा जी!' : 'Good Day, Sharma Ji!'}
        </h4>
        {language === 'hi' ? (
          <p className="text-xs text-neutral-300 leading-relaxed">
            आज आपकी दुकान की अनुमानित बिक्री लगभग <strong className="text-white">₹{briefing.today_sales.toLocaleString('en-IN')}</strong> रही है{' '}
            <span className="text-emerald-400 font-semibold">(कल के मुकाबले +{briefing.sales_growth_pct}% ज़्यादा)</span>। दुकान में{' '}
            <span className="text-amber-400 font-semibold">{briefing.low_stock_count} ज़रूरी सामान का स्टॉक कम</span> है और{' '}
            <span className="text-indigo-400 font-semibold">{briefing.inactive_customer_count} सुस्त ग्राहकों</span> को री-एक्टिवेशन वाउचर भेजकर बिक्री बढ़ाई जा सकती है।
          </p>
        ) : (
          <p className="text-xs text-neutral-300 leading-relaxed">
            Today's estimated shop sales are approximately <strong className="text-white">₹{briefing.today_sales.toLocaleString('en-IN')}</strong>{' '}
            <span className="text-emerald-400 font-semibold">(+{briefing.sales_growth_pct}% vs yesterday)</span>. There are{' '}
            <span className="text-amber-400 font-semibold">{briefing.low_stock_count} products running low</span> in stock, and{' '}
            <span className="text-indigo-400 font-semibold">{briefing.inactive_customer_count} dormant customers</span> can be targeted with reactivation campaigns.
          </p>
        )}
      </div>

      {/* 3 Metric Pills */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-5">
        <div className="bg-[#0f0f0f] border border-white/[0.05] rounded-lg p-3 flex items-center gap-3">
          <div className="w-8 h-8 rounded bg-emerald-500/10 flex items-center justify-center text-emerald-400 shrink-0">
            <TrendingUp className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-bold text-neutral-500">Today's Sales Run-Rate</div>
            <div className="text-sm font-bold text-white">₹{briefing.today_sales.toLocaleString('en-IN')}</div>
            <div className="text-[10px] text-emerald-400">+{briefing.sales_growth_pct}% higher vs yesterday</div>
          </div>
        </div>

        <div className="bg-[#0f0f0f] border border-white/[0.05] rounded-lg p-3 flex items-center gap-3">
          <div className="w-8 h-8 rounded bg-amber-500/10 flex items-center justify-center text-amber-400 shrink-0">
            <AlertTriangle className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-bold text-neutral-500">Low Stock Warnings</div>
            <div className="text-sm font-bold text-white">{briefing.low_stock_count} Products Low</div>
            <div className="text-[10px] text-amber-400">Restock bread & staples</div>
          </div>
        </div>

        <div className="bg-[#0f0f0f] border border-white/[0.05] rounded-lg p-3 flex items-center gap-3">
          <div className="w-8 h-8 rounded bg-indigo-500/10 flex items-center justify-center text-indigo-400 shrink-0">
            <Users className="w-4 h-4" />
          </div>
          <div>
            <div className="text-[10px] uppercase font-bold text-neutral-500">Inactive Customers</div>
            <div className="text-sm font-bold text-white">{briefing.inactive_customer_count} Customers</div>
            <div className="text-[10px] text-indigo-400">Target reactivation pool</div>
          </div>
        </div>
      </div>

      {/* Top Growth Opportunities for Today */}
      {briefing.growth_opportunities && briefing.growth_opportunities.length > 0 && (
        <div className="border-t border-white/[0.06] pt-4">
          <div className="text-[11px] font-bold uppercase tracking-wider text-neutral-400 mb-2.5">
            Top 3 Actionable Opportunities for Today
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2.5">
            {briefing.growth_opportunities.map((opp, idx) => (
              <div
                key={idx}
                className="bg-[#141414] border border-white/[0.04] hover:border-[#22D3EE]/30 rounded-lg p-3 transition-colors"
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-semibold text-white truncate">{opp.title}</span>
                  <span className="text-xs font-bold text-[#22D3EE]">
                    +₹{opp.impact_inr.toLocaleString('en-IN')}
                  </span>
                </div>
                <div className="text-[11px] text-neutral-400 flex items-center gap-1">
                  <span>{opp.action}</span>
                  <ArrowRight className="w-3 h-3 text-neutral-500" />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
