import { useState, useEffect, useRef } from 'react'

function EchoChamber({ api, onXPUpdate }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [questions, setQuestions] = useState([])
  const [currentIndex, setCurrentIndex] = useState(0)

  // Game states
  const [lives, setLives] = useState(3)
  const [score, setScore] = useState(0)
  const [streak, setStreak] = useState(0)
  const [bestStreak, setBestStreak] = useState(0)
  const [completed, setCompleted] = useState(false)

  // Stage controls per question
  // stage: 'stress' | 'silent'
  const [stage, setStage] = useState('stress')
  const [selectedSyllable, setSelectedSyllable] = useState(null)
  const [stressCorrect, setStressCorrect] = useState(null)
  
  const [clickedLetters, setClickedLetters] = useState([]) // index of characters clicked
  const [silentCorrect, setSilentCorrect] = useState(null)

  // Stats logging
  const [correctWords, setCorrectWords] = useState([])

  useEffect(() => {
    loadEcho()
  }, [])

  async function loadEcho() {
    try {
      setLoading(true)
      setError(null)
      setCompleted(false)
      setCurrentIndex(0)
      setLives(3)
      setScore(0)
      setStreak(0)
      setBestStreak(0)
      setStage('stress')
      setSelectedSyllable(null)
      setStressCorrect(null)
      setClickedLetters([])
      setSilentCorrect(null)
      setCorrectWords([])

      const data = await api('/vocabulary/practice/echo-chamber')
      if (data && data.questions && data.questions.length > 0) {
        setQuestions(data.questions)
        // Automatically play first word audio
        setTimeout(() => speakWord(data.questions[0].word), 500)
      } else {
        setQuestions([])
      }
    } catch (err) {
      setError(err.message || 'Failed to load Echo Chamber')
    } finally {
      setLoading(false)
    }
  }

  function speakWord(text) {
    if ('speechSynthesis' in window) {
      // Cancel any ongoing speaking
      window.speechSynthesis.cancel()
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.lang = 'en-US'
      
      const voices = window.speechSynthesis.getVoices()
      // Prefer Google US English or standard English voice
      const enVoice = voices.find(v => v.lang === 'en-US') || voices.find(v => v.lang.startsWith('en'))
      if (enVoice) utterance.voice = enVoice
      
      window.speechSynthesis.speak(utterance)
    }
  }

  function handleSyllableClick(idx) {
    if (selectedSyllable !== null || lives <= 0) return
    const currentQ = questions[currentIndex]
    setSelectedSyllable(idx)

    if (idx === currentQ.stressed_index) {
      setStressCorrect(true)
      setScore(s => s + 1)
      setStreak(st => {
        const nextSt = st + 1
        if (nextSt > bestStreak) setBestStreak(nextSt)
        return nextSt
      })

      // If the word has silent letters, move to silent letter hunt stage
      if (currentQ.silent_letters && currentQ.silent_letters.length > 0) {
        setTimeout(() => {
          setStage('silent')
        }, 1000)
      } else {
        // Record success for this word
        setCorrectWords(prev => [...prev, currentQ.word])
        setTimeout(() => {
          advanceQuestion()
        }, 1000)
      }
    } else {
      setStressCorrect(false)
      setStreak(0)
      setLives(l => {
        const nextL = l - 1
        if (nextL <= 0) endGame(score, 0)
        return nextL
      })
      setTimeout(() => {
        setSelectedSyllable(null)
        setStressCorrect(null)
      }, 1200)
    }
  }

  function handleLetterClick(charIdx, char) {
    if (silentCorrect !== null || lives <= 0) return
    const currentQ = questions[currentIndex]
    
    // Toggle clicked state
    let nextClicked = [...clickedLetters]
    if (nextClicked.includes(charIdx)) {
      nextClicked = nextClicked.filter(idx => idx !== charIdx)
    } else {
      nextClicked.push(charIdx)
    }
    setClickedLetters(nextClicked)

    // Check if the set of clicked characters matches the silent letters
    const clickedChars = nextClicked.map(idx => currentQ.word[idx].toLowerCase())
    const targetSilent = currentQ.silent_letters.map(c => c.toLowerCase())

    // Check if they found all of them
    const hasAll = targetSilent.every(c => clickedChars.includes(c))
    const hasOnlySilent = clickedChars.every(c => targetSilent.includes(c))

    if (hasAll && hasOnlySilent) {
      setSilentCorrect(true)
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
    } else if (nextClicked.length >= targetSilent.length && (!hasOnlySilent)) {
      // Got it wrong
      setSilentCorrect(false)
      setStreak(0)
      setLives(l => {
        const nextL = l - 1
        if (nextL <= 0) endGame(score, 0)
        return nextL
      })
      setTimeout(() => {
        setClickedLetters([])
        setSilentCorrect(null)
      }, 1200)
    }
  }

  function advanceQuestion() {
    setSelectedSyllable(null)
    setStressCorrect(null)
    setClickedLetters([])
    setSilentCorrect(null)
    setStage('stress')

    setCurrentIndex(prev => {
      const next = prev + 1
      if (next >= questions.length) {
        endGame(score, streak)
        return prev
      }
      // Speak next word
      speakWord(questions[next].word)
      return next
    })
  }

  async function endGame(finalScore, finalStreak) {
    setCompleted(true)
    
    // Calculate final XP
    let xp = 0
    const finalCorrectWords = [...new Set(correctWords)]
    questions.forEach(q => {
      if (finalCorrectWords.includes(q.word)) {
        xp += q.silent_letters.length > 0 ? 6 : 3
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
        console.error('Failed to save Echo Chamber success:', err)
      }
    }
  }

  if (loading) {
    return <div className="vocab-loader">Charging the Echo chamber...</div>
  }

  if (error) {
    return (
      <div className="vocab-empty-state">
        <p className="text-amber">{error}</p>
        <button className="system-button mt-2" onClick={loadEcho}>Try Again</button>
      </div>
    )
  }

  if (questions.length === 0) {
    return (
      <div className="vocab-empty-state">
        <p>No pronunciation cards available. Add words with IPA & Stress in Codex to begin.</p>
      </div>
    )
  }

  if (completed || lives <= 0) {
    const finalCorrectWords = [...new Set(correctWords)]
    let totalXp = 0
    questions.forEach(q => {
      if (finalCorrectWords.includes(q.word)) {
        totalXp += q.silent_letters.length > 0 ? 6 : 3
      }
    })
    if (bestStreak >= 10) {
      totalXp += 20
    }

    return (
      <div className="echo-completed">
        <div className={`victory-badge ${lives <= 0 ? 'badge-failed' : 'badge-won'}`}>
          {lives <= 0 ? 'ECHO SILENCED' : 'CHAMBER CLEARED'}
        </div>
        <h4>CHAMBER RESULTS</h4>
        <div className="victory-stat-grid mt-4 mb-4">
          <div className="victory-stat-box">
            <strong>{score}</strong>
            <span>Completed Challenges</span>
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

        <button className="system-button system-button--primary mt-4" onClick={loadEcho}>
          Enter Chamber Again
        </button>
      </div>
    )
  }

  const currentQ = questions[currentIndex]

  return (
    <div className="echo-chamber">
      <div className="echo-header">
        <div className="echo-top-info">
          <h3>ECHO CHAMBER</h3>
          <div className="echo-lives">
            {Array.from({ length: 3 }).map((_, i) => (
              <span key={i} className={`life-heart ${i < lives ? 'active' : 'spent'}`}>
                ❤
              </span>
            ))}
          </div>
        </div>
        <div className="echo-stats-row">
          <span>Streak: <strong>{streak}</strong></span>
          <span>Index: <strong>{currentIndex + 1} / {questions.length}</strong></span>
        </div>
      </div>

      <div className="echo-arena mt-4">
        {/* Word Card Panel */}
        <div className="echo-card">
          <span className="echo-card-label">PHONETICS CHALLENGE</span>
          <h2>{currentQ.word}</h2>
          <div className="echo-ipa mt-2">{currentQ.pronunciation_ipa}</div>
          
          <button 
            className="system-button system-button--primary speak-btn mt-3" 
            onClick={() => speakWord(currentQ.word)}
          >
            🔊 LISTEN PRO-WORD
          </button>
        </div>

        {/* Stage 1: Stress Syllables Challenge */}
        {stage === 'stress' && (
          <div className="stress-challenge-box w-full max-w-xl mt-4">
            <h4 className="challenge-title">STAGE 1: CLICK THE STRESSED SYLLABLE</h4>
            <p className="text-muted text-center mb-3">Listen to the word stress and select the syllable with primary stress.</p>
            
            <div className="syllables-row">
              {currentQ.syllables.map((syl, idx) => {
                let btnClass = 'syllable-btn'
                if (selectedSyllable === idx) {
                  btnClass += stressCorrect ? ' correct' : ' wrong'
                } else if (selectedSyllable !== null && idx === currentQ.stressed_index) {
                  btnClass += ' correct-reveal'
                }

                return (
                  <button
                    key={idx}
                    className={btnClass}
                    onClick={() => handleSyllableClick(idx)}
                    disabled={selectedSyllable !== null}
                  >
                    {syl.toUpperCase()}
                  </button>
                )
              })}
            </div>
          </div>
        )}

        {/* Stage 2: Silent Letters Challenge */}
        {stage === 'silent' && (
          <div className="silent-challenge-box w-full max-w-xl mt-4">
            <h4 className="challenge-title">STAGE 2: HUNT THE SILENT LETTERS</h4>
            <p className="text-muted text-center mb-3">Click all silent letter(s) that are written but NOT pronounced in the word.</p>
            
            <div className="letters-row">
              {currentQ.word.split('').map((char, idx) => {
                const isClicked = clickedLetters.includes(idx)
                let btnClass = 'letter-btn'
                if (isClicked) {
                  btnClass += ' selected'
                }
                if (silentCorrect !== null) {
                  btnClass += silentCorrect ? ' correct' : ' wrong'
                }

                return (
                  <button
                    key={idx}
                    className={btnClass}
                    onClick={() => handleLetterClick(idx, char)}
                    disabled={silentCorrect !== null}
                  >
                    {char.toUpperCase()}
                  </button>
                )
              })}
            </div>

            {silentCorrect !== null && (
              <div className="silent-feedback mt-3 text-center">
                {silentCorrect ? (
                  <span className="text-success">✔ Correct! Silent letters resolved.</span>
                ) : (
                  <span className="text-danger">✘ Wrong! Try again.</span>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default EchoChamber
