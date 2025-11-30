import { useState, useMemo, useCallback, useEffect, type ReactNode } from 'react';
import type { Contact, Account } from '../types';
import {
  generateOutreach,
  generateLinkedInMessage,
  generateFollowUpSequence,
  getPersonalizationData,
  assessDataQuality,
  type OutreachTone,
  type OutreachVariant,
  type GeneratedOutreach,
  type FollowUpEmail,
  type DataQuality,
} from '../utils/outreachGenerator';
import { CopyButton } from './CopyButton';

interface Props {
  contact: Contact;
  account: Account;
  onClose: () => void;
}

type TabType = 'email' | 'linkedin' | 'sequence';
type GenerationStatus = 'idle' | 'generating' | 'success' | 'error';

interface AIGeneratedEmail {
  subject: string;
  opening: string;
  valueHook: string;
  callToAction: string;
  ps?: string;
}

interface AIGeneratedLinkedIn {
  connectionRequest: string;
  followUpMessage: string;
}

interface AIGeneratedSequence {
  day1: { subject: string; body: string };
  day3: { subject: string; body: string };
  day7: { subject: string; body: string };
  day14: { subject: string; body: string };
}

export function OutreachPanel({ contact, account, onClose }: Props) {
  const [activeTab, setActiveTab] = useState<TabType>('email');
  const [tone, setTone] = useState<OutreachTone>('conversational');
  const [showDataSources, setShowDataSources] = useState(false);

  // AI Generation State
  const [generationStatus, setGenerationStatus] = useState<GenerationStatus>('idle');
  const [aiEmail, setAiEmail] = useState<AIGeneratedEmail | null>(null);
  const [aiLinkedIn, setAiLinkedIn] = useState<AIGeneratedLinkedIn | null>(null);
  const [aiSequence, setAiSequence] = useState<AIGeneratedSequence | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [displayedText, setDisplayedText] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  // Fallback template-based generation
  const context = useMemo(() => ({ contact, account, tone, variant: 'value_led' as OutreachVariant }), [contact, account, tone]);
  const templateEmail = useMemo(() => generateOutreach(context), [context]);
  const templateLinkedIn = useMemo(() => generateLinkedInMessage(context), [context]);
  const templateSequence = useMemo(() => generateFollowUpSequence(context), [context]);

  const personalizationData = useMemo(() => getPersonalizationData(context), [context]);
  const dataQuality = useMemo(() => assessDataQuality(context), [context]);

  // Typing animation effect
  const animateText = useCallback((fullText: string, onComplete?: () => void) => {
    setIsTyping(true);
    setDisplayedText('');

    let index = 0;
    const chunkSize = 3; // Characters per tick for faster animation

    const interval = setInterval(() => {
      if (index < fullText.length) {
        setDisplayedText(fullText.slice(0, index + chunkSize));
        index += chunkSize;
      } else {
        clearInterval(interval);
        setIsTyping(false);
        onComplete?.();
      }
    }, 10);

    return () => clearInterval(interval);
  }, []);

  // Generate AI outreach
  const generateAIOutreach = useCallback(async () => {
    setGenerationStatus('generating');
    setError(null);
    setDisplayedText('');

    const outreachType = activeTab === 'sequence' ? 'sequence' : activeTab;

    try {
      const response = await fetch('http://localhost:5001/api/outreach/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          contact,
          account,
          outreach_type: outreachType,
          tone
        })
      });

      const data = await response.json();

      if (!response.ok) {
        if (data.fallback) {
          // Use template fallback
          setError('AI generation unavailable - using template');
          setGenerationStatus('error');
          return;
        }
        throw new Error(data.message || 'Generation failed');
      }

      const generated = data.generated;

      if (activeTab === 'email') {
        setAiEmail(generated);
        // Compose full message for animation
        const fullMessage = `${generated.opening}\n\n${generated.valueHook}\n\n${generated.callToAction}\n\n${generated.ps || ''}`;
        animateText(fullMessage);
      } else if (activeTab === 'linkedin') {
        setAiLinkedIn(generated);
        animateText(generated.connectionRequest);
      } else if (activeTab === 'sequence') {
        setAiSequence(generated);
        animateText(generated.day1.body);
      }

      setGenerationStatus('success');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      setGenerationStatus('error');
    }
  }, [contact, account, activeTab, tone, animateText]);

  // Reset AI state when tab changes
  useEffect(() => {
    setGenerationStatus('idle');
    setDisplayedText('');
    setError(null);
  }, [activeTab]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ backgroundColor: 'rgba(0, 0, 0, 0.8)' }}
      onClick={onClose}
    >
      <div
        className="w-full max-w-4xl max-h-[90vh] rounded-xl overflow-hidden flex flex-col"
        style={{
          backgroundColor: 'var(--color-bg-elevated)',
          border: '1px solid var(--color-border-default)',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
        }}
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <PanelHeader contact={contact} account={account} onClose={onClose} />

        {/* MEDDIC Context Bar */}
        <MeddicContextBar contact={contact} dataQuality={dataQuality} />

        {/* Data Sources Toggle */}
        <DataSourcesBar
          personalizationData={personalizationData}
          showDataSources={showDataSources}
          onToggle={() => setShowDataSources(!showDataSources)}
        />

        {/* Controls Bar */}
        <ControlsBar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          tone={tone}
          setTone={setTone}
        />

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-5">
          {/* AI Generation Button */}
          <GenerateButton
            status={generationStatus}
            onGenerate={generateAIOutreach}
            error={error}
          />

          {activeTab === 'email' && (
            <EmailContent
              aiEmail={aiEmail}
              templateEmail={templateEmail}
              generationStatus={generationStatus}
              displayedText={displayedText}
              isTyping={isTyping}
            />
          )}
          {activeTab === 'linkedin' && (
            <LinkedInContent
              aiLinkedIn={aiLinkedIn}
              templateMessage={templateLinkedIn}
              generationStatus={generationStatus}
              displayedText={displayedText}
              isTyping={isTyping}
            />
          )}
          {activeTab === 'sequence' && (
            <SequenceContent
              aiSequence={aiSequence}
              templateSequence={templateSequence}
              generationStatus={generationStatus}
              displayedText={displayedText}
              isTyping={isTyping}
            />
          )}
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// Generate Button Component
// ============================================================================

