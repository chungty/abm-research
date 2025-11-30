import type { Contact, Account, RoleTier } from '../types';

// ============================================================================
// Types
// ============================================================================

export type OutreachTone = 'professional' | 'conversational' | 'direct';
export type OutreachVariant = 'value_led' | 'pain_led' | 'social_proof';

export interface OutreachContext {
  contact: Contact;
  account: Account;
  tone?: OutreachTone;
  variant?: OutreachVariant;
}

export interface GeneratedOutreach {
  subject: string;
  opening: string;
  valueHook: string;
  callToAction: string;
  fullMessage: string;
  variant: OutreachVariant;
}

export interface OutreachVariants {
  value_led: GeneratedOutreach;
  pain_led: GeneratedOutreach;
  social_proof: GeneratedOutreach;
}

export interface PersonalizationData {
  sources: string[];
  dataPoints: { label: string; value: string; used: boolean }[];
}

export interface FollowUpEmail {
  dayAfter: number;
  subject: string;
  body: string;
  purpose: string;
}

// ============================================================================
// Configuration
// ============================================================================

const roleMessaging: Record<RoleTier, {
  painPoint: string;
  valueAngle: string;
  ctaStyle: string;
  formalTitle: string;
}> = {
  entry_point: {
    painPoint: 'day-to-day operational challenges',
    valueAngle: 'technical efficiency and visibility',
    ctaStyle: '15-minute technical walkthrough',
    formalTitle: 'technical leaders',
  },
  middle_decider: {
    painPoint: 'tooling gaps and process inefficiencies',
    valueAngle: 'operational control and team productivity',
    ctaStyle: 'solution overview call',
    formalTitle: 'operations leaders',
  },
  economic_buyer: {
    painPoint: 'cost optimization and risk management',
    valueAngle: 'ROI, uptime guarantees, and strategic alignment',
    ctaStyle: 'executive briefing',
    formalTitle: 'executive leadership',
  },
};

const toneModifiers: Record<OutreachTone, {
  greeting: (name: string) => string;
  signoff: string;
  ctaPrefix: string;
}> = {
  professional: {
    greeting: (name) => `Dear ${name},`,
    signoff: 'Best regards,',
    ctaPrefix: 'Would you be open to',
  },
  conversational: {
    greeting: (name) => `Hi ${name},`,
    signoff: 'Best,',
    ctaPrefix: 'Would you be up for',
  },
  direct: {
    greeting: (name) => `${name} —`,
    signoff: 'Thanks,',
    ctaPrefix: 'Can we schedule',
  },
};

// ============================================================================
// Main Generation Functions
// ============================================================================

export function generateAllVariants(context: OutreachContext): OutreachVariants {
  const variants: OutreachVariant[] = ['value_led', 'pain_led', 'social_proof'];

  return variants.reduce((acc, variant) => {
    acc[variant] = generateOutreach({ ...context, variant });
    return acc;
  }, {} as OutreachVariants);
}

export function generateOutreach(context: OutreachContext): GeneratedOutreach {
  const { contact, account, tone = 'conversational', variant = 'value_led' } = context;
  // Null-safe role tier lookup with fallback to entry_point (most common)
  const roleTier = contact.role_tier || 'entry_point';
  const roleConfig = roleMessaging[roleTier] || roleMessaging.entry_point;
  const toneConfig = toneModifiers[tone];

  const enrichedData = extractEnrichedData(account, contact);
  const firstName = contact.name.split(' ')[0];

  const subject = buildSubject(contact, account, enrichedData, variant);
  const opening = buildOpening(firstName, account, roleConfig, toneConfig, enrichedData, variant);
  const valueHook = buildValueHook(account, enrichedData, roleConfig, variant);
  const callToAction = buildCTA(contact, roleConfig, toneConfig);
  const fullMessage = assembleMessage(firstName, opening, valueHook, callToAction, toneConfig);

  return {
    subject,
    opening,
    valueHook,
    callToAction,
    fullMessage,
    variant,
  };
}

