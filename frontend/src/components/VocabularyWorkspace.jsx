import { useState, useEffect, useMemo } from 'react'
import WordNetworkTree from './WordNetworkTree'
import CollocationForge from './CollocationForge'
import ShadowDuel from './ShadowDuel'
import WordFamilyEvolution from './WordFamilyEvolution'
import EchoChamber from './EchoChamber'
import ErrorDungeon from './ErrorDungeon'
import VocabularyBoss from './VocabularyBoss'
import VocabularyLibrary from './VocabularyLibrary'

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

// I4-4: Collocation Flashcard Review inline component
function CollocationFlashcardReview({
  api,
  topics, setTopics,
  cards, setCards,
  cardIndex, setCardIndex,
  showAnswer, setShowAnswer,
  completed, setCompleted,
  selectedTopic, setSelectedTopic,
  loading, setLoading,
}) {
  const [reviewError, setReviewError] = useState('')

  async function loadCards(topic) {
    try {
      setLoading(true)
      setSelectedTopic(topic)
      setCards([])
      setCardIndex(0)
      setShowAnswer(false)
      setCompleted(false)
      const data = await api(`/collocations/flashcard/topics/${topic.id}`)
      setCards(data)
    } catch (err) {
      setReviewError(err.message || 'Failed to load flashcard items')
    } finally {
      setLoading(false)
    }
  }

  async function handleReview(result) {
    if (!cards.length) return
    const item = cards[cardIndex]
    try {
      const res = await api(`/collocations/${item.id}/flashcard/review`, {
        method: 'POST',
        body: JSON.stringify({ result }),
      })
      if (res.collocation_forge_autocompleted) {
        console.log('[I4-7] Collocation Forge daily quest auto-completed!')
      }
    } catch (err) {
      console.error('Failed to submit review:', err)
    }
    const nextIndex = cardIndex + 1
    if (nextIndex >= cards.length) {
      setCompleted(true)
    } else {
      setCardIndex(nextIndex)
      setShowAnswer(false)
    }
  }

  function handleRestart() {
    setSelectedTopic(null)
    setCards([])
    setCardIndex(0)
    setShowAnswer(false)
    setCompleted(false)
    // Refresh topics
    api('/collocations/flashcard/topics').then(data => setTopics(data)).catch(() => {})
  }

  // Topic selection screen
  if (!selectedTopic) {
    return (
      <div className="coll-flash-lobby">
        <div className="gate-crest">
          <span className="gate-crest-icon">📚</span>
          <h3>COLLOCATION REVIEW</h3>
          <p>Choose a topic to review your added collocations.</p>
        </div>
        {loading && <div className="coll-topic-list__loading">Loading topics…</div>}
        {!loading && topics.length === 0 && (
          <div className="gate-clear-message">
            No collocation flashcards added yet. Browse the <strong>Collocations</strong> tab to add cards.
          </div>
        )}
        <div className="coll-flash-topic-grid">
          {topics.map(topic => (
            <button
              key={topic.id}
              className="coll-flash-topic-btn"
              onClick={() => loadCards(topic)}
            >
              <span className="coll-flash-topic-btn__title">{topic.title}</span>
              <span className="coll-flash-topic-btn__count">{topic.card_count} cards</span>
              <span className="coll-flash-topic-btn__section">{topic.section_title}</span>
            </button>
          ))}
        </div>
        {reviewError && <div className="vocab-error-banner">{reviewError}</div>}
      </div>
    )
  }

  // Completed screen
  if (completed) {
    return (
      <div className="gate-victory-screen">
        <div className="victory-badge">SESSION COMPLETE</div>
        <h4>COLLOCATION REVIEW DONE</h4>
        <p>You reviewed all collocations in <strong>{selectedTopic.title}</strong>.</p>
        <button className="system-button system-button--primary gate-exit-btn" onClick={handleRestart}>
          Back to Topics
        </button>
      </div>
    )
  }

  // Card loading
  if (loading) {
    return <div className="coll-items-loading">Loading cards…</div>
  }

  if (!cards.length) {
    return (
      <div className="coll-items-empty">
        <p>No non-graduated cards found in this topic.</p>
        <button className="system-button" onClick={handleRestart}>Back</button>
      </div>
    )
  }

  const item = cards[cardIndex]
  const neonCls = item.effective_familiarity === 'easy' ? 'coll-neon-easy'
    : item.effective_familiarity === 'good' ? 'coll-neon-good'
    : item.effective_familiarity === 'hard' ? 'coll-neon-hard'
    : 'coll-neon-again'

  return (
    <div className="card-arena">
      <div className="arena-header">
        <button className="system-button" onClick={handleRestart} style={{ fontSize: '0.8rem', padding: '4px 10px' }}>
          ← Topics
        </button>
        <span>Collocation {cardIndex + 1} of {cards.length}</span>
      </div>
      <div
        className={`flip-card coll-review-card ${neonCls} ${showAnswer ? 'is-flipped' : ''}`}
        role="button"
        tabIndex={0}
        aria-pressed={showAnswer}
        aria-label="Flashcard, click to flip"
        onClick={() => setShowAnswer(s => !s)}
        onKeyDown={e => {
          if (e.key === 'Enter') setShowAnswer(s => !s)
          if (e.key === ' ') { e.preventDefault(); setShowAnswer(s => !s) }
        }}
      >
        <div className="flip-card-inner">
          <div className="flip-card-front">
            <div className="card-title">Collocation</div>
            <h2 className="card-vocab-word">{item.collocation}</h2>
            {item.pronunciation_us && (
              <p style={{ fontStyle: 'italic', color: '#9ca3af', margin: '4px 0' }}>/{item.pronunciation_us}/</p>
            )}
            {item.collocation_type && (
              <span className="coll-tag coll-tag--type">{item.collocation_type}</span>
            )}
          </div>
          <div className="flip-card-back">
            <div className="card-title">Meaning</div>
            <h2 className="card-vocab-word" style={{ fontSize: '1.4rem', marginBottom: '8px' }}>{item.collocation}</h2>
            {item.meaning_vi && (
              <p className="meaning-vi" style={{ color: '#a7f3d0', margin: '4px 0' }}>{item.meaning_vi}</p>
            )}
            {item.example_en && (
              <p style={{ fontStyle: 'italic', margin: '8px 0 4px' }}>"{item.example_en}"</p>
            )}
            {item.example_vi && (
              <p style={{ color: '#9ca3af', fontSize: '0.9rem' }}>↳ {item.example_vi}</p>
            )}
            <div className="difficulty-selectors" style={{ marginTop: '16px' }}>
              <button className="system-button review-act-btn again" onClick={e => { e.stopPropagation(); handleReview('again') }}>Again</button>
              <button className="system-button review-act-btn hard" onClick={e => { e.stopPropagation(); handleReview('hard') }}>Hard</button>
              <button className="system-button review-act-btn good" onClick={e => { e.stopPropagation(); handleReview('good') }}>Good</button>
              <button className="system-button review-act-btn easy" onClick={e => { e.stopPropagation(); handleReview('easy') }}>Easy ★</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
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

  // Flashcard sub-tab state (I4-4)
  const [flashSubTab, setFlashSubTab] = useState('vocabulary') // 'vocabulary' | 'collocation'

  // Collocation flashcard review state (I4-4)
  const [collFlashTopics, setCollFlashTopics] = useState([])
  const [collFlashCards, setCollFlashCards] = useState([])
  const [collFlashCardIndex, setCollFlashCardIndex] = useState(0)
  const [collFlashShowAnswer, setCollFlashShowAnswer] = useState(false)
  const [collFlashCompleted, setCollFlashCompleted] = useState(false)
  const [collFlashSelectedTopic, setCollFlashSelectedTopic] = useState(null)
  const [collFlashLoading, setCollFlashLoading] = useState(false)

  // Vocab Library flashcard review state
  const [vlFlashCards, setVlFlashCards] = useState([])
  const [vlFlashLoading, setVlFlashLoading] = useState(false)
  const [vlFlashCardIndex, setVlFlashCardIndex] = useState(0)
  const [vlFlashShowAnswer, setVlFlashShowAnswer] = useState(false)
  const [vlFlashCompleted, setVlFlashCompleted] = useState(false)
  const [vlFlashSelectedTopic, setVlFlashSelectedTopic] = useState(null) // {id, title, card_count} | null

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

  // Example add state
  const [activeItemDetails, setActiveItemDetails] = useState(null)
  const [exampleText, setExampleText] = useState('')

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

  // I4-4: Collocation flashcard loading helpers
  async function loadCollFlashTopics() {
    try {
      setCollFlashLoading(true)
      const data = await api('/collocations/flashcard/topics')
      setCollFlashTopics(data)
    } catch (err) {
      console.error('Failed to load collocation flashcard topics', err)
    } finally {
      setCollFlashLoading(false)
    }
  }

  async function loadVlFlashCards() {
    try {
      setVlFlashLoading(true)
      const data = await api('/vocab-library/flashcards/due')
      setVlFlashCards(data)
      setVlFlashSelectedTopic(null)
      setVlFlashCardIndex(0)
      setVlFlashShowAnswer(false)
      setVlFlashCompleted(false)
    } catch (err) {
      console.error('Failed to load vocab library flashcards', err)
    } finally {
      setVlFlashLoading(false)
    }
  }

  // Group due cards by topic for the lobby (mirrors collocation flashcard flow)
  const vlFlashTopics = useMemo(() => {
    const byTopic = new Map()
    for (const c of vlFlashCards) {
      const id = c.topic_id || 0
      if (!byTopic.has(id)) {
        byTopic.set(id, { id, title: c.topic_title || 'Uncategorized', card_count: 0 })
      }
      byTopic.get(id).card_count += 1
    }
    return [...byTopic.values()].sort((a, b) => a.id - b.id)
  }, [vlFlashCards])

  // Cards belonging to the currently selected topic (the active review deck)
  const vlActiveCards = useMemo(() => {
    if (!vlFlashSelectedTopic) return []
    return vlFlashCards.filter((c) => (c.topic_id || 0) === vlFlashSelectedTopic.id)
  }, [vlFlashCards, vlFlashSelectedTopic])

  function handleSelectVlTopic(topic) {
    setVlFlashSelectedTopic(topic)
    setVlFlashCardIndex(0)
    setVlFlashShowAnswer(false)
    setVlFlashCompleted(false)
  }

  function handleVlBackToTopics() {
    setVlFlashSelectedTopic(null)
    setVlFlashCardIndex(0)
    setVlFlashShowAnswer(false)
    setVlFlashCompleted(false)
    // Refresh due cards so topic counts reflect cards just reviewed
    loadVlFlashCards()
  }

  async function handleVlReview(result) {
    const card = vlActiveCards[vlFlashCardIndex]
    if (!card) return
    try {
      await api(`/vocab-library/words/${card.id}/flashcard/review`, {
        method: 'POST',
        body: JSON.stringify({ result }),
      })
    } catch (err) {
      console.error('Failed to review vocab library flashcard', err)
    }
    const next = vlFlashCardIndex + 1
    if (next >= vlActiveCards.length) {
      setVlFlashCompleted(true)
    } else {
      setVlFlashCardIndex(next)
      setVlFlashShowAnswer(false)
    }
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
            <span className="vocab-nav-icon">📚</span> Collocations
          </button>
          <button
            className={`vocab-nav-btn ${activeTab === 'library' ? 'is-active' : ''}`}
            type="button"
            onClick={() => { setActiveTab('library'); setIsFormOpen(false); }}
          >
            <span className="vocab-nav-icon">📕</span> Vocabulary Library
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
            {/* I4-4: sub-tab switcher */}
            <div className="flashcard-subtabs">
              <button
                className={`flashcard-subtab-btn ${flashSubTab === 'vocabulary' ? 'is-active' : ''}`}
                onClick={() => { setFlashSubTab('vocabulary') }}
              >🧠 Vocabulary</button>
              <button
                className={`flashcard-subtab-btn ${flashSubTab === 'collocation' ? 'is-active' : ''}`}
                onClick={() => {
                  setFlashSubTab('collocation')
                  if (collFlashTopics.length === 0) loadCollFlashTopics()
                }}
              >📚 Collocation</button>
              <button
                className={`flashcard-subtab-btn ${flashSubTab === 'vocab-library' ? 'is-active' : ''}`}
                onClick={() => {
                  setFlashSubTab('vocab-library')
                  if (vlFlashCards.length === 0 && !vlFlashCompleted) loadVlFlashCards()
                }}
              >📕 Vocab Library</button>
            </div>

            {/* Vocabulary sub-tab (unchanged) */}
            {flashSubTab === 'vocabulary' && (
              <>
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

                        <div
                          className={`flip-card ${showAnswer ? 'is-flipped' : ''}`}
                          role="button"
                          tabIndex={0}
                          aria-pressed={showAnswer}
                          aria-label="Flashcard, click to flip"
                          onClick={() => setShowAnswer(s => !s)}
                          onKeyDown={e => {
                            if (e.key === 'Enter') setShowAnswer(s => !s)
                            if (e.key === ' ') { e.preventDefault(); setShowAnswer(s => !s) }
                          }}
                        >
                          <div className="flip-card-inner">
                            <div className="flip-card-front">
                              <div className="card-title">Vocabulary</div>
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

                                </div>
                              ) : (
                                <pre className="card-back-text">
                                  {activeReview.cards[activeReview.currentIndex].back_text}
                                </pre>
                              )}

                              <div className="difficulty-selectors">
                                <button
                                  className="system-button review-act-btn again"
                                  onClick={e => { e.stopPropagation(); handleReviewAction('again') }}
                                >
                                  Again <small>+0 XP</small>
                                </button>
                                <button
                                  className="system-button review-act-btn hard"
                                  onClick={e => { e.stopPropagation(); handleReviewAction('hard') }}
                                >
                                  Hard <small>+10 XP</small>
                                </button>
                                <button
                                  className="system-button review-act-btn good"
                                  onClick={e => { e.stopPropagation(); handleReviewAction('good') }}
                                >
                                  Good <small>+20 XP</small>
                                </button>
                                <button
                                  className="system-button review-act-btn easy"
                                  onClick={e => { e.stopPropagation(); handleReviewAction('easy') }}
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
              </>
            )}

            {/* Collocation flashcard sub-tab (I4-4) */}
            {flashSubTab === 'collocation' && (
              <CollocationFlashcardReview
                api={api}
                topics={collFlashTopics}
                setTopics={setCollFlashTopics}
                cards={collFlashCards}
                setCards={setCollFlashCards}
                cardIndex={collFlashCardIndex}
                setCardIndex={setCollFlashCardIndex}
                showAnswer={collFlashShowAnswer}
                setShowAnswer={setCollFlashShowAnswer}
                completed={collFlashCompleted}
                setCompleted={setCollFlashCompleted}
                selectedTopic={collFlashSelectedTopic}
                setSelectedTopic={setCollFlashSelectedTopic}
                loading={collFlashLoading}
                setLoading={setCollFlashLoading}
              />
            )}

            {/* Vocab Library flashcard sub-tab */}
            {flashSubTab === 'vocab-library' && (
              <div className="flashcard-gate-active">
                {vlFlashLoading && <div className="vocab-loader">Loading Vocab Library cards…</div>}

                {/* Empty state: no due cards at all */}
                {!vlFlashLoading && vlFlashCards.length === 0 && (
                  <div className="flashcard-gate-empty">
                    <div className="gate-icon">📕</div>
                    <h4>No vocab library cards due</h4>
                    <p>Add words from <strong>Vocabulary Library</strong> to start reviewing.</p>
                  </div>
                )}

                {/* Topic lobby: choose a topic to review (mirrors collocation flow) */}
                {!vlFlashLoading && vlFlashCards.length > 0 && !vlFlashSelectedTopic && (
                  <div className="coll-flash-lobby">
                    <div className="gate-crest">
                      <span className="gate-crest-icon">📕</span>
                      <h3>VOCAB LIBRARY REVIEW</h3>
                      <p>Choose a topic to review your added vocabulary words.</p>
                    </div>
                    <div className="coll-flash-topic-grid">
                      {vlFlashTopics.map(topic => (
                        <button
                          key={topic.id}
                          className="coll-flash-topic-btn"
                          onClick={() => handleSelectVlTopic(topic)}
                        >
                          <span className="coll-flash-topic-btn__title">{topic.title}</span>
                          <span className="coll-flash-topic-btn__count">{topic.card_count} cards</span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}

                {/* Completed screen for the selected topic */}
                {!vlFlashLoading && vlFlashSelectedTopic && vlFlashCompleted && (
                  <div className="gate-victory-screen">
                    <div className="victory-badge">SESSION COMPLETE</div>
                    <h4>All cards reviewed!</h4>
                    <p>You reviewed all cards in <strong>{vlFlashSelectedTopic.title}</strong>.</p>
                    <button className="system-button system-button--primary gate-exit-btn" onClick={handleVlBackToTopics}>
                      Back to Topics
                    </button>
                  </div>
                )}

                {/* Review loop for the selected topic */}
                {!vlFlashLoading && vlFlashSelectedTopic && !vlFlashCompleted && vlActiveCards.length > 0 && (() => {
                  const card = vlActiveCards[vlFlashCardIndex]
                  if (!card) return null
                  return (
                    <div className="card-arena">
                      <div className="arena-header">
                        <button className="system-button" onClick={handleVlBackToTopics} style={{ fontSize: '0.8rem', padding: '4px 10px' }}>
                          ← Topics
                        </button>
                        <span>Card {vlFlashCardIndex + 1} of {vlActiveCards.length}</span>
                      </div>
                      <div
                        className={`flip-card ${vlFlashShowAnswer ? 'is-flipped' : ''}`}
                        role="button"
                        tabIndex={0}
                        aria-pressed={vlFlashShowAnswer}
                        onClick={() => setVlFlashShowAnswer(s => !s)}
                        onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); setVlFlashShowAnswer(s => !s) } }}
                      >
                        <div className="flip-card-inner">
                          <div className="flip-card-front">
                            <div className="card-title">Vocabulary Library</div>
                            <h2 className="card-vocab-word">{card.word}</h2>
                            {card.part_of_speech && <span className="card-pos-badge" style={{ padding: '2px 8px', borderRadius: '4px', fontSize: '0.8rem', background: '#3b82f6', color: '#fff' }}>{card.part_of_speech}</span>}
                            {card.pronunciation_us && <p className="card-pronunciation" style={{ fontStyle: 'italic', color: '#9ca3af' }}>/{card.pronunciation_us}/</p>}
                          </div>
                          <div className="flip-card-back">
                            <div className="card-title">Meaning</div>
                            {card.meaning_vi && <p className="card-meaning-vi" style={{ fontSize: '1.1rem', marginBottom: '8px' }}>{card.meaning_vi}</p>}
                            {card.example_en && <p className="card-example" style={{ fontStyle: 'italic', color: '#9ca3af', fontSize: '0.85rem' }}>"{card.example_en}"</p>}
                            {card.level_name && <p style={{ fontSize: '0.75rem', color: 'rgba(230,237,243,0.4)', marginTop: '8px' }}>{card.level_name} · {card.section_title}</p>}
                            {vlFlashShowAnswer && (
                              <div className="difficulty-selectors">
                                <button className="system-button review-act-btn again" onClick={e => { e.stopPropagation(); handleVlReview('again') }}>Again</button>
                                <button className="system-button review-act-btn hard" onClick={e => { e.stopPropagation(); handleVlReview('hard') }}>Hard</button>
                                <button className="system-button review-act-btn good" onClick={e => { e.stopPropagation(); handleVlReview('good') }}>Good</button>
                                <button className="system-button review-act-btn easy" onClick={e => { e.stopPropagation(); handleVlReview('easy') }}>Easy ★</button>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  )
                })()}
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

        {activeTab === 'library' && (
          <VocabularyLibrary api={api} />
        )}
      </main>
    </div>
  )
}

export default VocabularyWorkspace