function GenerateButton({
  status,
  onGenerate,
  error
}: {
  status: GenerationStatus;
  onGenerate: () => void;
  error: string | null;
}) {
  return (
    <div className="mb-6">
      <button
        onClick={onGenerate}
        disabled={status === 'generating'}
        className="w-full py-4 rounded-xl font-semibold text-base transition-all flex items-center justify-center gap-3"
        style={{
          background: status === 'generating'
            ? 'linear-gradient(135deg, var(--color-bg-card) 0%, var(--color-bg-elevated) 100%)'
            : 'linear-gradient(135deg, var(--color-accent-primary) 0%, #7c3aed 100%)',
          color: status === 'generating' ? 'var(--color-text-muted)' : 'white',
          boxShadow: status === 'generating' ? 'none' : '0 4px 14px rgba(99, 102, 241, 0.4)',
          border: status === 'generating' ? '1px solid var(--color-border-default)' : 'none',
          cursor: status === 'generating' ? 'not-allowed' : 'pointer',
        }}
      >
        {status === 'generating' ? (
          <>
            <LoadingSpinner />
            <span>Crafting personalized outreach...</span>
          </>
        ) : status === 'success' ? (
          <>
            <SparklesIcon />
            <span>Regenerate with AI</span>
          </>
        ) : (
          <>
            <SparklesIcon />
            <span>Generate Personalized Outreach with AI</span>
          </>
        )}
      </button>

      {error && (
        <div
          className="mt-3 p-3 rounded-lg flex items-center gap-2"
          style={{
            backgroundColor: 'var(--color-priority-low-bg)',
            border: '1px solid var(--color-priority-low-border)'
          }}
        >
          <svg className="w-4 h-4" style={{ color: 'var(--color-priority-low)' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span className="text-sm" style={{ color: 'var(--color-priority-low)' }}>{error}</span>
        </div>
      )}

      {status === 'idle' && (
        <p className="text-center text-xs mt-2" style={{ color: 'var(--color-text-muted)' }}>
          AI will use role tier, trigger events, and account intelligence to craft personalized messaging
        </p>
      )}
    </div>
  );
}

function LoadingSpinner() {
  return (
    <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
    </svg>
  );
}

function SparklesIcon() {
  return (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
    </svg>
  );
}

// ============================================================================
// Header Components
// ============================================================================

function PanelHeader({
  contact,
  account,
  onClose
}: {
  contact: Contact;
  account: Account;
  onClose: () => void;
}) {
  return (
    <div
      className="p-5 flex items-center justify-between"
      style={{ borderBottom: '1px solid var(--color-border-subtle)' }}
    >
      <div>
        <h2
          className="text-xl font-semibold flex items-center gap-2"
          style={{ color: 'var(--color-text-primary)' }}
        >
          <SparklesIcon />
          AI Outreach Generator
        </h2>
        <p className="text-sm mt-1" style={{ color: 'var(--color-text-tertiary)' }}>
          <span style={{ color: 'var(--color-text-secondary)' }}>{contact.name}</span>
          {' '}• {contact.title} at {account.name}
        </p>
      </div>
      <button
        onClick={onClose}
        className="p-2 rounded-lg transition-colors"
        style={{ color: 'var(--color-text-muted)' }}
        onMouseEnter={(e) => {
          e.currentTarget.style.backgroundColor = 'var(--color-bg-hover)';
          e.currentTarget.style.color = 'var(--color-text-secondary)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = 'transparent';
          e.currentTarget.style.color = 'var(--color-text-muted)';
        }}
      >
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  );
}

function MeddicContextBar({
  contact,
  dataQuality
}: {
  contact: Contact;
  dataQuality: DataQuality;
}) {
  const hasRoleTier = !!contact.role_tier;
  const roleTierDisplay = hasRoleTier ? contact.role_tier : 'unknown';
  const championLevel = contact.champion_potential_level || 'Not assessed';
  const whyPrioritize = contact.why_prioritize || [];
  const recommendedApproach = contact.recommended_approach || '';

  const qualityColors = {
    excellent: { bg: 'var(--color-priority-very-high-bg)', color: 'var(--color-priority-very-high)' },
    good: { bg: 'var(--color-priority-high-bg)', color: 'var(--color-priority-high)' },
    fair: { bg: 'var(--color-priority-medium-bg)', color: 'var(--color-priority-medium)' },
    sparse: { bg: 'var(--color-priority-low-bg)', color: 'var(--color-priority-low)' },
  };

  const roleColors: Record<string, { bg: string; color: string }> = {
    entry_point: { bg: 'var(--color-priority-high-bg)', color: 'var(--color-priority-high)' },
    middle_decider: { bg: 'var(--color-priority-medium-bg)', color: 'var(--color-priority-medium)' },
    economic_buyer: { bg: 'var(--color-accent-primary-muted)', color: 'var(--color-accent-primary)' },
    unknown: { bg: 'var(--color-bg-card)', color: 'var(--color-text-muted)' },
  };

  const championColors: Record<string, { bg: string; color: string }> = {
    'Very High': { bg: 'var(--color-priority-very-high-bg)', color: 'var(--color-priority-very-high)' },
    'High': { bg: 'var(--color-priority-high-bg)', color: 'var(--color-priority-high)' },
    'Medium': { bg: 'var(--color-priority-medium-bg)', color: 'var(--color-priority-medium)' },
    'Low': { bg: 'var(--color-priority-low-bg)', color: 'var(--color-priority-low)' },
    'Not assessed': { bg: 'var(--color-bg-card)', color: 'var(--color-text-muted)' },
  };

  const qColors = qualityColors[dataQuality.level];
  const rColors = roleColors[roleTierDisplay] || roleColors.unknown;
  const cColors = championColors[championLevel] || championColors['Not assessed'];

  return (
    <div
      className="px-5 py-3"
      style={{
        backgroundColor: dataQuality.level === 'sparse' ? 'var(--color-priority-low-bg)' : 'var(--color-bg-card)',
        borderBottom: '1px solid var(--color-border-subtle)'
      }}
    >
      <div className="flex items-center gap-4 flex-wrap">
        <div className="flex items-center gap-2">
          <span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>Role:</span>
          <span
            className="px-2 py-0.5 rounded text-xs font-medium"
            style={{ backgroundColor: rColors.bg, color: rColors.color }}
          >
            {!hasRoleTier ? 'Not Classified' : roleTierDisplay.replace('_', ' ')}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>Champion:</span>
          <span
            className="px-2 py-0.5 rounded text-xs font-medium"
            style={{ backgroundColor: cColors.bg, color: cColors.color }}
          >
            {championLevel}
          </span>
        </div>

        <div className="flex items-center gap-2 ml-auto">
          <span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>Data Quality:</span>
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 rounded-full" style={{ backgroundColor: qColors.color }} />
            <span className="text-xs font-medium capitalize" style={{ color: qColors.color }}>
              {dataQuality.level}
            </span>
            <span className="text-xs font-data" style={{ color: 'var(--color-text-muted)' }}>
              ({dataQuality.score}%)
            </span>
          </div>
        </div>
      </div>

      {(whyPrioritize.length > 0 || recommendedApproach) && (
        <div className="mt-2 pt-2" style={{ borderTop: '1px solid var(--color-border-subtle)' }}>
          {whyPrioritize.length > 0 && (
            <p className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>
              <span style={{ color: 'var(--color-text-muted)' }}>Why prioritize: </span>
              {whyPrioritize[0]}
            </p>
          )}
          {recommendedApproach && (
            <p className="text-xs mt-1" style={{ color: 'var(--color-text-secondary)' }}>
              <span style={{ color: 'var(--color-text-muted)' }}>Approach: </span>
              {recommendedApproach}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

function DataSourcesBar({
  personalizationData,
  showDataSources,
  onToggle
}: {
  personalizationData: ReturnType<typeof getPersonalizationData>;
  showDataSources: boolean;
  onToggle: () => void;
}) {
  const usedCount = personalizationData.dataPoints.filter(d => d.used).length;

  return (
    <div style={{ borderBottom: '1px solid var(--color-border-subtle)' }}>
      <button
        onClick={onToggle}
        className="w-full px-5 py-3 flex items-center justify-between transition-colors"
        style={{ backgroundColor: showDataSources ? 'var(--color-bg-card)' : 'transparent' }}
      >
        <div className="flex items-center gap-2">
          <svg className="w-4 h-4" style={{ color: 'var(--color-accent-primary)' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span className="text-sm" style={{ color: 'var(--color-text-secondary)' }}>
            Intelligence:{' '}
            <span style={{ color: 'var(--color-accent-primary)' }}>{usedCount} data points</span>
            {' will be used for personalization'}
          </span>
        </div>
        <svg
          className="w-4 h-4 transition-transform"
          style={{ color: 'var(--color-text-muted)', transform: showDataSources ? 'rotate(180deg)' : 'rotate(0deg)' }}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {showDataSources && (
        <div className="px-5 py-4 grid grid-cols-3 gap-3" style={{ backgroundColor: 'var(--color-bg-card)' }}>
          {personalizationData.dataPoints.map((dp, i) => (
            <div key={i} className="flex items-start gap-2 text-xs" style={{ opacity: dp.used ? 1 : 0.5 }}>
              <span
                className="mt-0.5 w-4 h-4 rounded flex items-center justify-center flex-shrink-0"
                style={{
                  backgroundColor: dp.used ? 'var(--color-priority-very-high-bg)' : 'var(--color-bg-elevated)',
                  color: dp.used ? 'var(--color-priority-very-high)' : 'var(--color-text-muted)'
                }}
              >
                {dp.used ? '✓' : '–'}
              </span>
              <div>
                <div style={{ color: 'var(--color-text-muted)' }}>{dp.label}</div>
                <div style={{ color: dp.used ? 'var(--color-text-primary)' : 'var(--color-text-muted)' }}>{dp.value}</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function ControlsBar({
  activeTab,
  setActiveTab,
  tone,
  setTone,
}: {
  activeTab: TabType;
  setActiveTab: (tab: TabType) => void;
  tone: OutreachTone;
  setTone: (tone: OutreachTone) => void;
}) {
  const tabs: { key: TabType; label: string; icon: ReactNode }[] = [
    {
      key: 'email',
      label: 'Email',
      icon: <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>,
    },
    {
      key: 'linkedin',
      label: 'LinkedIn',
      icon: <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>,
    },
    {
      key: 'sequence',
      label: 'Follow-up Sequence',
      icon: <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" /></svg>,
    },
  ];

  const tones: { key: OutreachTone; label: string }[] = [
    { key: 'professional', label: 'Formal' },
    { key: 'conversational', label: 'Friendly' },
    { key: 'direct', label: 'Direct' },
  ];

  return (
    <div
      className="px-5 py-3 flex items-center justify-between gap-4 flex-wrap"
      style={{ backgroundColor: 'var(--color-bg-base)', borderBottom: '1px solid var(--color-border-subtle)' }}
    >
      <div className="flex gap-1">
        {tabs.map(tab => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className="flex items-center gap-2 px-3 py-1.5 rounded-md text-sm font-medium transition-all"
            style={{
              backgroundColor: activeTab === tab.key ? 'var(--color-accent-primary-muted)' : 'transparent',
              color: activeTab === tab.key ? 'var(--color-accent-primary)' : 'var(--color-text-tertiary)',
              border: activeTab === tab.key ? '1px solid var(--color-accent-primary)' : '1px solid transparent',
            }}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </div>

      <div className="flex items-center gap-2">
        <span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>Tone:</span>
        <div className="flex gap-1">
          {tones.map(t => (
            <button
              key={t.key}
              onClick={() => setTone(t.key)}
              className="px-2 py-1 rounded text-xs font-medium transition-all"
              style={{
                backgroundColor: tone === t.key ? 'var(--color-priority-high-bg)' : 'transparent',
                color: tone === t.key ? 'var(--color-priority-high)' : 'var(--color-text-tertiary)',
                border: tone === t.key ? '1px solid var(--color-priority-high-border)' : '1px solid var(--color-border-subtle)',
              }}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// Email Content
// ============================================================================

function EmailContent({
  aiEmail,
  templateEmail,
  generationStatus,
  displayedText,
  isTyping
}: {
  aiEmail: AIGeneratedEmail | null;
  templateEmail: GeneratedOutreach;
  generationStatus: GenerationStatus;
  displayedText: string;
  isTyping: boolean;
}) {
  const useAI = aiEmail && generationStatus === 'success';
  const subject = useAI ? aiEmail.subject : templateEmail.subject;
  const body = useAI ? displayedText : templateEmail.fullMessage;

  return (
    <div className="space-y-5">
      {/* Status indicator */}
      {generationStatus === 'success' && (
        <div
          className="flex items-center gap-2 px-4 py-2 rounded-lg"
          style={{ backgroundColor: 'var(--color-priority-very-high-bg)', border: '1px solid var(--color-priority-very-high-border)' }}
        >
          <SparklesIcon />
          <span className="text-sm font-medium" style={{ color: 'var(--color-priority-very-high)' }}>
            AI-Generated Content
          </span>
          {isTyping && <span className="animate-pulse">|</span>}
        </div>
      )}

      {/* Subject Line */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="section-header">Subject Line</label>
          <CopyButton text={subject} label="Copy" size="sm" />
        </div>
        <div
          className="p-3 rounded-lg font-medium text-sm"
          style={{
            backgroundColor: 'var(--color-bg-card)',
            border: '1px solid var(--color-border-default)',
            color: 'var(--color-text-primary)'
          }}
        >
          {subject}
        </div>
      </div>

      {/* Full Message */}
      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="section-header">Message Body</label>
          <CopyButton text={useAI ? `${aiEmail.opening}\n\n${aiEmail.valueHook}\n\n${aiEmail.callToAction}\n\n${aiEmail.ps || ''}` : templateEmail.fullMessage} label="Copy Message" size="sm" />
        </div>
        <div
          className="p-4 rounded-lg whitespace-pre-wrap text-sm leading-relaxed min-h-[300px]"
          style={{
            backgroundColor: 'var(--color-bg-card)',
            border: '1px solid var(--color-border-default)',
            color: 'var(--color-text-secondary)'
          }}
        >
          {generationStatus === 'generating' ? (
            <div className="flex items-center gap-2" style={{ color: 'var(--color-text-muted)' }}>
              <LoadingSpinner />
              <span>Crafting personalized message based on role tier and account intelligence...</span>
            </div>
          ) : (
            <>
              {body}
              {isTyping && <span className="animate-pulse ml-1 inline-block w-2 h-4" style={{ backgroundColor: 'var(--color-accent-primary)' }} />}
            </>
          )}
        </div>
        <p className="mt-2 text-xs" style={{ color: 'var(--color-text-muted)' }}>
          {useAI ? 'AI-personalized based on contact role, triggers, and account data' : 'Template-based • Click Generate for AI-powered personalization'}
        </p>
      </div>
    </div>
  );
}

// ============================================================================
// LinkedIn Content
// ============================================================================

function LinkedInContent({
  aiLinkedIn,
  templateMessage,
  generationStatus,
  displayedText,
  isTyping
}: {
  aiLinkedIn: AIGeneratedLinkedIn | null;
  templateMessage: string;
  generationStatus: GenerationStatus;
  displayedText: string;
  isTyping: boolean;
}) {
  const useAI = aiLinkedIn && generationStatus === 'success';
  const message = useAI ? displayedText : templateMessage;
  const charCount = message.length;
  const isOverLimit = charCount > 300;

  return (
    <div className="space-y-4">
      {generationStatus === 'success' && (
        <div
          className="flex items-center gap-2 px-4 py-2 rounded-lg"
          style={{ backgroundColor: 'var(--color-priority-very-high-bg)', border: '1px solid var(--color-priority-very-high-border)' }}
        >
          <SparklesIcon />
          <span className="text-sm font-medium" style={{ color: 'var(--color-priority-very-high)' }}>
            AI-Generated Content
          </span>
        </div>
      )}

      <div>
        <div className="flex items-center justify-between mb-2">
          <label className="section-header">Connection Request Message</label>
          <CopyButton text={useAI ? aiLinkedIn.connectionRequest : templateMessage} label="Copy" size="sm" />
        </div>

        <div
          className="p-4 rounded-lg whitespace-pre-wrap text-sm leading-relaxed"
          style={{
            backgroundColor: 'var(--color-bg-card)',
            border: `1px solid ${isOverLimit ? 'var(--color-target-hot-border)' : 'var(--color-border-default)'}`,
            color: 'var(--color-text-secondary)'
          }}
        >
          {generationStatus === 'generating' ? (
            <div className="flex items-center gap-2" style={{ color: 'var(--color-text-muted)' }}>
              <LoadingSpinner />
              <span>Crafting concise connection message...</span>
            </div>
          ) : (
            <>
              {message}
              {isTyping && <span className="animate-pulse ml-1 inline-block w-2 h-4" style={{ backgroundColor: 'var(--color-accent-primary)' }} />}
            </>
          )}
        </div>

        <div className="mt-2 flex items-center justify-between">
          <div className="h-1 flex-1 rounded-full overflow-hidden mr-4" style={{ backgroundColor: 'var(--color-bg-card)' }}>
            <div
              className="h-full transition-all"
              style={{
                width: `${Math.min(100, (charCount / 300) * 100)}%`,
                backgroundColor: isOverLimit ? 'var(--color-target-hot)' : charCount > 250 ? 'var(--color-priority-medium)' : 'var(--color-priority-very-high)'
              }}
            />
          </div>
          <span className="text-xs font-data" style={{ color: isOverLimit ? 'var(--color-target-hot)' : 'var(--color-text-muted)' }}>
            {charCount}/300
          </span>
        </div>
      </div>

      {/* Follow-up message for AI */}
      {useAI && aiLinkedIn.followUpMessage && (
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="section-header">Follow-up After Accept</label>
            <CopyButton text={aiLinkedIn.followUpMessage} label="Copy" size="sm" />
          </div>
          <div
            className="p-4 rounded-lg whitespace-pre-wrap text-sm leading-relaxed"
            style={{
              backgroundColor: 'var(--color-bg-card)',
              border: '1px solid var(--color-border-default)',
              color: 'var(--color-text-secondary)'
            }}
          >
            {aiLinkedIn.followUpMessage}
          </div>
        </div>
      )}
    </div>
  );
}

// ============================================================================
// Sequence Content
// ============================================================================

function SequenceContent({
  aiSequence,
  templateSequence,
  generationStatus,
}: {
  aiSequence: AIGeneratedSequence | null;
  templateSequence: FollowUpEmail[];
  generationStatus: GenerationStatus;
  displayedText?: string;
  isTyping?: boolean;
}) {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);
  const useAI = !!(aiSequence && generationStatus === 'success');

  const sequenceItems = useAI
    ? [
        { dayAfter: 1, subject: aiSequence.day1.subject, body: aiSequence.day1.body, purpose: 'Initial personalized touch' },
        { dayAfter: 3, subject: aiSequence.day3.subject, body: aiSequence.day3.body, purpose: 'Value-add follow-up' },
        { dayAfter: 7, subject: aiSequence.day7.subject, body: aiSequence.day7.body, purpose: 'Check-in with alternatives' },
        { dayAfter: 14, subject: aiSequence.day14.subject, body: aiSequence.day14.body, purpose: 'Graceful close' },
      ]
    : templateSequence;

  return (
    <div className="space-y-4">
      {generationStatus === 'success' && (
        <div
          className="flex items-center gap-2 px-4 py-2 rounded-lg"
          style={{ backgroundColor: 'var(--color-priority-very-high-bg)', border: '1px solid var(--color-priority-very-high-border)' }}
        >
          <SparklesIcon />
          <span className="text-sm font-medium" style={{ color: 'var(--color-priority-very-high)' }}>
            AI-Generated 4-Touch Sequence
          </span>
        </div>
      )}

      <div className="flex items-center justify-between mb-2">
        <div>
          <h3 className="text-base font-semibold" style={{ color: 'var(--color-text-primary)' }}>
            {useAI ? '4-Touch AI Sequence' : '3-Touch Follow-up Sequence'}
          </h3>
          <p className="text-xs mt-1" style={{ color: 'var(--color-text-muted)' }}>
            {useAI ? 'AI-crafted progression building on each touch' : 'Template-based cadence'}
          </p>
        </div>
      </div>

      {generationStatus === 'generating' ? (
        <div
          className="p-6 rounded-lg flex items-center justify-center gap-3"
          style={{ backgroundColor: 'var(--color-bg-card)', border: '1px solid var(--color-border-default)' }}
        >
          <LoadingSpinner />
          <span style={{ color: 'var(--color-text-muted)' }}>Generating personalized email sequence...</span>
        </div>
      ) : (
        <div className="space-y-3">
          {sequenceItems.map((email, index) => (
            <SequenceEmail
              key={index}
              email={email}
              index={index}
              isExpanded={expandedIndex === index}
              onToggle={() => setExpandedIndex(expandedIndex === index ? null : index)}
              isAI={useAI}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function SequenceEmail({
  email,
  index,
  isExpanded,
  onToggle,
  isAI
}: {
  email: { dayAfter: number; subject: string; body: string; purpose: string };
  index: number;
  isExpanded: boolean;
  onToggle: () => void;
  isAI: boolean;
}) {
  return (
    <div
      className="rounded-lg overflow-hidden"
      style={{
        backgroundColor: 'var(--color-bg-card)',
        border: isAI ? '1px solid var(--color-accent-primary-muted)' : '1px solid var(--color-border-default)',
      }}
    >
      <button onClick={onToggle} className="w-full p-4 flex items-center justify-between text-left">
        <div className="flex items-center gap-4">
          <div
            className="w-8 h-8 rounded-full flex items-center justify-center font-data font-semibold text-sm"
            style={{
              backgroundColor: isAI ? 'var(--color-accent-primary-muted)' : 'var(--color-bg-elevated)',
              color: isAI ? 'var(--color-accent-primary)' : 'var(--color-text-tertiary)',
            }}
          >
            {index + 1}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span
                className="text-xs px-2 py-0.5 rounded"
                style={{ backgroundColor: 'var(--color-priority-medium-bg)', color: 'var(--color-priority-medium)' }}
              >
                Day {email.dayAfter}
              </span>
              <span className="text-sm font-medium" style={{ color: 'var(--color-text-primary)' }}>
                {email.subject}
              </span>
            </div>
            <p className="text-xs mt-0.5" style={{ color: 'var(--color-text-muted)' }}>
              {email.purpose}
            </p>
          </div>
        </div>
        <svg
          className="w-4 h-4 transition-transform"
          style={{ color: 'var(--color-text-muted)', transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)' }}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isExpanded && (
        <div className="px-4 pb-4 pt-0" style={{ borderTop: '1px solid var(--color-border-subtle)' }}>
          <div className="flex justify-end mb-2 pt-3">
            <CopyButton text={`Subject: ${email.subject}\n\n${email.body}`} label="Copy Email" size="sm" />
          </div>
          <div
            className="p-3 rounded-lg whitespace-pre-wrap text-sm leading-relaxed"
            style={{ backgroundColor: 'var(--color-bg-elevated)', color: 'var(--color-text-secondary)' }}
          >
            {email.body}
          </div>
        </div>
      )}
    </div>
  );
}
