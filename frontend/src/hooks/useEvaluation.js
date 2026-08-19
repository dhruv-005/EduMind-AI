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

    // Show loading toast with long duration (90s)
    toast.loading(
      '[ EVALUATING ] AI analysis in progress... This may take 30-60 seconds.',
      {
        id:       'eval-toast',
        duration: 90000,
      }
    )

    try {
      const data = await evaluatorService.evaluate(formData)

      // Handle both response formats
      const resultData = data?.data || data

      setResult(resultData)
      addToHistory({
        ...resultData,
        question,
        subject,
        timestamp: new Date().toISOString(),
      })

      toast.success(
        `[ COMPLETE ] Score: ${resultData?.score_out_of_10 || resultData?.score || '?'}/10`,
        { id: 'eval-toast' }
      )

      pushLog(
        `EVAL_ENGINE: Score ${resultData?.score_out_of_10 || resultData?.score}/${maxScore} — ${resultData?.grade}`,
        'OK'
      )

      return resultData
    } catch (err) {
      const msg =
        err.code === 'ECONNABORTED'
          ? 'Request timed out — AI is taking too long. Please try again.'
          : err.response?.data?.detail ||
            err.response?.data?.error?.message ||
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

  const reset = useCallback(() => {
    resetForm()
    clearError()
  }, [resetForm, clearError])

  return {
    question,
    referenceAnswer,
    studentAnswer,
    subject,
    maxScore,
    result,
    isLoading,
    error,
    history,
    evaluate,
    reset,
  }
}

export default useEvaluation
