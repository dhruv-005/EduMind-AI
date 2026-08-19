/* ============================================================
   EDUMIND AI — VOICE TUTOR STORE (Challenge 4)
   ============================================================ */

import { create } from 'zustand'

// VAD States
export const VAD_STATE = {
  IDLE: 'IDLE',
  LISTENING: 'LISTENING',
  PROCESSING: 'PROCESSING',
  SPEAKING: 'SPEAKING',
  ERROR: 'ERROR',
}

export const useVoiceTutorStore = create((set, get) => ({
  // Session
  sessionId: null,
  subject: 'mathematics',
  gradeLevel: 'grade-10',
  isSessionActive: false,

  // VAD / Recording
  vadState: VAD_STATE.IDLE,
  isRecording: false,
  audioLevel: 0,

  // Transcript
  transcript: [],    // { role: 'user'|'tutor', text, timestamp }
  currentTranscript: '',

  // Audio
  isPlaying: false,
  currentAudioUrl: null,

  // WebSocket
  wsConnected: false,
  wsError: null,

  // Stats
  sessionStats: {
    questionsAsked: 0,
    topicsCovered: [],
    sessionDuration: 0,
    startTime: null,
  },

  // Error
  error: null,

  // Setters
  setSessionId: (id) => set({ sessionId: id }),
  setSubject: (subject) => set({ subject }),
  setGradeLevel: (level) => set({ gradeLevel: level }),
  setIsSessionActive: (active) => set({ isSessionActive: active }),
  setVadState: (state) => set({ vadState: state }),
  setIsRecording: (recording) => set({ isRecording: recording }),
  setAudioLevel: (level) => set({ audioLevel: level }),
  setCurrentTranscript: (text) => set({ currentTranscript: text }),
  setIsPlaying: (playing) => set({ isPlaying: playing }),
  setCurrentAudioUrl: (url) => set({ currentAudioUrl: url }),
  setWsConnected: (connected) => set({ wsConnected: connected }),
  setWsError: (error) => set({ wsError: error }),
  setError: (error) => set({ error }),
  clearError: () => set({ error: null }),

  // Add transcript entry
  addTranscript: (entry) =>
    set((state) => ({
      transcript: [
        ...state.transcript,
        {
          ...entry,
          timestamp: new Date().toISOString(),
          id: Date.now(),
        },
      ],
    })),

  // Start session
  startSession: (sessionId) =>
    set({
      sessionId,
      isSessionActive: true,
      transcript: [],
      sessionStats: {
        questionsAsked: 0,
        topicsCovered: [],
        sessionDuration: 0,
        startTime: Date.now(),
      },
    }),

  // End session
  endSession: () =>
    set((state) => ({
      isSessionActive: false,
      vadState: VAD_STATE.IDLE,
      isRecording: false,
      isPlaying: false,
      sessionStats: {
        ...state.sessionStats,
        sessionDuration: state.sessionStats.startTime
          ? Math.floor((Date.now() - state.sessionStats.startTime) / 1000)
          : 0,
      },
    })),

  // Increment questions asked
  incrementQuestions: () =>
    set((state) => ({
      sessionStats: {
        ...state.sessionStats,
        questionsAsked: state.sessionStats.questionsAsked + 1,
      },
    })),

  // Add topic covered
  addTopic: (topic) =>
    set((state) => ({
      sessionStats: {
        ...state.sessionStats,
        topicsCovered: [
          ...new Set([...state.sessionStats.topicsCovered, topic]),
        ],
      },
    })),

  // Reset
  reset: () =>
    set({
      sessionId: null,
      isSessionActive: false,
      vadState: VAD_STATE.IDLE,
      isRecording: false,
      audioLevel: 0,
      transcript: [],
      currentTranscript: '',
      isPlaying: false,
      currentAudioUrl: null,
      wsConnected: false,
      wsError: null,
      error: null,
      sessionStats: {
        questionsAsked: 0,
        topicsCovered: [],
        sessionDuration: 0,
        startTime: null,
      },
    }),
}))
