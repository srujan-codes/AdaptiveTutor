/**
 * useLesson hook — manages lesson generation and retrieval.
 * Implementation: TICKET-018
 */

// TODO: [TICKET-018] Implement useLesson hook
// - generateLesson(topic, difficulty) → lesson data
// - getLesson(lessonId) → lesson data
// - loading, error states

export default function useLesson() {
  return {
    lesson: null,
    loading: false,
    error: null,
    generateLesson: async () => {},
    getLesson: async () => {},
  }
}
