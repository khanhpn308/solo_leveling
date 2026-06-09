import { useState } from 'react'

function ErrorDungeon({ activeErrors, api, onRefresh }) {
  const [activeBattle, setActiveBattle] = useState(null)
  const [userInput, setUserInput] = useState('')
  const [feedback, setFeedback] = useState(null) // { success: boolean, message: string }
  const [submitting, setSubmitting] = useState(false)

  // Map error types to thematic monster names and descriptions
  const getMonsterDetails = (errorType) => {
    switch (errorType) {
      case 'wrong_collocation':
        return {
          name: 'Collocation Chimera',
          icon: '🔗',
          color: 'from-pink-500 to-rose-700',
          desc: 'A beast formed of mismatched word partners. It thrives on unnatural pairings.'
        }
      case 'wrong_meaning':
        return {
          name: 'Semantic Specter',
          icon: '👻',
          color: 'from-purple-500 to-indigo-700',
          desc: 'A phantom that distorts definitions, leading scholars down paths of false comprehension.'
        }
      case 'wrong_register':
        return {
          name: 'Register Wraith',
          icon: '👺',
          color: 'from-amber-500 to-orange-700',
          desc: 'A shadow demon that whispers informal slang into formal academic texts.'
        }
      case 'wrong_word_form':
        return {
          name: 'Morphology Ogre',
          icon: '👹',
          color: 'from-red-500 to-amber-700',
          desc: 'A brute that crushes nouns into verbs and adjectives into adverbs indiscriminately.'
        }
      case 'wrong_preposition':
        return {
          name: 'Preposition Pixie',
          icon: '🧚',
          color: 'from-cyan-500 to-blue-700',
          desc: 'A mischievous sprite that swaps out prepositions to confuse relation paths.'
        }
      case 'wrong_grammar_pattern':
        return {
          name: 'Syntactic Golem',
          icon: '🗿',
          color: 'from-emerald-500 to-teal-700',
          desc: 'An ancient stone colossus built from broken gerunds and infinitive structures.'
        }
      default:
        return {
          name: 'Lexical Goblin',
          icon: '👺',
          color: 'from-slate-500 to-slate-700',
          desc: 'A minor pest that feeds on simple spelling and lexical slips.'
        }
    }
  }

  const startBattle = (error) => {
    setActiveBattle(error)
    setUserInput('')
    setFeedback(null)
  }

  const exitBattle = () => {
    setActiveBattle(null)
    setUserInput('')
    setFeedback(null)
    onRefresh()
  }

  const handleSubmitCorrection = async (e) => {
    e.preventDefault()
    if (!userInput.trim() || submitting) return

    setSubmitting(true)
    try {
      const isCorrect = userInput.trim().toLowerCase() === activeBattle.corrected_text.trim().toLowerCase()
      
      if (isCorrect) {
        // Submit victory / increment defeated count
        const response = await api(`/vocabulary/errors/${activeBattle.id}/defeat`, { method: 'POST' })
        
        const isFullyDefeated = response.status === 'defeated'
        setFeedback({
          success: true,
          message: isFullyDefeated 
            ? 'CRITICAL HIT! The monster has been fully defeated and banished from the dungeon!' 
            : `DIRECT HIT! Monster HP reduced. (Attempt ${response.defeated_count}/3 successful)`
        })
      } else {
        setFeedback({
          success: false,
          message: `MISS! That was incorrect. Let's study the correct answer and try again.`
        })
      }
    } catch (err) {
      setFeedback({
        success: false,
        message: err.message || 'Failed to submit action'
      })
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="error-dungeon-container">
      {activeBattle ? (
        <div className="battle-arena">
          <div className="battle-card-container">
            <button className="back-to-lobby-btn" onClick={exitBattle}>
              ← Flee Battle
            </button>

            <div className="battle-opponent">
              <span className="monster-arena-icon">{getMonsterDetails(activeBattle.error_type).icon}</span>
              <h4>{getMonsterDetails(activeBattle.error_type).name}</h4>
              <p className="monster-desc">{getMonsterDetails(activeBattle.error_type).desc}</p>
              
              <div className="monster-hp-bar">
                <span className="hp-label">HP: {3 - activeBattle.defeated_count}/3</span>
                <div className="hp-fill-container">
                  <div 
                    className="hp-fill" 
                    style={{ width: `${((3 - activeBattle.defeated_count) / 3) * 100}%` }}
                  />
                </div>
              </div>
            </div>

            <div className="battle-scroll">
              <div className="wrong-bubble">
                <span className="bubble-tag">WRONG PATTERN:</span>
                <p>"{activeBattle.wrong_text}"</p>
              </div>

              {feedback ? (
                <div className={`battle-feedback ${feedback.success ? 'feedback-success' : 'feedback-fail'}`}>
                  <h5>{feedback.success ? '💥 SUCCESS!' : '⚠️ TRY AGAIN'}</h5>
                  <p>{feedback.message}</p>
                  
                  {!feedback.success && (
                    <div className="explanation-box">
                      <p><strong>Correct Form:</strong> <code className="text-success">"{activeBattle.corrected_text}"</code></p>
                      {activeBattle.explanation && (
                        <p className="explanation-text"><strong>Why:</strong> {activeBattle.explanation}</p>
                      )}
                    </div>
                  )}

                  <button className="system-button system-button--primary continue-battle-btn" onClick={exitBattle}>
                    Return to Dungeon
                  </button>
                </div>
              ) : (
                <form className="correction-form" onSubmit={handleSubmitCorrection}>
                  <label htmlFor="correction-input">Forge the corrected sentence or phrase:</label>
                  <input
                    id="correction-input"
                    type="text"
                    className="system-input correction-text-input"
                    placeholder="Type the exact corrected text..."
                    value={userInput}
                    onChange={(e) => setUserInput(e.target.value)}
                    autoComplete="off"
                    autoFocus
                    required
                  />
                  <div className="battle-form-actions">
                    <button 
                      type="submit" 
                      className="system-button system-button--primary strike-btn"
                      disabled={submitting}
                    >
                      {submitting ? 'Casting Strike...' : 'Cast Correction Strike'}
                    </button>
                  </div>
                </form>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="dungeon-lobby">
          <div className="dungeon-header">
            <h4>ERROR DUNGEON</h4>
            <p>Monsters generated from your vocabulary mistakes. Defeat them to secure your progress.</p>
          </div>

          {activeErrors.length === 0 ? (
            <div className="dungeon-secured-screen">
              <span className="secured-crest">🛡️</span>
              <h5>DUNGEON SECURED</h5>
              <p>No active error monsters detected. Your vocabulary foundations are perfectly stable!</p>
            </div>
          ) : (
            <div className="monsters-grid">
              {activeErrors.map((error) => {
                const details = getMonsterDetails(error.error_type)
                const hp = 3 - error.defeated_count
                return (
                  <article key={error.id} className="monster-card">
                    <div className="monster-crest">
                      <span className="monster-icon">{details.icon}</span>
                      <span className="monster-hp-badge">HP {hp}/3</span>
                    </div>
                    
                    <div className="monster-body">
                      <h5>{details.name}</h5>
                      <span className="error-type-tag">{error.error_type.replace('wrong_', '').replace('_', ' ')}</span>
                      <p className="spotted-wrong">"{error.wrong_text}"</p>
                    </div>

                    <div className="monster-footer">
                      <button className="system-button fight-btn" onClick={() => startBattle(error)}>
                        Fight Monster
                      </button>
                    </div>
                  </article>
                )
              })}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default ErrorDungeon
