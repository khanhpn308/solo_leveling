import { useState, useEffect } from 'react'

function CollocationForge({ api, onXPUpdate }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [practiceData, setPracticeData] = useState(null)
  
  const [currentIndex, setCurrentIndex] = useState(0)
  const [options, setOptions] = useState([])
  const [selectedOption, setSelectedOption] = useState(null)
  const [isCorrect, setIsCorrect] = useState(null)
  const [completed, setCompleted] = useState(false)
  const [xpEarned, setXpEarned] = useState(0)

  useEffect(() => {
    loadPractice()
  }, [])

  async function loadPractice() {
    try {
      setLoading(true)
      setError(null)
      setCompleted(false)
      setCurrentIndex(0)
      setXpEarned(0)
      const data = await api('/vocabulary/practice/collocations')
      if (!data || !data.matches || data.matches.length === 0) {
        setPracticeData(null)
      } else {
        setPracticeData(data)
        setupQuestion(data, 0)
      }
    } catch (err) {
      setError(err.message || 'Failed to load collocation practice')
    } finally {
      setLoading(false)
    }
  }

  function setupQuestion(data, index) {
    if (index >= data.matches.length) {
      setCompleted(true)
      if (onXPUpdate && xpEarned > 0) {
        onXPUpdate(xpEarned) // Just visual/mock since we didn't add a backend XP route yet
      }
      return
    }

    const currentMatch = data.matches[index]
    const correctOption = currentMatch.collocation

    // Collect distractors: other matches' collocations + dedicated distractors
    const otherCollocations = data.matches
      .filter((m, i) => i !== index)
      .map(m => m.collocation)
    
    const allDistractors = [...otherCollocations, ...data.distractors]
    
    // Shuffle and pick up to 3 distractors
    const shuffledDistractors = [...new Set(allDistractors)].sort(() => 0.5 - Math.random())
    const selectedDistractors = shuffledDistractors.slice(0, 3)

    // Combine and shuffle options
    const finalOptions = [correctOption, ...selectedDistractors].sort(() => 0.5 - Math.random())
    
    setOptions(finalOptions)
    setSelectedOption(null)
    setIsCorrect(null)
  }

  function handleSelect(opt) {
    if (selectedOption !== null) return // Already answered
    
    const currentMatch = practiceData.matches[currentIndex]
    setSelectedOption(opt)
    
    if (opt === currentMatch.collocation) {
      setIsCorrect(true)
      setXpEarned(prev => prev + 10)
      setTimeout(() => {
        setCurrentIndex(prev => {
          const next = prev + 1
          setupQuestion(practiceData, next)
          return next
        })
      }, 1000)
    } else {
      setIsCorrect(false)
      setTimeout(() => {
        setSelectedOption(null)
        setIsCorrect(null)
      }, 1500)
    }
  }

  if (loading) {
    return <div className="vocab-loader">Heating up the Forge...</div>
  }

  if (error) {
    return (
      <div className="vocab-empty-state">
        <p className="text-amber">{error}</p>
        <button className="system-button mt-2" onClick={loadPractice}>Try Again</button>
      </div>
    )
  }

  if (!practiceData || practiceData.matches.length === 0) {
    return (
      <div className="vocab-empty-state">
        <p>No collocations available. Awaken words and forge collocations first!</p>
      </div>
    )
  }

  if (completed) {
    return (
      <div className="forge-completed">
        <div className="victory-badge">FORGE COMPLETE</div>
        <h4>COLLOCATIONS MASTERED</h4>
        <div className="victory-stat mt-4 mb-4">
          <strong>+{xpEarned}</strong>
          <span>Support Skill XP Earned</span>
        </div>
        <button className="system-button system-button--primary" onClick={loadPractice}>
          Forge Again
        </button>
      </div>
    )
  }

  const currentMatch = practiceData.matches[currentIndex]

  return (
    <div className="collocation-forge">
      <div className="forge-header">
        <h3>COLLOCATION FORGE</h3>
        <p>Combine words to create powerful expressions.</p>
        <div className="forge-progress">
          Set: {currentIndex + 1} / {practiceData.matches.length}
        </div>
      </div>

      <div className="forge-arena">
        <div className="forge-core-word">
          <span className="forge-label">Core Word</span>
          <h2>{currentMatch.core_word}</h2>
          {currentMatch.collocation_type && (
            <span className="vocab-tag tag-level">{currentMatch.collocation_type}</span>
          )}
        </div>

        <div className="forge-options">
          {options.map((opt, idx) => {
            let btnClass = 'forge-option-btn'
            if (selectedOption === opt) {
              btnClass += isCorrect ? ' correct' : ' wrong'
            } else if (selectedOption !== null && opt === currentMatch.collocation) {
              btnClass += ' correct-reveal' // Reveal correct if they got it wrong
            }

            return (
              <button 
                key={idx} 
                className={btnClass}
                onClick={() => handleSelect(opt)}
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

export default CollocationForge
