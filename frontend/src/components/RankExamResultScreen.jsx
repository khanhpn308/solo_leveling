import OverlayFrame from './OverlayFrame'

function RankExamResultScreen({ open, result, skill, onClose, onRetry }) {
  // result: { attempt_id, passed, score_percent, score_points, total_points, confirmed_rank }
  if (!result) return null

  const { passed, score_percent, score_points, total_points, confirmed_rank } = result
  const pct = Math.round(score_percent ?? 0)

  return (
    <OverlayFrame
      open={open}
      title={passed ? 'SYSTEM GATE CLEARED' : 'SYSTEM GATE FAILED'}
      subtitle={`${skill?.name ?? ''} rank exam result`}
      onClose={onClose}
      className={`overlay-frame--result ${passed ? 'overlay-frame--result-pass' : 'overlay-frame--result-fail'}`}
    >
      <div className="exam-result">
        <div className={`exam-result__banner ${passed ? 'exam-result__banner--pass' : 'exam-result__banner--fail'}`}>
          <span className="exam-result__icon">{passed ? '⚔️' : '💀'}</span>
          <h2 className="exam-result__verdict">{passed ? 'CLEARED' : 'FAILED'}</h2>
        </div>

        <div className="exam-result__stats">
          <div className="exam-result__stat">
            <span className="exam-result__stat-label">Score</span>
            <strong className="exam-result__stat-value">
              {score_points} / {total_points}
            </strong>
          </div>
          <div className="exam-result__stat">
            <span className="exam-result__stat-label">Accuracy</span>
            <strong className="exam-result__stat-value">{pct}%</strong>
          </div>
          <div className="exam-result__stat">
            <span className="exam-result__stat-label">Current Rank</span>
            <strong className="exam-result__stat-value exam-result__rank">{confirmed_rank}</strong>
          </div>
        </div>

        {passed ? (
          <p className="exam-result__message exam-result__message--pass">
            Rank promoted to <strong>{confirmed_rank}</strong>. Keep pushing forward.
          </p>
        ) : (
          <p className="exam-result__message exam-result__message--fail">
            Not enough this time. Study more and challenge again when ready.
          </p>
        )}

        <div className="exam-result__actions">
          {!passed && onRetry && (
            <button className="exam-result__btn exam-result__btn--retry" onClick={onRetry}>
              Try Again
            </button>
          )}
          <button className="exam-result__btn exam-result__btn--close" onClick={onClose}>
            Back to Dashboard
          </button>
        </div>
      </div>
    </OverlayFrame>
  )
}

export default RankExamResultScreen