export function getPersonalizationData(context: OutreachContext): PersonalizationData {
  const { account, contact } = context;
  const sources: string[] = [];
  const dataPoints: PersonalizationData['dataPoints'] = [];

  // Infrastructure data
  const gpuDetected = account.infrastructure_breakdown?.breakdown?.gpu_infrastructure?.detected || [];
  dataPoints.push({
    label: 'GPU/AI Infrastructure',
    value: gpuDetected.length > 0 ? gpuDetected.slice(0, 3).join(', ') : 'None detected',
    used: gpuDetected.length > 0,
  });
  if (gpuDetected.length > 0) sources.push('Infrastructure Analysis');

  // Company size
  dataPoints.push({
    label: 'Company Size',
    value: account.employee_count ? `${account.employee_count.toLocaleString()} employees` : 'Unknown',
    used: !!account.employee_count,
  });
  if (account.employee_count) sources.push('Company Data');

  // Partnership classification
  dataPoints.push({
    label: 'Partnership Type',
    value: account.partnership_classification || 'Not classified',
    used: !!account.partnership_classification,
  });
  if (account.partnership_classification) sources.push('Partnership Analysis');

  // Trigger events
  const triggers = account.account_score_breakdown?.buying_signals?.breakdown?.trigger_events?.high_value_triggers || [];
  dataPoints.push({
    label: 'Trigger Events',
    value: triggers.length > 0 ? triggers[0] : 'None detected',
    used: triggers.length > 0,
  });
  if (triggers.length > 0) sources.push('Signal Detection');

  // Contact enrichment
  dataPoints.push({
    label: 'Content Themes',
    value: contact.content_themes?.slice(0, 2).join(', ') || 'Not available',
    used: !!contact.content_themes?.length,
  });
  if (contact.content_themes?.length) sources.push('LinkedIn Enrichment');

  // Role context (null-safe)
  const hasRoleTier = !!contact.role_tier;
  dataPoints.push({
    label: 'Role Tier',
    value: hasRoleTier ? contact.role_tier.replace('_', ' ') : 'unknown',
    used: hasRoleTier,
  });
  if (hasRoleTier) sources.push('MEDDIC Analysis');

  // Champion potential
  dataPoints.push({
    label: 'Champion Potential',
    value: contact.champion_potential_level || 'Not assessed',
    used: !!contact.champion_potential_level && contact.champion_potential_level !== 'Low',
  });

  // Why prioritize (from MEDDIC)
  const whyPrioritize = contact.why_prioritize || [];
  dataPoints.push({
    label: 'Prioritization Reason',
    value: whyPrioritize.length > 0 ? whyPrioritize[0] : 'Not assessed',
    used: whyPrioritize.length > 0,
  });

  // Recommended approach
  dataPoints.push({
    label: 'Recommended Approach',
    value: contact.recommended_approach || 'Not available',
    used: !!contact.recommended_approach,
  });

  return { sources: [...new Set(sources)], dataPoints };
}

// Data quality assessment for sparse data UI
export interface DataQuality {
  score: number; // 0-100
  level: 'excellent' | 'good' | 'fair' | 'sparse';
  missingFields: string[];
  recommendations: string[];
}

export function assessDataQuality(context: OutreachContext): DataQuality {
  const { contact, account } = context;
  const missingFields: string[] = [];
  const recommendations: string[] = [];
  let score = 0;

  // Check critical fields (weighted)
  if (contact.role_tier) {
    score += 25;
  } else {
    missingFields.push('Role Tier');
    recommendations.push('Rescore contact to classify role tier');
  }

  if (contact.champion_potential_level && contact.champion_potential_level !== 'Low') {
    score += 20;
  } else if (!contact.champion_potential_level) {
    missingFields.push('Champion Potential');
    recommendations.push('Rescore to assess champion potential');
  }

  if (contact.why_prioritize && contact.why_prioritize.length > 0) {
    score += 15;
  } else {
    missingFields.push('Prioritization Reasons');
  }

  // Check account data
  const gpuDetected = account.infrastructure_breakdown?.breakdown?.gpu_infrastructure?.detected || [];
  if (gpuDetected.length > 0) {
    score += 15;
  } else {
    missingFields.push('Infrastructure Detection');
  }

  if (account.partnership_classification) {
    score += 10;
  } else {
    missingFields.push('Partnership Classification');
  }

  if (account.employee_count) {
    score += 5;
  }

  const triggers = account.account_score_breakdown?.buying_signals?.breakdown?.trigger_events?.high_value_triggers || [];
  if (triggers.length > 0) {
    score += 10;
  } else {
    missingFields.push('Trigger Events');
  }

  // Determine level
  let level: DataQuality['level'];
  if (score >= 80) level = 'excellent';
  else if (score >= 60) level = 'good';
  else if (score >= 40) level = 'fair';
  else level = 'sparse';

  // Add general recommendation for sparse data
  if (level === 'sparse') {
    recommendations.push('Consider enriching this account to improve outreach quality');
  }

  return { score, level, missingFields, recommendations };
}

