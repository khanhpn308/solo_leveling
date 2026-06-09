import { useState, useEffect } from 'react'

// Familiarity → neon CSS class
function neonClass(familiarity) {
  switch (familiarity) {
    case 'easy': return 'coll-neon-easy'
    case 'good': return 'coll-neon-good'
    case 'hard': return 'coll-neon-hard'
    default:     return 'coll-neon-again'
  }
}

function familiarityLabel(familiarity) {
  switch (familiarity) {
    case 'easy': return '★ Graduated'
    case 'good': return '◆ Good'
    case 'hard': return '◈ Hard'
    default:     return '○ New'
  }
}

function CollocationForge({ api }) {
  const [topics, setTopics] = useState([])
  const [selectedTopic, setSelectedTopic] = useState(null)
  const [items, setItems] = useState([])
  const [loadingTopics, setLoadingTopics] = useState(true)
  const [loadingItems, setLoadingItems] = useState(false)
  const [error, setError] = useState('')
  const [actionLoading, setActionLoading] = useState({})

  useEffect(() => {
    loadTopics()
  }, [])

  async function loadTopics() {
    try {
      setLoadingTopics(true)
      const data = await api('/collocations/topics')
      setTopics(data)
    } catch (err) {
      setError(err.message || 'Failed to load topics')
    } finally {
      setLoadingTopics(false)
    }
  }

  async function loadItems(topic) {
    try {
      setLoadingItems(true)
      setSelectedTopic(topic)
      setItems([])
      const data = await api(`/collocations/topics/${topic.id}/items`)
      setItems(data)
    } catch (err) {
      setError(err.message || 'Failed to load items')
    } finally {
      setLoadingItems(false)
    }
  }

  async function handleAddFlashcard(itemId) {
    try {
      setActionLoading(prev => ({ ...prev, [itemId]: true }))
      await api(`/collocations/${itemId}/flashcard`, { method: 'POST' })
      // Refresh items to update is_added and effective_familiarity
      if (selectedTopic) {
        const data = await api(`/collocations/topics/${selectedTopic.id}/items`)
        setItems(data)
      }
    } catch (err) {
      setError(err.message || 'Failed to add flashcard')
    } finally {
      setActionLoading(prev => ({ ...prev, [itemId]: false }))
    }
  }

  async function handleRemoveFlashcard(itemId) {
    try {
      setActionLoading(prev => ({ ...prev, [itemId]: true }))
      await api(`/collocations/${itemId}/flashcard`, { method: 'DELETE' })
      if (selectedTopic) {
        const data = await api(`/collocations/topics/${selectedTopic.id}/items`)
        setItems(data)
      }
    } catch (err) {
      setError(err.message || 'Failed to remove flashcard')
    } finally {
      setActionLoading(prev => ({ ...prev, [itemId]: false }))
    }
  }

  return (
    <div className="coll-browser">
      <div className="coll-browser__header">
        <h3 className="coll-browser__title">
          <span className="coll-browser__icon">📚</span>
          Collocation Browser
        </h3>
        <p className="coll-browser__subtitle">
          Browse collocations by topic. Add items to your flashcard deck to start reviewing.
        </p>
      </div>

      {error && <div className="vocab-error-banner">{error}</div>}

      <div className="coll-browser__body">
        {/* Topic list sidebar */}
        <aside className="coll-topic-list">
          <div className="coll-topic-list__head">Topics</div>
          {loadingTopics && <div className="coll-topic-list__loading">Loading…</div>}
          {!loadingTopics && topics.length === 0 && (
            <div className="coll-topic-list__empty">No topics linked to your campaign.</div>
          )}
          {topics.map(topic => (
            <button
              key={topic.id}
              className={`coll-topic-btn ${selectedTopic?.id === topic.id ? 'is-active' : ''}`}
              onClick={() => loadItems(topic)}
              type="button"
            >
              <span className="coll-topic-btn__title">{topic.title}</span>
              <span className="coll-topic-btn__meta">{topic.section_title} · {topic.item_count} items</span>
            </button>
          ))}
        </aside>

        {/* Items panel */}
        <main className="coll-items-panel">
          {!selectedTopic && (
            <div className="coll-items-empty">
              <div className="coll-items-empty__icon">👈</div>
              <p>Select a topic from the left to browse its collocations.</p>
            </div>
          )}

          {selectedTopic && loadingItems && (
            <div className="coll-items-loading">Loading collocations…</div>
          )}

          {selectedTopic && !loadingItems && items.length === 0 && (
            <div className="coll-items-empty">No collocations found in this topic.</div>
          )}

          {selectedTopic && !loadingItems && items.length > 0 && (
            <div className="coll-items-grid">
              {items.map(item => {
                const loading = actionLoading[item.id]
                return (
                  <div
                    key={item.id}
                    className={`coll-item-card ${neonClass(item.effective_familiarity)}`}
                  >
                    <div className="coll-item-card__header">
                      <h4 className="coll-item-card__word">{item.collocation}</h4>
                      <div className="coll-item-card__badges">
                        {item.collocation_type && (
                          <span className="coll-tag coll-tag--type">{item.collocation_type}</span>
                        )}
                        {item.is_added && (
                          <span className={`coll-tag coll-tag--fam ${neonClass(item.effective_familiarity)}`}>
                            {familiarityLabel(item.effective_familiarity)}
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="coll-item-card__body">
                      {item.pronunciation_us && (
                        <p className="coll-item-card__pron">/{item.pronunciation_us}/</p>
                      )}
                      {item.meaning_vi && (
                        <p className="coll-item-card__meaning">{item.meaning_vi}</p>
                      )}
                      {item.example_en && (
                        <p className="coll-item-card__example">
                          <em>"{item.example_en}"</em>
                        </p>
                      )}
                      {item.example_vi && (
                        <p className="coll-item-card__example-vi">↳ {item.example_vi}</p>
                      )}
                    </div>

                    <div className="coll-item-card__footer">
                      {!item.is_added ? (
                        <button
                          className="system-button system-button--primary coll-add-btn"
                          onClick={() => handleAddFlashcard(item.id)}
                          disabled={loading}
                        >
                          {loading ? '…' : '+ Add to Flashcard'}
                        </button>
                      ) : (
                        <div className="coll-added-row">
                          <span className="coll-added-badge">✓ Added</span>
                          {item.effective_familiarity !== 'easy' && (
                            <button
                              className="system-button coll-remove-btn"
                              onClick={() => handleRemoveFlashcard(item.id)}
                              disabled={loading}
                            >
                              {loading ? '…' : 'Remove'}
                            </button>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </main>
      </div>
    </div>
  )
}

export default CollocationForge
