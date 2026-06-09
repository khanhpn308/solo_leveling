import { useState } from 'react'

function VocabularyBoss({ bossStatus, api, onRefresh }) {
  const [activeExam, setActiveExam] = useState(null) // { boss_id, questions, currentIndex, answers, completed, result }
  const [selectedOption, setSelectedOption] = useState('')
  const [loadingChallenge, setLoadingChallenge] = useState(false)
  const [submittingExam, setSubmittingExam] = useState(false)

  if (!bossStatus) {
    return <div className="loading-state">Loading boss status...</div>
  }

  const startChallenge = async (bossId) => {
    setLoadingChallenge(true)
    try {
      const exam = await api(`/vocabulary/boss/${bossId}/challenge`, { method: 'POST' })
      setActiveExam({
        boss_id: bossId,
        questions: exam.questions,
        currentIndex: 0,
        answers: {},
        completed: false,
        result: null
      })
      setSelectedOption('')
    } catch (err) {
      alert(err.message || 'Failed to start challenge')
    } finally {
      setLoadingChallenge(false)
    }
  }

  const handleSelectOption = (opt) => {
    setSelectedOption(opt)
  }

  const handleNextQuestion = async () => {
    if (!selectedOption) return

    const isLast = activeExam.currentIndex === activeExam.questions.length - 1
    const updatedAnswers = {
      ...activeExam.answers,
      [activeExam.currentIndex]: selectedOption
    }

    if (isLast) {
      // Calculate score and submit
      setSubmittingExam(true)
      try {
        let correctCount = 0
        activeExam.questions.forEach((q, idx) => {
          if (updatedAnswers[idx] === q.correct_answer) {
            correctCount++
          }
        })
        const pct = (correctCount / activeExam.questions.length) * 100
        const submissionResult = await api(`/vocabulary/boss/${activeExam.boss_id}/submit`, {
          method: 'POST',
          body: { score_pct: pct }
        })

        setActiveExam(prev => ({
          ...prev,
          answers: updatedAnswers,
          completed: true,
          result: submissionResult
        }))
      } catch (err) {
        alert(err.message || 'Failed to submit exam results')
      } finally {
        setSubmittingExam(false)
      }
    } else {
      setActiveExam(prev => ({
        ...prev,
        currentIndex: prev.currentIndex + 1,
        answers: updatedAnswers
      }))
      setSelectedOption('')
    }
  }

  const exitExam = () => {
    setActiveExam(null)
    onRefresh()
  }

  const currentBoss = activeExam ? bossStatus.bosses.find(b => b.id === activeExam.boss_id) : null

  return (
    <div className="vocabulary-boss-container">
      {activeExam ? (
        <div className="boss-arena">
          <div className="arena-card">
            {activeExam.completed ? (
              <div className="exam-result-view">
                <div className={`result-crest ${activeExam.result.passed ? 'passed' : 'failed'}`}>
                  {activeExam.result.passed ? '🏆 VICTORY' : '💀 DEFEAT'}
                </div>
                <h3>{currentBoss.title} Cleared Status</h3>
                
                <div className="result-stats">
                  <div className="stat-circle">
                    <strong>{activeExam.result.score_pct.toFixed(0)}%</strong>
                    <span>Your Score</span>
                  </div>
                  <div className="stat-required">
                    <span>Required to Pass:</span>
                    <strong>75%</strong>
                  </div>
                </div>

                <p className="result-message">{activeExam.result.message}</p>

                {activeExam.result.passed && (
                  <div className="rewards-claimed-box">
                    <h5>REWARDS EARNED</h5>
                    <div className="rewards-list">
                      <div className="reward-item">
                        <span>XP Awarded</span>
                        <strong>+{activeExam.result.reward_xp} Vocabulary XP</strong>
                      </div>
                    </div>
                  </div>
                )}

                <button className="system-button system-button--primary return-btn" onClick={exitExam}>
                  Exit Arena
                </button>
              </div>
            ) : (
              <div className="exam-question-view">
                <div className="arena-bar">
                  <span>BOSS BATTLE: {currentBoss.title}</span>
                  <span>
                    Question {activeExam.currentIndex + 1} of {activeExam.questions.length}
                  </span>
                </div>

                <div className="question-body">
                  <h4 className="question-prompt">
                    {activeExam.questions[activeExam.currentIndex].prompt}
                  </h4>

                  <div className="options-grid">
                    {activeExam.questions[activeExam.currentIndex].choices.map((opt, oIdx) => (
                      <button
                        key={oIdx}
                        className={`option-btn ${selectedOption === opt ? 'option-btn--selected' : ''}`}
                        onClick={() => handleSelectOption(opt)}
                      >
                        <span className="option-marker">{String.fromCharCode(65 + oIdx)}</span>
                        <span className="option-text">{opt}</span>
                      </button>
                    ))}
                  </div>
                </div>

                <div className="arena-footer">
                  <button className="flee-exam-btn" onClick={exitExam}>
                    Flee Battle
                  </button>
                  <button
                    className="system-button next-q-btn"
                    onClick={handleNextQuestion}
                    disabled={!selectedOption || submittingExam}
                  >
                    {submittingExam ? 'Submitting...' : (activeExam.currentIndex === activeExam.questions.length - 1 ? 'Finish Challenge' : 'Next Question')}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      ) : (
        <div className="boss-lobby">
          <div className="lobby-header">
            <h4>LEXICAL CHECKPOINTS</h4>
            <p>Awaken your ranks and earn legendary badges by proving your lexical retention.</p>
          </div>

          <div className="boss-cards-grid">
            {bossStatus.bosses.map((boss) => (
              <article key={boss.id} className={`boss-card boss-card--${boss.status}`}>
                <div className="boss-card-header">
                  <div>
                    <span className="boss-stage-label">{boss.stage}</span>
                    <h5>{boss.title}</h5>
                  </div>
                  <div className="boss-badge-status">
                    {boss.status === 'cleared' && <span className="cleared-crest-badge">CLEARED</span>}
                    {boss.status === 'ready' && <span className="ready-crest-badge">READY</span>}
                    {boss.status === 'locked' && <span className="locked-crest-badge">LOCKED</span>}
                  </div>
                </div>

                <p className="boss-goal-text">{boss.goal}</p>

                <div className="boss-requirements">
                  <h6>REQUIREMENTS:</h6>
                  <ul className="req-list">
                    {Object.entries(boss.requirements).map(([key, req]) => (
                      <li key={key} className={`req-item ${req.met ? 'req-met' : 'req-unmet'}`}>
                        <span className="req-icon">{req.met ? '✓' : '✗'}</span>
                        <span className="req-name">{key.replace('_', ' ')}</span>
                        <strong className="req-values">
                          {req.current} / {req.target}
                        </strong>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="boss-card-footer">
                  <span className="boss-reward-xp">+{boss.reward_xp} Vocabulary XP</span>
                  
                  {boss.status === 'ready' && (
                    <button 
                      className="system-button challenge-btn"
                      onClick={() => startChallenge(boss.id)}
                      disabled={loadingChallenge}
                    >
                      {loadingChallenge ? 'Preparing arena...' : 'Challenge Boss'}
                    </button>
                  )}

                  {boss.status === 'cleared' && (
                    <button className="system-button challenge-btn cleared" disabled>
                      Defeated
                    </button>
                  )}

                  {boss.status === 'locked' && (
                    <button className="system-button challenge-btn locked" disabled>
                      Locked
                    </button>
                  )}
                </div>
              </article>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default VocabularyBoss