export function generateFollowUpSequence(context: OutreachContext): FollowUpEmail[] {
  const { contact, account } = context;
  const firstName = contact.name.split(' ')[0];
  const companyName = account.name;
  const enrichedData = extractEnrichedData(account, contact);

  return [
    {
      dayAfter: 3,
      subject: `Re: ${companyName} infrastructure`,
      body: `Hi ${firstName},

Wanted to follow up on my previous note. I know you're busy, so I'll keep this brief.

${enrichedData.hasGpu
  ? `Given your AI/GPU infrastructure investments, I thought you might find value in how we've helped similar teams reduce power costs by 15-20% while maintaining compute density.`
  : `I came across some recent work Verdigris has done with companies at ${companyName}'s scale that might be relevant to your infrastructure challenges.`}

Happy to share a quick case study if helpful - no call required.

Best,
[Your Name]`,
      purpose: 'Value-add follow-up with case study offer',
    },
    {
      dayAfter: 7,
      subject: `Quick question, ${firstName}`,
      body: `Hi ${firstName},

I've reached out a couple times and want to be respectful of your time.

Quick question: Is infrastructure monitoring/optimization something ${companyName} is actively looking at, or should I check back in a few months?

Either way, happy to help if questions come up.

Best,
[Your Name]`,
      purpose: 'Polite break-up email to prompt response',
    },
    {
      dayAfter: 14,
      subject: `${companyName} + Verdigris - closing the loop`,
      body: `Hi ${firstName},

Last note from me for now.

If datacenter monitoring and optimization becomes a priority, feel free to reach out anytime. I'll keep an eye on ${companyName}'s growth and may circle back when timing seems better.

${enrichedData.partnershipType
  ? `PS: Given your ${enrichedData.partnershipType.toLowerCase()} position in the market, we'd be especially interested in exploring partnership opportunities down the line.`
  : `In the meantime, happy to connect on LinkedIn if you'd like to stay in touch.`}

Best,
[Your Name]`,
      purpose: 'Graceful close with door open for future',
    },
  ];
}

export function generateLinkedInMessage(context: OutreachContext): string {
  const { contact, account, tone = 'conversational' } = context;
  const firstName = contact.name.split(' ')[0];
  const enrichedData = extractEnrichedData(account, contact);
  const roleTier = contact.role_tier || 'entry_point';

  // LinkedIn connection requests have 300 char limit - be concise
  if (enrichedData.hasGpu) {
    return `Hi ${firstName} - noticed ${account.name}'s GPU/AI infrastructure work. We help datacenter teams optimize power and cooling for high-density compute. Would love to connect and share what we're seeing in the space.`;
  }

  if (roleTier === 'economic_buyer') {
    return `Hi ${firstName} - ${account.name} fits the profile of organizations we work with on datacenter efficiency. Would be great to connect and learn about your infrastructure priorities.`;
  }

  if (enrichedData.partnershipType) {
    return `Hi ${firstName} - saw ${account.name}'s work as a ${enrichedData.partnershipType.toLowerCase()}. We work with similar organizations on datacenter monitoring. Would love to connect.`;
  }

  if (tone === 'direct') {
    return `${firstName} - reaching out because ${account.name} matches our ICP for datacenter monitoring solutions. Quick connect to see if there's fit?`;
  }

  return `Hi ${firstName} - came across your profile while researching ${account.name}. We help datacenter teams with real-time infrastructure visibility. Would be great to connect.`;
}

// ============================================================================
// Helper Functions
// ============================================================================

interface EnrichedData {
  hasGpu: boolean;
  gpuVendors: string[];
  employeeCount: number | null;
  sizeCategory: string;
  triggerEvent: string | null;
  partnershipType: string | null;
  detectedInfra: string[];
  contentThemes: string[];
}

