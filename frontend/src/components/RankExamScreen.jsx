import { useCallback, useEffect, useRef, useState } from 'react'
import OverlayFrame from './OverlayFrame'
import { submitRankExam } from '../api/rankExam'

function useCountdown(expiresAt) {
  const [secondsLeft, setSecondsLeft] = useState(() => {
    const diff = new Date(expiresAt).getTime() - Date.now()
    return Math.max(0, Math.floor(diff / 1000))
  })

  useEffect(() => {
    if (secondsLeft <= 0) return
    const timer = setInterval(() => {
      setSecondsLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer)
          return 0
        }
        return prev - 1
      })
    }, 1000)
    return () => clearInterval(timer)
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const mm = String(Math.floor(secondsLeft / 60)).padStart(2, '0')
  const ss = String(secondsLeft % 60).padStart(2, '0')
  return { secondsLeft, display: `${mm}:${ss}` }
}

function RankExamScreen({ open, examData, skill, onClose, onResult }) {
  // examData: { attempt_id, from_rank, to_rank, time_limit_minutes, expires_at, questions }
  const { questions = [], attempt_id, from_rank, to_rank, expires_at } = examData || {}

  const [currentIdx, setCurrentIdx] = useState(0)
  const [answers, setAnswers] = useState({}) // { [question_id]: answer_value }
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const autoSubmittedRef = useRef(false)

  const { secondsLeft, display: timerDisplay } = useCountdown(expires_at || new Date(Date.now() + 3600000).toISOString())

  const handleSubmit = useCallback(async () => {
    if (submitting) return
    setSubmitting(true)
    setError('')
    try {
      const payload = Object.entries(answers).map(([qid, val]) => ({
        question_id: parseInt(qid),
        answer_json: val,
      }))
      const result = await submitRankExam(attempt_id, payload)
      onResult(result)
    } catch (err) {
      setError(err.message || 'Submit failed. Please try again.')
      setSubmitting(false)
    }
  }, [attempt_id, answers, submitting, onResult])

  // Auto-submit on timer expiry
  useEffect(() => {
    if (secondsLeft === 0 && !autoSubmittedRef.current && !submitting) {
      autoSubmittedRef.current = true
      handleSubmit()
    }
  }, [secondsLeft, submitting, handleSubmit])

  if (!examData) return null

  const currentQ = questions[currentIdx]
  const answeredCount = Object.keys(answers).length
  const timerCritical = secondsLeft < 60

  function setAnswer(qid, val) {
    setAnswers((prev) => ({ ...prev, [qid]: val }))
  }

  return (
    <OverlayFrame
      open={open}
      title={`Rank Boss Exam — ${skill?.name ?? ''}`}
      subtitle={`${from_rank} → ${to_rank} · ${questions.length} questions`}
      onClose={onClose}
      className="overlay-frame--exam"
    >
      <div className="exam-layout">
        {/* Timer bar */}
        <div className={`exam-timer ${timerCritical ? 'exam-timer--critical' : ''}`}>
          <span className="exam-timer__label">Time remaining</span>
          <span className="exam-timer__display">{timerDisplay}</span>
        </div>

        {/* Question navigator */}
        <div className="exam-nav">
          {questions.map((q, idx) => (
            <button
              key={q.id}
              className={`exam-nav__dot${idx === currentIdx ? ' is-current' : ''}${answers[q.id] !== undefined ? ' is-answered' : ''}`}
              onClick={() => setCurrentIdx(idx)}
              title={`Q${idx + 1}`}
            >
              {idx + 1}
            </button>
          ))}
        </div>

        {/* Question body */}
        {currentQ ? (
          <div className="exam-question">
            <p className="exam-question__meta">
              Question {currentIdx + 1} of {questions.length}
              {currentQ.instruction ? ` · ${currentQ.instruction}` : ''}
            </p>
            <h3 className="exam-question__prompt">{currentQ.prompt}</h3>
            <QuestionInput
              question={currentQ}
              value={answers[currentQ.id]}
              onChange={(val) => setAnswer(currentQ.id, val)}
            />
          </div>
        ) : (
          <div className="empty-state">No questions found in this exam.</div>
        )}

        {/* Navigation */}
        <div className="exam-footer">
          <div className="exam-footer__nav">
            <button
              className="exam-footer__btn"
              disabled={currentIdx === 0}
              onClick={() => setCurrentIdx((i) => i - 1)}
            >
              ← Previous
            </button>
            <span className="exam-footer__progress">
              {answeredCount} / {questions.length} answered
            </span>
            <button
              className="exam-footer__btn"
              disabled={currentIdx === questions.length - 1}
              onClick={() => setCurrentIdx((i) => i + 1)}
            >
              Next →
            </button>
          </div>
          {error && <p className="exam-error">{error}</p>}
          <button
            className="exam-submit-btn"
            disabled={submitting}
            onClick={handleSubmit}
          >
            {submitting ? 'Submitting...' : `Submit Exam (${answeredCount}/${questions.length})`}
          </button>
        </div>
      </div>
    </OverlayFrame>
  )
}

function QuestionInput({ question, value, onChange }) {
  const { question_type, options_json } = question

  if (question_type === 'mcq' && Array.isArray(options_json)) {
    return (
      <div className="exam-options">
        {options_json.map((opt, idx) => {
          const optVal = typeof opt === 'object' ? opt.value ?? opt.text ?? String(idx) : String(opt)
          const optLabel = typeof opt === 'object' ? opt.text ?? opt.label ?? optVal : String(opt)
          return (
            <label key={idx} className={`exam-option${value === optVal ? ' is-selected' : ''}`}>
              <input
                type="radio"
                name={`q-${question.id}`}
                value={optVal}
                checked={value === optVal}
                onChange={() => onChange(optVal)}
              />
              <span>{optLabel}</span>
            </label>
          )
        })}
      </div>
    )
  }

  // Fallback: free text
  return (
    <textarea
      className="exam-textarea"
      placeholder="Type your answer here..."
      value={value ?? ''}
      onChange={(e) => onChange(e.target.value)}
      rows={4}
    />
  )
}

export default RankExamScreen
