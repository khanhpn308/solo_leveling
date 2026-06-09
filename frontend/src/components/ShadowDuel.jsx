import { useState, useEffect, useRef } from 'react'

function ShadowDuel({ api, onXPUpdate }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [questions, setQuestions] = useState([])
  const [currentIndex, setCurrentIndex] = useState(0)
  
  // Game states
  const [lives, setLives] = useState(3)
  const [score, setScore] = useState(0)
  const [streak, setStreak] = useState(0)
  const [bestStreak, setBestStreak] = useState(0)
  const [selectedOption, setSelectedOption] = useState(null)
  const [isCorrect, setIsCorrect] = useState(null)
  const [completed, setCompleted] = useState(false)
  
  // Stats logging
  const [correctWords, setCorrectWords] = useState([])
  
  // Timer states
  const [timeLeft, setTimeLeft] = useState(10) // 10 seconds per question
  const timerRef = useRef(null)

  useEffect(() => {
    loadDuel()
    return () => clearInterval(timerRef.current)
  }, [])

  useEffect(() => {
    if (questions.length > 0 && currentIndex < questions.length && !completed && lives > 0) {
      startTimer()
    }
  }, [currentIndex, questions, completed, lives])

  function startTimer() {
    clearInterval(timerRef.current)
    setTimeLeft(10)
    timerRef.current = setInterval(() => {
      setTimeLeft(prev => {
        if (prev <= 1) {
          clearInterval(timerRef.current)
          handleTimeout()
          return 0
        }
        return prev - 1
      })
    }, 1000)
  }

  function handleTimeout() {
    // Treat as wrong answer
    setLives(l => {
      const nextL = l - 1
      if (nextL <= 0) {
        endGame(score, streak, true)
      }
      return nextL
    })
    setStreak(0)
    setIsCorrect(false)
    setSelectedOption('') // empty string marks timeout
    
    // Advance to next after a delay
    setTimeout(() => {
      advanceQuestion()
    }, 1500)
  }

  async function loadDuel() {
    try {
      setLoading(true)
      setError(null)
      setCompleted(false)
      setCurrentIndex(0)
      setLives(3)
      setScore(0)
      setStreak(0)
      setBestStreak(0)
      setCorrectWords([])
      const data = await api('/vocabulary/practice/shadow-duel')
      if (!data || !data.questions || data.questions.length === 0) {
        setQuestions([])
      } else {
        setQuestions(data.questions)
      }
    } catch (err) {
      setError(err.message || 'Failed to load Shadow Duel')
    } finally {
      setLoading(false)
    }
  }

  function handleAnswer(opt) {
    if (selectedOption !== null || lives <= 0) return // Already answered or dead
    clearInterval(timerRef.current)
    
    const currentQ = questions[currentIndex]
    setSelectedOption(opt)

    if (opt === currentQ.correct_answer) {
      setIsCorrect(true)
      setScore(s => s + 1)
      setStreak(st => {
        const nextSt = st + 1
        if (nextSt > bestStreak) setBestStreak(nextSt)
        return nextSt
      })
      setCorrectWords(prev => [...prev, currentQ.word])

      setTimeout(() => {
        advanceQuestion()
      }, 1000)
    } else {
      setIsCorrect(false)
      setStreak(0)
      setLives(l => {
        const nextL = l - 1
        if (nextL <= 0) {
          endGame(score, 0, true)
        }
        return nextL
      })

      setTimeout(() => {
        advanceQuestion()
      }, 1500)
    }
  }

  function advanceQuestion() {
    setSelectedOption(null)
    setIsCorrect(null)
    setCurrentIndex(prev => {
      const next = prev + 1
      if (next >= questions.length) {
        endGame(score + (isCorrect ? 1 : 0), streak, false)
        return prev
      }
      return next
    })
  }

  async function endGame(finalScore, finalStreak, lostAllLives) {
    setCompleted(true)
    clearInterval(timerRef.current)
    
    // Calculate final XP award
    // Correct synonym/antonym = 2 XP, correct register = 3 XP
    // 10 streak = +20 XP
    let xp = 0
    const finalCorrectWords = [...new Set(correctWords)]
    
    // Just sum basic correct answers
    questions.forEach((q, idx) => {
      if (finalCorrectWords.includes(q.word)) {
        xp += q.question_type === 'register' ? 3 : 2
      }
    })
    
    if (bestStreak >= 10 || finalStreak >= 10) {
      xp += 20
    }

    if (finalCorrectWords.length > 0) {
      try {
        await api('/vocabulary/practice/record-success', {
          method: 'POST',
          body: {
            words: finalCorrectWords,
            xp_gained: xp
          }
        })
        if (onXPUpdate) {
          onXPUpdate(xp)
        }
      } catch (err) {
        console.error('Failed to save practice success:', err)
      }
    }
  }

  if (loading) {
    return <div className="vocab-loader"> Summoning the Shadows...</div>
  }

  if (error) {
    return (
      <div className="vocab-empty-state">
        <p className="text-amber">{error}</p>
        <button className="system-button mt-2" onClick={loadDuel}>Try Again</button>
      </div>
    )
  }

  if (questions.length === 0) {
    return (
      <div className="vocab-empty-state">
        <p>No questions available. Add more words/relations to start a Shadow Duel!</p>
      </div>
    )
  }

  if (completed || lives <= 0) {
    const finalCorrectWords = [...new Set(correctWords)]
    let totalXp = 0
    questions.forEach(q => {
      if (finalCorrectWords.includes(q.word)) {
        totalXp += q.question_type === 'register' ? 3 : 2
      }
    })
    if (bestStreak >= 10) {
      totalXp += 20
    }

    return (
      <div className="duel-completed">
        <div className={`victory-badge ${lives <= 0 ? 'badge-failed' : 'badge-won'}`}>
          {lives <= 0 ? 'DEFEATED IN THE SHADOWS' : 'DUEL CLEARED'}
        </div>
        <h4>DUEL RESULTS</h4>
        <div className="victory-stat-grid mt-4 mb-4">
          <div className="victory-stat-box">
            <strong>{score} / {questions.length}</strong>
            <span>Questions Solved</span>
          </div>
          <div className="victory-stat-box">
            <strong>{bestStreak}</strong>
            <span>Best Streak</span>
          </div>
          <div className="victory-stat-box highlight">
            <strong>+{totalXp}</strong>
            <span>XP persistent reward</span>
          </div>
        </div>
        
        {finalCorrectWords.length > 0 && (
          <div className="mastered-words-list">
            <h5>Words Awakened:</h5>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', justifyContent: 'center', marginTop: '8px' }}>
              {finalCorrectWords.map((w, i) => (
                <span key={i} className="vocab-tag tag-mastered">{w}</span>
              ))}
            </div>
          </div>
        )}

        <button className="system-button system-button--primary mt-4" onClick={loadDuel}>
          Duel Again
        </button>
      </div>
    )
  }

  const currentQ = questions[currentIndex]

  return (
    <div className="shadow-duel">
      <div className="duel-header">
        <div className="duel-top-info">
          <h3>SHADOW DUEL</h3>
          <div className="duel-lives">
            {Array.from({ length: 3 }).map((_, i) => (
              <span 
                key={i} 
                className={`life-heart ${i < lives ? 'active' : 'spent'}`}
              >
                ❤
              </span>
            ))}
          </div>
        </div>
        
        <div className="duel-stats-row">
          <span>Streak: <strong>{streak}</strong></span>
          <span>Index: <strong>{currentIndex + 1} / {questions.length}</strong></span>
        </div>

        <div className="duel-timer-bar">
          <div 
            className="duel-timer-progress" 
            style={{ 
              width: `${(timeLeft / 10) * 100}%`,
              background: timeLeft <= 3 ? 'var(--danger)' : 'var(--primary)'
            }}
          />
        </div>
      </div>

      <div className="duel-arena">
        <div className="duel-card">
          <span className="duel-card-label">{currentQ.question_type.toUpperCase()} DUEL</span>
          <div className="duel-prompt">
            {currentQ.question_type === 'synonym' && <p>Select the synonym of:</p>}
            {currentQ.question_type === 'antonym' && <p>Select the antonym of:</p>}
            {currentQ.question_type === 'register' && <p>Convert informal word to academic:</p>}
            <h2>{currentQ.word}</h2>
          </div>
        </div>

        {selectedOption !== null && currentQ.register_note && (
          <div className="duel-feedback-note">
            <span className="feedback-label">SYSTEM ADVICE:</span>
            <p>{currentQ.register_note}</p>
          </div>
        )}

        <div className="duel-options">
          {currentQ.options.map((opt, idx) => {
            let btnClass = 'duel-option-btn'
            if (selectedOption === opt) {
              btnClass += isCorrect ? ' correct' : ' wrong'
            } else if (selectedOption !== null && opt === currentQ.correct_answer) {
              btnClass += ' correct-reveal'
            }

            return (
              <button
                key={idx}
                className={btnClass}
                onClick={() => handleAnswer(opt)}
                disabled={selectedOption !== null}
              >
                {opt}
              </button>
            )
          })}
        </div>
      </div>
    </div>
  )
}

export default ShadowDuel