function extractEnrichedData(account: Account, contact: Contact): EnrichedData {
  const breakdown = account.infrastructure_breakdown?.breakdown;
  const gpuDetected = breakdown?.gpu_infrastructure?.detected || [];
  const triggers = account.account_score_breakdown?.buying_signals?.breakdown?.trigger_events?.high_value_triggers || [];

  // Collect all detected infrastructure
  const detectedInfra: string[] = [];
  if (breakdown) {
    Object.entries(breakdown).forEach(([category, data]) => {
      if (data.detected?.length > 0) {
        detectedInfra.push(category);
      }
    });
  }

  // Determine company size category
  const emp = account.employee_count;
  let sizeCategory = 'mid-sized';
  if (emp && emp > 10000) sizeCategory = 'enterprise';
  else if (emp && emp > 1000) sizeCategory = 'large';
  else if (emp && emp < 200) sizeCategory = 'growing';

  return {
    hasGpu: gpuDetected.length > 0,
    gpuVendors: gpuDetected,
    employeeCount: account.employee_count || null,
    sizeCategory,
    triggerEvent: triggers.length > 0 ? triggers[0] : null,
    partnershipType: account.partnership_classification || null,
    detectedInfra,
    contentThemes: contact.content_themes || [],
  };
}

function buildSubject(
  contact: Contact,
  account: Account,
  data: EnrichedData,
  variant: OutreachVariant
): string {
  const firstName = contact.name.split(' ')[0];

  // Variant-specific subjects
  if (variant === 'pain_led') {
    if (data.hasGpu) return `${firstName} - GPU density challenges at ${account.name}?`;
    return `${firstName} - infrastructure visibility at ${account.name}`;
  }

  if (variant === 'social_proof') {
    if (data.sizeCategory === 'enterprise') {
      return `How ${data.sizeCategory} datacenter teams are reducing power costs`;
    }
    return `${account.name} + Verdigris - quick question`;
  }

  // Value-led (default)
  if (data.hasGpu) {
    const vendor = data.gpuVendors[0]?.split(' ')[0] || 'GPU';
    return `${firstName} - ${vendor} infrastructure optimization at ${account.name}`;
  }

  if (data.triggerEvent) {
    return `${firstName} - congrats on ${account.name}'s growth`;
  }

  if (contact.role_tier === 'economic_buyer') {
    return `${account.name} datacenter efficiency - strategic question`;
  }

  return `${firstName} - infrastructure visibility for ${account.name}`;
}

function buildOpening(
  firstName: string,
  account: Account,
  roleConfig: typeof roleMessaging.entry_point,
  toneConfig: typeof toneModifiers.professional,
  data: EnrichedData,
  variant: OutreachVariant
): string {
  const greeting = toneConfig.greeting(firstName);
  const companyName = account.name;

  // Pain-led variant
  if (variant === 'pain_led') {
    if (data.hasGpu) {
      return `${greeting}\n\nManaging GPU density at scale is one of the hardest infrastructure challenges - thermal management, power distribution, and uptime all competing for attention. I imagine ${companyName}'s ${roleConfig.formalTitle} deal with this constantly.`;
    }
    return `${greeting}\n\nAs datacenter infrastructure scales, ${roleConfig.painPoint} often become the bottleneck. Wanted to reach out because ${companyName} seems to be at that inflection point.`;
  }

  // Social proof variant
  if (variant === 'social_proof') {
    return `${greeting}\n\nWe recently helped a ${data.sizeCategory} datacenter operation similar to ${companyName} reduce their power monitoring blind spots by 40%. Given your role, thought this might resonate.`;
  }

  // Value-led variant (default)
  if (data.triggerEvent) {
    return `${greeting}\n\nI noticed ${companyName} recently ${data.triggerEvent.toLowerCase()}. Congrats - that kind of growth creates both opportunities and infrastructure complexity to navigate.`;
  }

  if (data.partnershipType) {
    return `${greeting}\n\nI've been following ${companyName}'s work as a ${data.partnershipType.toLowerCase()} in the datacenter space. Your infrastructure expertise is impressive - wanted to introduce a tool that might complement what you're doing.`;
  }

  if (data.hasGpu) {
    const vendorMention = data.gpuVendors.length > 0
      ? `(noticed the ${data.gpuVendors[0]} deployment)`
      : '';
    return `${greeting}\n\nI came across ${companyName}'s AI/GPU infrastructure work ${vendorMention} and wanted to reach out. As someone focused on ${roleConfig.valueAngle}, I thought you'd appreciate how we're helping similar teams.`;
  }

  return `${greeting}\n\nI've been researching datacenter operations at ${data.sizeCategory} organizations like ${companyName}. Given your role, wanted to share how we're helping ${roleConfig.formalTitle} tackle ${roleConfig.painPoint}.`;
}

