import { useState, useEffect } from 'react'
import WordNetworkTree from './WordNetworkTree'
import CollocationForge from './CollocationForge'
import ShadowDuel from './ShadowDuel'
import WordFamilyEvolution from './WordFamilyEvolution'
import EchoChamber from './EchoChamber'
import ErrorDungeon from './ErrorDungeon'
import VocabularyBoss from './VocabularyBoss'

const INITIAL_FORM = {
  word: '',
  normalized_word: '',
  part_of_speech: 'noun',
  cefr_level: 'B2',
  ielts_topic: 'General',
  meaning_en: '',
  meaning_vi: '',
  pronunciation_ipa: '',
  word_stress: '',
  source_type: 'self-study',
  source_reference: '',
}

function VocabularyWorkspace({ onClose, api, vocabularyItems, dueFlashcards, onLoadData }) {
  const [activeTab, setActiveTab] = useState('codex')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [editingItem, setEditingItem] = useState(null)
  const [form, setForm] = useState(INITIAL_FORM)
  const [searchQuery, setSearchQuery] = useState('')

  // Flashcard review state
  const [activeReview, setActiveReview] = useState(null)
  const [showAnswer, setShowAnswer] = useState(false)
  const [reviewXpEarned, setReviewXpEarned] = useState(0)

  // Error dungeon and boss states
  const [activeErrors, setActiveErrors] = useState([])
  const [bossStatus, setBossStatus] = useState(null)

  useEffect(() => {
    loadData()
  }, [])

  async function loadData() {
    try {
      setLoading(true)
      await onLoadData()
      
      const errorsData = await api('/vocabulary/errors/active')
      setActiveErrors(errorsData)
      
      const bossData = await api('/vocabulary/boss/status')
      setBossStatus(bossData)
      
      setError('')
    } catch (err) {
      setError(err.message || 'Failed to load vocabulary data')
    } finally {
      setLoading(false)
    }
  }

  function handleOpenCreate() {
    setForm(INITIAL_FORM)
    setEditingItem(null)
    setIsFormOpen(true)
  }

  function handleOpenEdit(item) {
    setForm({
      word: item.word || '',
      normalized_word: item.normalized_word || '',
      part_of_speech: item.part_of_speech || 'noun',
      cefr_level: item.cefr_level || 'B2',
      ielts_topic: item.ielts_topic || 'General',
      meaning_en: item.meaning_en || '',
      meaning_vi: item.meaning_vi || '',
      pronunciation_ipa: item.pronunciation_ipa || '',
      word_stress: item.word_stress || '',
      source_type: item.source_type || 'self-study',
      source_reference: item.source_reference || '',
    })
    setEditingItem(item)
    setIsFormOpen(true)
  }

  async function handleSubmit(event) {
    event.preventDefault()
    try {
      setSubmitting(true)
      if (editingItem) {
        await api(`/vocabulary/${editingItem.id}`, {
          method: 'PUT',
          body: JSON.stringify(form),
        })
      } else {
        await api('/vocabulary', {
          method: 'POST',
          body: JSON.stringify(form),
        })
      }
      setIsFormOpen(false)
      setForm(INITIAL_FORM)
      setEditingItem(null)
      loadData()
    } catch (err) {
      setError(err.message || 'Failed to save vocabulary item')
    } finally {
      setSubmitting(false)
    }
  }

  async function handleDelete(itemId) {
    if (!window.confirm('Are you sure you want to delete this word from the Codex?')) return
    try {
      setLoading(true)
      await api(`/vocabulary/${itemId}`, { method: 'DELETE' })
      loadData()
    } catch (err) {
      setError(err.message || 'Failed to delete item')
      setLoading(false)
    }
  }

  // Collocation / Example add state
  const [activeItemDetails, setActiveItemDetails] = useState(null)
  const [collocationText, setCollocationText] = useState('')
  const [collocationType, setCollocationType] = useState('adjective + noun')
  const [exampleText, setExampleText] = useState('')

  async function handleAddCollocation(itemId) {
    if (!collocationText.trim()) return
    try {
      setSubmitting(true)
      await api(`/vocabulary/${itemId}/collocations`, {
        method: 'POST',
        body: JSON.stringify({
          collocation: collocationText,
          collocation_type: collocationType,
        }),
      })
      setCollocationText('')
      loadData()
    } catch (err) {
      setError(err.message || 'Failed to add collocation')
    } finally {
      setSubmitting(false)
    }
  }

  async function handleDeleteCollocation(collocationId) {
    try {
      setLoading(true)
      await api(`/vocabulary/collocations/${collocationId}`, { method: 'DELETE' })
      loadData()
    } catch (err) {
      setError(err.message || 'Failed to delete collocation')
      setLoading(false)
    }
  }

  async function handleAddExample(itemId) {
    if (!exampleText.trim()) return
    try {
      setSubmitting(true)
      await api(`/vocabulary/${itemId}/examples`, {
        method: 'POST',
        body: JSON.stringify({ example_sentence: exampleText }),
      })
      setExampleText('')
      loadData()
    } catch (err) {
      setError(err.message || 'Failed to add example')
    } finally {
      setSubmitting(false)
    }
  }

  async function handleDeleteExample(exampleId) {
    try {
      setLoading(true)
      await api(`/vocabulary/examples/${exampleId}`, { method: 'DELETE' })
      loadData()
    } catch (err) {
      setError(err.message || 'Failed to delete example')
      setLoading(false)
    }
  }

  // Spaced repetition flashcard review loop
  function handleStartReview() {
    if (dueFlashcards.length === 0) return
    setActiveReview({
      currentIndex: 0,
      cards: dueFlashcards,
      completed: false,
    })
    setShowAnswer(false)
    setReviewXpEarned(0)
  }

  async function handleReviewAction(result) {
    if (!activeReview) return
    const card = activeReview.cards[activeReview.currentIndex]
    
    const xpEarned = { again: 0, hard: 1, good: 2, easy: 3 }[result] || 0
    setReviewXpEarned((prev) => prev + xpEarned)

    try {
      await api(`/flashcards/${card.id}/review`, {
        method: 'POST',
        body: JSON.stringify({ result }),
      })
    } catch (err) {
      console.error('Failed to submit review:', err)
    }

    const nextIndex = activeReview.currentIndex + 1
    if (nextIndex >= activeReview.cards.length) {
      setActiveReview((current) => ({ ...current, completed: true }))
      loadData()
    } else {
      setActiveReview((current) => ({ ...current, currentIndex: nextIndex }))
      setShowAnswer(false)
    }
  }

  function handleCloseReview() {
    setActiveReview(null)
    setShowAnswer(false)
  }

  const filteredItems = vocabularyItems.filter((item) => {
    const q = searchQuery.toLowerCase()
    return (
      (item.word || '').toLowerCase().includes(q) ||
      (item.meaning_en || '').toLowerCase().includes(q) ||
      (item.meaning_vi || '').toLowerCase().includes(q) ||
      (item.ielts_topic || '').toLowerCase().includes(q)
    )
  })

  return (
    <div className="vocab-workspace">
      <aside className="vocab-sidebar">
        <div className="vocab-sidebar__header">
          <button className="vocab-back-button" onClick={onClose} aria-label="Return to Dashboard">
            <span className="vocab-back-arrow">←</span> Back to Dashboard
          </button>
          <div className="vocab-sidebar__title-block">
            <span className="vocab-sidebar__eyebrow">Support Skill System</span>
            <h2 className="vocab-sidebar__title">Lexical Awakening</h2>
          </div>
        </div>

        <div className="vocab-sidebar__stats">
          <div className="vocab-stat-card">
            <span>Codex Words</span>
            <strong>{vocabularyItems.length}</strong>
          </div>
          <div className="vocab-stat-card">
            <span>Due Cards</span>
            <strong className={dueFlashcards.length > 0 ? 'text-amber' : ''}>{dueFlashcards.length}</strong>
          </div>
          <div className="vocab-stat-card">
            <span>Active Errors</span>
            <strong className={activeErrors.length > 0 ? 'text-danger' : ''}>{activeErrors.length}</strong>
          </div>
        </div>

        <nav className="vocab-sidebar__nav">
          <button
            className={`vocab-nav-btn ${activeTab === 'codex' ? 'is-active' : ''}`}
            type="button"
            onClick={() => { setActiveTab('codex'); setIsFormOpen(false); }}
          >
            <span className="vocab-nav-icon">📖</span> Codex Archive
          </button>
          <button
            className={`vocab-nav-btn ${activeTab === 'tree' ? 'is-active' : ''}`}
            type="button"
            onClick={() => { setActiveTab('tree'); setIsFormOpen(false); }}
          >
            <span className="vocab-nav-icon">🌿</span> Word Network Tree
          </button>
          <button
            className={`vocab-nav-btn ${activeTab === 'flashcard' ? 'is-active' : ''}`}
            type="button"
            onClick={() => { setActiveTab('flashcard'); setIsFormOpen(false); }}
          >
            <span className="vocab-nav-icon">🧠</span> Flashcard Gate
            {dueFlashcards.length > 0 && <span className="vocab-badge-count">{dueFlashcards.length}</span>}
          </button>
          <button
            className={`vocab-nav-btn ${activeTab === 'forge' ? 'is-active' : ''}`}
            type="button"
            onClick={() => { setActiveTab('forge'); setIsFormOpen(false); }}
          >
            <span className="vocab-nav-icon">🔨</span> Collocation Forge
          </button>
          <button
            className={`vocab-nav-btn ${activeTab === 'shadow-duel' ? 'is-active' : ''}`}
            type="button"
            onClick={() => { setActiveTab('shadow-duel'); setIsFormOpen(false); }}
          >
            <span className="vocab-nav-icon">⚔️</span> Shadow Duel
          </button>
          <button
            className={`vocab-nav-btn ${activeTab === 'word-family' ? 'is-active' : ''}`}
            type="button"
            onClick={() => { setActiveTab('word-family'); setIsFormOpen(false); }}
          >
            <span className="vocab-nav-icon">🧬</span> Word Family
          </button>
          <button
            className={`vocab-nav-btn ${activeTab === 'echo-chamber' ? 'is-active' : ''}`}
            type="button"
            onClick={() => { setActiveTab('echo-chamber'); setIsFormOpen(false); }}
          >
            <span className="vocab-nav-icon">🎙️</span> Echo Chamber
          </button>
          <button
            className={`vocab-nav-btn ${activeTab === 'dungeon' ? 'is-active' : ''}`}
            type="button"
            onClick={() => { setActiveTab('dungeon'); setIsFormOpen(false); }}
          >
            <span className="vocab-nav-icon">🏰</span> Error Dungeon
            {activeErrors.length > 0 && <span className="vocab-badge-count danger">{activeErrors.length}</span>}
          </button>
          <button
            className={`vocab-nav-btn ${activeTab === 'boss' ? 'is-active' : ''}`}
            type="button"
            onClick={() => { setActiveTab('boss'); setIsFormOpen(false); }}
          >
            <span className="vocab-nav-icon">👹</span> Boss Battles
          </button>
        </nav>
      </aside>

      <main className="vocab-content">
        {error && <div className="vocab-error-banner">{error}</div>}

        {activeTab === 'codex' && (
          <div className="codex-tab">
            <div className="codex-controls">
              <input
                type="text"
                placeholder="Filter Codex word archive..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="system-input search-input"
              />
              <button className="system-button system-button--primary" onClick={handleOpenCreate}>
                + Awaken New Word
              </button>
            </div>

            {isFormOpen && (
              <form onSubmit={handleSubmit} className="vocab-form">
                <h3>{editingItem ? 'Update Lexical Item' : 'Register Discovered Word'}</h3>
                
                <div className="form-grid">
                  <label>
                    <span>Word / Phrase</span>
                    <input
                      type="text"
                      value={form.word}
                      onChange={(e) => setForm({ ...form, word: e.target.value })}
                      required
                      className="system-input"
                    />
                  </label>
                  <label>
                    <span>Part of Speech</span>
                    <select
                      value={form.part_of_speech}
                      onChange={(e) => setForm({ ...form, part_of_speech: e.target.value })}
                      className="system-input"
                    >
                      <option value="noun">Noun (n)</option>
                      <option value="verb">Verb (v)</option>
                      <option value="adjective">Adjective (adj)</option>
                      <option value="adverb">Adverb (adv)</option>
                      <option value="preposition">Preposition (prep)</option>
                      <option value="phrase">Phrase</option>
                    </select>
                  </label>
                  <label>
                    <span>CEFR Level</span>
                    <input
                      type="text"
                      value={form.cefr_level}
                      onChange={(e) => setForm({ ...form, cefr_level: e.target.value })}
                      placeholder="B2, C1..."
                      className="system-input"
                    />
                  </label>
                  <label>
                    <span>IELTS Topic</span>
                    <input
                      type="text"
                      value={form.ielts_topic}
                      onChange={(e) => setForm({ ...form, ielts_topic: e.target.value })}
                      placeholder="Education, Technology..."
                      className="system-input"
                    />
                  </label>
                  <label>
                    <span>Pronunciation (IPA)</span>
                    <input
                      type="text"
                      value={form.pronunciation_ipa}
                      onChange={(e) => setForm({ ...form, pronunciation_ipa: e.target.value })}
                      placeholder="/.../"
                      className="system-input"
                    />
                  </label>
                  <label>
                    <span>Word Stress (Syllables/Info)</span>
                    <input
                      type="text"
                      value={form.word_stress}
                      onChange={(e) => setForm({ ...form, word_stress: e.target.value })}
                      placeholder="e.g. 2nd syllable"
                      className="system-input"
                    />
                  </label>
                </div>

                <label className="textarea-label">
                  <span>Meaning (English)</span>
                  <textarea
                    value={form.meaning_en}
                    onChange={(e) => setForm({ ...form, meaning_en: e.target.value })}
                    className="system-input"
                    rows={2}
                  />
                </label>

                <label className="textarea-label">
                  <span>Meaning (Vietnamese)</span>
                  <textarea
                    value={form.meaning_vi}
                    onChange={(e) => setForm({ ...form, meaning_vi: e.target.value })}
                    className="system-input"
                    rows={2}
                  />
                </label>

                <div className="form-actions">
                  <button type="button" className="system-button" onClick={() => setIsFormOpen(false)}>
                    Cancel
                  </button>
                  <button type="submit" className="system-button system-button--primary" disabled={submitting}>
                    {submitting ? 'Awakening...' : editingItem ? 'Update Word' : 'Awaken Word'}
                  </button>
                </div>
              </form>
            )}

            {loading && <div className="vocab-loader">Loading Codex Archive...</div>}

            {!loading && filteredItems.length === 0 && (
              <div className="vocab-empty-state">No words found in this sector of the Codex.</div>
            )}

            <div className="codex-grid">
              {filteredItems.map((item) => (
                <div key={item.id} className="codex-card">
                  <div className="codex-card-header">
                    <div>
                      <h4>{item.word}</h4>
                      <span className="vocab-tag tag-speech">{item.part_of_speech}</span>
                      {item.cefr_level && <span className="vocab-tag tag-level">{item.cefr_level}</span>}
                      {item.ielts_topic && <span className="vocab-tag tag-topic">{item.ielts_topic}</span>}
                    </div>
                    <div className="codex-card-actions">
                      <button className="card-act-btn edit-btn" onClick={() => handleOpenEdit(item)}>
                        Edit
                      </button>
                      <button className="card-act-btn delete-btn" onClick={() => handleDelete(item.id)}>
                        Delete
                      </button>
                    </div>
                  </div>

                  <div className="codex-card-body">
                    {item.pronunciation_ipa && (
                      <p className="vocab-ipa">
                        <strong>IPA:</strong> {item.pronunciation_ipa} {item.word_stress ? `(${item.word_stress})` : ''}
                      </p>
                    )}
                    {item.meaning_en && (
                      <p className="vocab-meaning">
                        <strong>EN:</strong> {item.meaning_en}
                      </p>
                    )}
                    {item.meaning_vi && (
                      <p className="vocab-meaning">
                        <strong>VI:</strong> {item.meaning_vi}
                      </p>
                    )}

                    {/* Collocations */}
                    <div className="vocab-detail-section">
                      <h5>Collocations</h5>
                      {item.collocations?.length > 0 ? (
                        <ul className="vocab-list">
                          {item.collocations.map((col) => (
                            <li key={col.id}>
                              <code>{col.collocation}</code> ({col.collocation_type})
                              <button className="vocab-del-small" onClick={() => handleDeleteCollocation(col.id)}>
                                ×
                              </button>
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="vocab-none">No collocations forged.</p>
                      )}

                      {activeItemDetails === `col-${item.id}` ? (
                        <div className="small-add-form">
                          <input
                            type="text"
                            placeholder="e.g. significant impact"
                            value={collocationText}
                            onChange={(e) => setCollocationText(e.target.value)}
                            className="system-input small-input"
                          />
                          <select
                            value={collocationType}
                            onChange={(e) => setCollocationType(e.target.value)}
                            className="system-input small-select"
                          >
                            <option value="adjective + noun">Adj + Noun</option>
                            <option value="verb + noun">Verb + Noun</option>
                            <option value="verb + preposition">Verb + Prep</option>
                            <option value="fixed phrase">Fixed Phrase</option>
                          </select>
                          <button
                            className="system-button system-button--primary small-btn"
                            onClick={() => handleAddCollocation(item.id)}
                          >
                            Add
                          </button>
                          <button className="system-button small-btn" onClick={() => setActiveItemDetails(null)}>
                            Cancel
                          </button>
                        </div>
                      ) : (
                        <button className="vocab-add-link" onClick={() => {
                          setActiveItemDetails(`col-${item.id}`)
                          setCollocationText('')
                        }}>
                          + Forge Collocation
                        </button>
                      )}
                    </div>

                    {/* Examples */}
                    <div className="vocab-detail-section">
                      <h5>Example Sentences</h5>
                      {item.examples?.length > 0 ? (
                        <ul className="vocab-list">
                          {item.examples.map((ex) => (
                            <li key={ex.id}>
                              <em>"{ex.example_sentence}"</em>
                              <button className="vocab-del-small" onClick={() => handleDeleteExample(ex.id)}>
                                ×
                              </button>
                            </li>
                          ))}
                        </ul>
                      ) : (
                        <p className="vocab-none">No custom examples recorded.</p>
                      )}

                      {activeItemDetails === `ex-${item.id}` ? (
                        <div className="small-add-form">
                          <input
                            type="text"
                            placeholder="Write example sentence..."
                            value={exampleText}
                            onChange={(e) => setExampleText(e.target.value)}
                            className="system-input small-input"
                            style={{ flex: 1 }}
                          />
                          <button
                            className="system-button system-button--primary small-btn"
                            onClick={() => handleAddExample(item.id)}
                          >
                            Add
                          </button>
                          <button className="system-button small-btn" onClick={() => setActiveItemDetails(null)}>
                            Cancel
                          </button>
                        </div>
                      ) : (
                        <button className="vocab-add-link" onClick={() => {
                          setActiveItemDetails(`ex-${item.id}`)
                          setExampleText('')
                        }}>
                          + Add Example Sentence
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'flashcard' && (
          <div className="flashcard-tab">
            {activeReview ? (
              <div className="flashcard-gate-active">
                {activeReview.completed ? (
                  <div className="gate-victory-screen">
                    <div className="victory-badge">GATE CLEARED</div>
                    <h4>LEXICAL AWAKENING SUCCESSFUL</h4>
                    <p>You have reviewed all due vocabulary items in this session.</p>
                    <div className="victory-stat">
                      <strong>+{reviewXpEarned * 10}</strong>
                      <span>Support Skill XP Gained</span>
                    </div>
                    <button className="system-button system-button--primary gate-exit-btn" onClick={handleCloseReview}>
                      Close Gate
                    </button>
                  </div>
                ) : (
                  <div className="card-arena">
                    <div className="arena-header">
                      <span>MEMORY GATE DUEL</span>
                      <span>
                        Card {activeReview.currentIndex + 1} of {activeReview.cards.length}
                      </span>
                    </div>

                    <div className={`flip-card ${showAnswer ? 'is-flipped' : ''}`}>
                      <div className="flip-card-inner">
                        <div className="flip-card-front">
                          <div className="card-title">Recall Meaning</div>
                          {activeReview.cards[activeReview.currentIndex].vocabulary_item ? (
                            <div className="card-vocab-details">
                              <h2 className="card-vocab-word">
                                {activeReview.cards[activeReview.currentIndex].vocabulary_item.word}
                              </h2>
                              <div className="card-metadata-row" style={{ display: 'flex', justifyContent: 'center', gap: '8px', marginBottom: '12px' }}>
                                {activeReview.cards[activeReview.currentIndex].vocabulary_item.part_of_speech && (
                                  <span className="card-pos-badge" style={{ padding: '2px 8px', borderRadius: '4px', fontSize: '0.8rem', background: '#3b82f6', color: '#fff' }}>
                                    {activeReview.cards[activeReview.currentIndex].vocabulary_item.part_of_speech}
                                  </span>
                                )}
                                {activeReview.cards[activeReview.currentIndex].vocabulary_item.pronunciation_ipa && (
                                  <span className="card-pronunciation" style={{ fontStyle: 'italic', color: '#9ca3af' }}>
                                    {activeReview.cards[activeReview.currentIndex].vocabulary_item.pronunciation_ipa}
                                  </span>
                                )}
                              </div>
                            </div>
                          ) : (
                            <h2 className="card-vocab-word">
                              {activeReview.cards[activeReview.currentIndex].front_text}
                            </h2>
                          )}
                          {activeReview.cards[activeReview.currentIndex].hint && (
                            <p className="card-hint">
                              <strong>Hint:</strong> {activeReview.cards[activeReview.currentIndex].hint}
                            </p>
                          )}
                          <button className="system-button reveal-btn" onClick={() => setShowAnswer(true)}>
                            Reveal Definition
                          </button>
                        </div>
                        <div className="flip-card-back">
                          <div className="card-title">Definition</div>
                          {activeReview.cards[activeReview.currentIndex].vocabulary_item ? (
                            <div className="card-back-details" style={{ textAlign: 'left', width: '100%' }}>
                              <div className="definition-box" style={{ marginBottom: '12px' }}>
                                {activeReview.cards[activeReview.currentIndex].vocabulary_item.meaning_en && (
                                  <p className="meaning-en" style={{ margin: '4px 0' }}>
                                    <strong>EN:</strong> {activeReview.cards[activeReview.currentIndex].vocabulary_item.meaning_en}
                                  </p>
                                )}
                                {activeReview.cards[activeReview.currentIndex].vocabulary_item.meaning_vi && (
                                  <p className="meaning-vi" style={{ margin: '4px 0', color: '#a7f3d0' }}>
                                    <strong>VI:</strong> {activeReview.cards[activeReview.currentIndex].vocabulary_item.meaning_vi}
                                  </p>
                                )}
                              </div>
                              
                              {activeReview.cards[activeReview.currentIndex].vocabulary_item.examples && 
                               activeReview.cards[activeReview.currentIndex].vocabulary_item.examples.length > 0 && (
                                <div className="example-box" style={{ background: 'rgba(0,0,0,0.2)', padding: '8px', borderRadius: '4px', marginTop: '8px' }}>
                                  <strong>Example Sentence:</strong>
                                  <p className="example-text" style={{ fontStyle: 'italic', margin: '4px 0' }}>
                                    "{activeReview.cards[activeReview.currentIndex].vocabulary_item.examples[0].example_sentence}"
                                  </p>
                                  {activeReview.cards[activeReview.currentIndex].vocabulary_item.examples[0].example_meaning && (
                                    <p className="example-translation" style={{ color: '#9ca3af', fontSize: '0.9rem', margin: '0' }}>
                                      ↳ {activeReview.cards[activeReview.currentIndex].vocabulary_item.examples[0].example_meaning}
                                    </p>
                                  )}
                                </div>
                              )}

                              {activeReview.cards[activeReview.currentIndex].vocabulary_item.collocations && 
                               activeReview.cards[activeReview.currentIndex].vocabulary_item.collocations.length > 0 && (
                                <div className="example-box" style={{ background: 'rgba(0,0,0,0.2)', padding: '8px', borderRadius: '4px', marginTop: '8px' }}>
                                  <strong>Collocation:</strong>
                                  <p className="example-text" style={{ fontStyle: 'italic', margin: '4px 0' }}>
                                    "{activeReview.cards[activeReview.currentIndex].vocabulary_item.collocations[0].collocation}"
                                  </p>
                                  {activeReview.cards[activeReview.currentIndex].vocabulary_item.collocations[0].example_sentence && (
                                    <p className="colloc-ex" style={{ fontStyle: 'italic', color: '#9ca3af', margin: '4px 0 0 0' }}>
                                      e.g., "{activeReview.cards[activeReview.currentIndex].vocabulary_item.collocations[0].example_sentence}"
                                    </p>
                                  )}
                                  {activeReview.cards[activeReview.currentIndex].vocabulary_item.collocations[0].example_meaning && (
                                    <p className="example-translation" style={{ color: '#9ca3af', fontSize: '0.9rem', margin: '0' }}>
                                      ↳ {activeReview.cards[activeReview.currentIndex].vocabulary_item.collocations[0].example_meaning}
                                    </p>
                                  )}
                                </div>
                              )}
                            </div>
                          ) : (
                            <pre className="card-back-text">
                              {activeReview.cards[activeReview.currentIndex].back_text}
                            </pre>
                          )}
                          
                          <div className="difficulty-selectors">
                            <button
                              className="system-button review-act-btn again"
                              onClick={() => handleReviewAction('again')}
                            >
                              Again <small>+0 XP</small>
                            </button>
                            <button
                              className="system-button review-act-btn hard"
                              onClick={() => handleReviewAction('hard')}
                            >
                              Hard <small>+10 XP</small>
                            </button>
                            <button
                              className="system-button review-act-btn good"
                              onClick={() => handleReviewAction('good')}
                            >
                              Good <small>+20 XP</small>
                            </button>
                            <button
                              className="system-button review-act-btn easy"
                              onClick={() => handleReviewAction('easy')}
                            >
                              Easy <small>+30 XP</small>
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="flashcard-gate-lobby">
                <div className="gate-crest">
                  <span className="gate-crest-icon">🧠</span>
                  <h3>DAILY MEMORY GATE</h3>
                  <p>Revise due flashcards to anchor their meaning and collocations.</p>
                </div>

                <div className="gate-status-panel">
                  <div className="gate-stat-row">
                    <span>Gate Status:</span>
                    <strong className={dueFlashcards.length > 0 ? 'text-amber' : 'text-success'}>
                      {dueFlashcards.length > 0 ? 'ACTIVE (MONSTERS DETECTED)' : 'SECURED'}
                    </strong>
                  </div>
                  <div className="gate-stat-row">
                    <span>Due Cards:</span>
                    <strong>{dueFlashcards.length}</strong>
                  </div>
                </div>

                {dueFlashcards.length > 0 ? (
                  <button className="system-button system-button--primary gate-enter-btn" onClick={handleStartReview}>
                    ENTER THE GATE
                  </button>
                ) : (
                  <div className="gate-clear-message">
                    All memory gates are secured. Discover new words to unlock more gates!
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {activeTab === 'tree' && (
          <WordNetworkTree
            api={api}
            vocabularyItems={vocabularyItems}
            onLoadData={loadData}
          />
        )}

        {activeTab === 'forge' && (
          <CollocationForge api={api} onXPUpdate={(xp) => {
            console.log("Earned XP in Forge:", xp)
            if (onLoadData) onLoadData()
          }} />
        )}

        {activeTab === 'shadow-duel' && (
          <ShadowDuel api={api} onXPUpdate={(xp) => {
            console.log("Earned XP in Shadow Duel:", xp)
            if (onLoadData) onLoadData()
          }} />
        )}

        {activeTab === 'word-family' && (
          <WordFamilyEvolution api={api} onXPUpdate={(xp) => {
            console.log("Earned XP in Word Family:", xp)
            if (onLoadData) onLoadData()
          }} />
        )}

        {activeTab === 'echo-chamber' && (
          <EchoChamber api={api} onXPUpdate={(xp) => {
            console.log("Earned XP in Echo Chamber:", xp)
            if (onLoadData) onLoadData()
          }} />
        )}

        {activeTab === 'dungeon' && (
          <ErrorDungeon
            activeErrors={activeErrors}
            api={api}
            onRefresh={loadData}
          />
        )}

        {activeTab === 'boss' && (
          <VocabularyBoss
            bossStatus={bossStatus}
            api={api}
            onRefresh={loadData}
          />
        )}
      </main>
    </div>
  )
}

export default VocabularyWorkspace
