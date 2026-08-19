/* ============================================================
   EDUMIND AI — EVALUATION HOOK (Challenge 1)
   ============================================================ */

import { useCallback } from 'react'
import toast from 'react-hot-toast'
import { useEvaluatorStore } from '@store/evaluatorStore'
import { evaluatorService } from '@services/evaluatorService'
import { validateEvaluatorForm } from '@utils/validators'
import { useTerminalLogs } from './useTerminalLogs'

export function useEvaluation() {
  const {
    question,
    referenceAnswer,
    studentAnswer,
    subject,
    maxScore,
    result,
    isLoading,
    error,
    history,
    setResult,
    setLoading,
    setError,
    clearError,
    resetForm,
    addToHistory,
    getFormData,
  } = useEvaluatorStore()

  const { pushLog } = useTerminalLogs(false)

  // Submit evaluation
  const evaluate = useCallback(async () => {
    clearError()

    const formData = getFormData()

    // Validate
    const { isValid, errors } = validateEvaluatorForm(formData)
    if (!isValid) {
      const firstError = Object.values(errors)[0]
      setError(firstError)
      toast.error(`[ VALIDATION ] ${firstError}`)
      return null
    }

    setLoading(true)
    pushLog('EVAL_ENGINE: Initiating multi-layer evaluation...', 'SYS')

    try {
      toast.loading('[ EVALUATING ] AI analysis in progress...', {
        id: 'eval-toast',
      })

      const data = await evaluatorService.evaluate(formData)

      setResult(data)
      addToHistory({
        ...data,
        question,
        subject,
        timestamp: new Date().toISOString(),
      })

      toast.success('[ COMPLETE ] Evaluation finished', {
        id: 'eval-toast',
      })

      pushLog(
        `EVAL_ENGINE: Score ${data.score}/${maxScore} — ${data.grade}`,
        'OK'
      )

      return data
    } catch (err) {
      const msg =
        err.response?.data?.detail ||
        err.message ||
        'Evaluation failed'
      setError(msg)
      toast.error(`[ ERROR ] ${msg}`, { id: 'eval-toast' })
      pushLog(`EVAL_ENGINE: Error — ${msg}`, 'ERR')
      return null
    } finally {
      setLoading(false)
    }
  }, [
    getFormData,
    clearError,
    setError,
    setLoading,
    setResult,
    addToHistory,
    question,
    subject,
    maxScore,
    pushLog,
  ])

  // Reset everything
  const reset = useCallback(() => {
    resetForm()
    clearError()
  }, [resetForm, clearError])

  return {
    // State
    question,
    referenceAnswer,
    studentAnswer,
    subject,
    maxScore,
    result,
    isLoading,
    error,
    history,

    // Actions
    evaluate,
    reset,
  }
}

export default useEvaluation