function buildValueHook(
  account: Account,
  data: EnrichedData,
  roleConfig: typeof roleMessaging.entry_point,
  variant: OutreachVariant
): string {
  const companyName = account.name;

  // Pain-led focuses on solving the problem
  if (variant === 'pain_led') {
    if (data.hasGpu) {
      return `Verdigris gives datacenter teams real-time visibility into power and environmental conditions at the rack level. For GPU-dense environments, this means catching thermal issues before they cause throttling or downtime - without adding another dashboard to monitor.`;
    }
    return `Verdigris provides real-time power and environmental monitoring that plugs directly into your existing infrastructure. No rip-and-replace - just better signal on what's actually happening in your facility.`;
  }

  // Social proof focuses on results
  if (variant === 'social_proof') {
    const sizeSpecific = data.sizeCategory === 'enterprise'
      ? 'enterprise datacenter teams'
      : `${data.sizeCategory} organizations`;
    return `We work with ${sizeSpecific} to provide real-time infrastructure visibility. Common outcomes include 15-20% reduction in power waste, 30% faster incident response, and better capacity planning data.`;
  }

  // Value-led (default) - customized to their infrastructure
  if (data.hasGpu) {
    return `Verdigris provides real-time power and environmental monitoring specifically designed for high-density compute environments. For teams like ${companyName}'s, this translates to:\n\n• Thermal visibility at the rack level (catch hotspots before they cause throttling)\n• Power distribution insights (optimize for GPU density without overloading circuits)\n• Predictive alerts (know about issues before they impact uptime)`;
  }

  if (data.detectedInfra.includes('power_systems')) {
    return `Given ${companyName}'s power infrastructure, real-time monitoring can unlock significant efficiency gains. Verdigris helps teams:\n\n• Identify power waste and ghost loads\n• Balance distribution for better reliability\n• Generate compliance-ready reporting automatically`;
  }

  if (data.detectedInfra.includes('cooling_systems')) {
    return `With your cooling systems running at scale, visibility into thermal patterns becomes critical. Verdigris provides:\n\n• Real-time environmental monitoring (temperature, humidity, airflow)\n• Correlation between power and thermal events\n• Automated alerting before conditions impact equipment`;
  }

  return `Verdigris helps datacenter teams like ${companyName}'s get ${roleConfig.valueAngle} through real-time power and environmental monitoring. This typically means faster troubleshooting, better capacity planning, and fewer surprises.`;
}

function buildCTA(
  contact: Contact,
  roleConfig: typeof roleMessaging.entry_point,
  toneConfig: typeof toneModifiers.professional
): string {
  const ctaBase = roleConfig.ctaStyle;

  if (contact.role_tier === 'entry_point') {
    return `${toneConfig.ctaPrefix} a ${ctaBase}? I can show you exactly how we'd work with your current setup - takes about 15 minutes and no prep needed on your end.`;
  }

  if (contact.role_tier === 'economic_buyer') {
    return `${toneConfig.ctaPrefix} a brief ${ctaBase}? Happy to share how similar organizations have approached this and what ROI they've seen.`;
  }

  return `${toneConfig.ctaPrefix} a ${ctaBase}? I'd like to understand your current priorities and see if there's a fit worth exploring.`;
}

function assembleMessage(
  firstName: string,
  opening: string,
  valueHook: string,
  callToAction: string,
  toneConfig: typeof toneModifiers.professional
): string {
  const ps = generatePS(firstName, toneConfig);

  return `${opening}

${valueHook}

${callToAction}

${toneConfig.signoff}
[Your Name]

${ps}`;
}

function generatePS(firstName: string, toneConfig: typeof toneModifiers.professional): string {
  // Rotate through different PS options for variety
  const psOptions = [
    `P.S. ${firstName}, if timing isn't right now, happy to share some resources on datacenter monitoring trends we're tracking.`,
    `P.S. No pressure either way - if you'd prefer I just send over a one-pager instead, let me know.`,
    `P.S. Even if Verdigris isn't the right fit, happy to connect and swap notes on what you're seeing in the industry.`,
  ];

  // Use greeting style to pick PS (creates consistency)
  if (toneConfig.signoff === 'Best regards,') return psOptions[1]; // professional
  if (toneConfig.signoff === 'Thanks,') return psOptions[2]; // direct
  return psOptions[0]; // conversational
}
