/* ============================================================
   EDUMIND AI — SALES STORE (Challenge 5)
   ============================================================ */

import { create } from 'zustand'

export const LEAD_TIER = {
  HOT: 'HOT',
  WARM: 'WARM',
  COOL: 'COOL',
  COLD: 'COLD',
}

export const useSalesStore = create((set, get) => ({
  // Catalogue
  catalogue: [],
  isCatalogueLoaded: false,
  isUploadingCatalogue: false,

  // Conversation
  messages: [],   // { role: 'user'|'assistant', content, timestamp, products? }
  isTyping: false,
  conversationId: null,

  // Customer profile
  customerProfile: {
    budget: null,
    requirements: [],
    preferences: [],
    objections: [],
    urgency: null,
  },

  // Recommendations
  recommendations: [],
  isLoadingRecommendations: false,

  // Lead score
  leadScore: {
    total: 0,
    tier: LEAD_TIER.COLD,
    breakdown: {
      budget: 0,
      intent: 0,
      authority: 0,
      urgency: 0,
    },
  },

  // Follow-up
  followUpEmail: '',
  followUpWhatsapp: '',
  isGeneratingFollowUp: false,

  // Escalation
  isEscalated: false,
  escalationSummary: '',

  // Error
  error: null,

  // Setters
  setCatalogue: (catalogue) =>
    set({ catalogue, isCatalogueLoaded: true }),
  setIsUploadingCatalogue: (uploading) =>
    set({ isUploadingCatalogue: uploading }),
  setIsTyping: (typing) => set({ isTyping: typing }),
  setConversationId: (id) => set({ conversationId: id }),
  setRecommendations: (recs) => set({ recommendations: recs }),
  setIsLoadingRecommendations: (loading) =>
    set({ isLoadingRecommendations: loading }),
  setLeadScore: (score) => set({ leadScore: score }),
  setFollowUpEmail: (email) => set({ followUpEmail: email }),
  setFollowUpWhatsapp: (wa) => set({ followUpWhatsapp: wa }),
  setIsGeneratingFollowUp: (gen) =>
    set({ isGeneratingFollowUp: gen }),
  setIsEscalated: (esc) => set({ isEscalated: esc }),
  setEscalationSummary: (summary) =>
    set({ escalationSummary: summary }),
  setError: (error) => set({ error }),
  clearError: () => set({ error: null }),

  // Add message
  addMessage: (message) =>
    set((state) => ({
      messages: [
        ...state.messages,
        {
          ...message,
          id: Date.now(),
          timestamp: new Date().toISOString(),
        },
      ],
    })),

  // Update customer profile
  updateCustomerProfile: (updates) =>
    set((state) => ({
      customerProfile: {
        ...state.customerProfile,
        ...updates,
      },
    })),

  // Get lead tier label
  getLeadTierLabel: () => {
    const { total } = get().leadScore
    if (total >= 75) return LEAD_TIER.HOT
    if (total >= 50) return LEAD_TIER.WARM
    if (total >= 25) return LEAD_TIER.COOL
    return LEAD_TIER.COLD
  },

  // Reset conversation
  resetConversation: () =>
    set({
      messages: [],
      conversationId: null,
      customerProfile: {
        budget: null,
        requirements: [],
        preferences: [],
        objections: [],
        urgency: null,
      },
      recommendations: [],
      leadScore: {
        total: 0,
        tier: LEAD_TIER.COLD,
        breakdown: { budget: 0, intent: 0, authority: 0, urgency: 0 },
      },
      followUpEmail: '',
      followUpWhatsapp: '',
      isEscalated: false,
      escalationSummary: '',
      error: null,
    }),
}))
