import { useState, useEffect, useMemo } from 'react'
import LevelBlock from './LevelBlock'

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

// Group flat topic list into [{ section_order, section_title, topics: [...] }]
function groupBySection(topics) {
  const map = new Map()
  for (const t of topics) {
    const key = t.section_order
    if (!map.has(key)) {
      map.set(key, {
        section_order: t.section_order,
        section_title: t.section_title || 'Untitled section',
        topics: [],
      })
    }
    map.get(key).topics.push(t)
  }
  return [...map.values()].sort((a, b) => a.section_order - b.section_order)
}

// Topic progress box: fills bottom-up by completion %, color shifts blue→yellow.
function TopicProgressBox({ topic, isActive, onSelect }) {
  const total = topic.item_count || 0
  const done = topic.completed_count || 0
  const pct = total > 0 ? Math.round((done / total) * 100) : 0

  return (
    <button
      type="button"
      className={`coll-topic-box ${isActive ? 'is-active' : ''}`}
      onClick={() => onSelect(topic)}
      aria-pressed={isActive}
      aria-label={`${topic.title}, ${pct}% complete, ${done} of ${total} collocations`}
      style={{ '--coll-ratio': pct / 100 }}
    >
      <span
        className="coll-topic-box__fill"
        style={{ '--coll-pct': `${pct}%` }}
        aria-hidden="true"
      />
      <span className="coll-topic-box__content">
        <span className="coll-topic-box__title">{topic.title}</span>
        <span className="coll-topic-box__stats">
          <span className="coll-topic-box__pct">{pct}%</span>
          <span className="coll-topic-box__frac">{done}/{total}</span>
        </span>
      </span>
    </button>
  )
}

// Compute section-level completion from topics list (topics now carry section_id)
function buildSectionStats(topics) {
  const map = new Map()
  for (const t of topics) {
    const sid = t.section_id || t.section_order
    if (!map.has(sid)) {
      map.set(sid, { completed: 0, total: 0 })
    }
    const s = map.get(sid)
    s.completed += t.completed_count || 0
    s.total += t.item_count || 0
  }
  return map
}

function CollocationForge({ api }) {
  const [levels, setLevels] = useState([])
  const [selectedLevel, setSelectedLevel] = useState(null)
  const [loadingLevels, setLoadingLevels] = useState(true)

  const [topics, setTopics] = useState([])
  const [selectedTopic, setSelectedTopic] = useState(null)
  const [items, setItems] = useState([])
  const [loadingTopics, setLoadingTopics] = useState(false)
  const [loadingItems, setLoadingItems] = useState(false)
  const [error, setError] = useState('')
  const [actionLoading, setActionLoading] = useState({})
  const [expandedSections, setExpandedSections] = useState(() => new Set())

  useEffect(() => {
    loadLevels()
  }, [])

  const sections = useMemo(() => groupBySection(topics), [topics])
  const sectionStats = useMemo(() => buildSectionStats(topics), [topics])

  async function loadLevels() {
    try {
      setLoadingLevels(true)
      const data = await api('/collocations/levels')
      setLevels(data)
    } catch (err) {
      setError(err.message || 'Failed to load levels')
    } finally {
      setLoadingLevels(false)
    }
  }

  async function loadTopics() {
    try {
      setLoadingTopics(true)
      const data = await api('/collocations/topics')
      setTopics(data)
      // Auto-expand the first section on initial load so the panel isn't empty.
      if (data.length > 0) {
        setExpandedSections(prev => {
          if (prev.size > 0) return prev
          return new Set([data[0].section_order])
        })
      }
    } catch (err) {
      setError(err.message || 'Failed to load topics')
    } finally {
      setLoadingTopics(false)
    }
  }

  function handleSelectLevel(level) {
    setSelectedLevel(level)
    setSelectedTopic(null)
    setItems([])
    setExpandedSections(new Set())
    loadTopics()
  }

  function handleBackToLevels() {
    setSelectedLevel(null)
    setSelectedTopic(null)
    setItems([])
    setExpandedSections(new Set())
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

  function toggleSection(sectionOrder) {
    setExpandedSections(prev => {
      const next = new Set(prev)
      if (next.has(sectionOrder)) next.delete(sectionOrder)
      else next.add(sectionOrder)
      return next
    })
  }

  // After a flashcard mutation, refresh both the open item list and the topic
  // progress counts (so the % box updates live).
  async function refreshAfterMutation() {
    if (selectedTopic) {
      const itemsData = await api(`/collocations/topics/${selectedTopic.id}/items`)
      setItems(itemsData)
    }
    const topicsData = await api('/collocations/topics')
    setTopics(topicsData)
  }

  async function handleAddFlashcard(itemId) {
    try {
      setActionLoading(prev => ({ ...prev, [itemId]: true }))
      await api(`/collocations/${itemId}/flashcard`, { method: 'POST' })
      await refreshAfterMutation()
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
      await refreshAfterMutation()
    } catch (err) {
      setError(err.message || 'Failed to remove flashcard')
    } finally {
      setActionLoading(prev => ({ ...prev, [itemId]: false }))
    }
  }

  // ── Level entry screen ──
  if (!selectedLevel) {
    return (
      <div className="coll-browser">
        <div className="coll-browser__header">
          <h3 className="coll-browser__title">
            <span className="coll-browser__icon">📚</span>
            Collocation Browser
          </h3>
          <p className="coll-browser__subtitle">
            Choose a level to start browsing collocations.
          </p>
        </div>
        {error && <div className="vocab-error-banner" role="alert">{error}</div>}
        {loadingLevels
          ? <div className="coll-topic-list__loading">Loading levels…</div>
          : (
            <div className="level-block-grid">
              {levels.map(lv => (
                <LevelBlock
                  key={lv.id}
                  level={lv}
                  onSelect={handleSelectLevel}
                  isActive={false}
                />
              ))}
            </div>
          )
        }
      </div>
    )
  }

  return (
    <div className="coll-browser">
      <div className="coll-browser__header">
        <h3 className="coll-browser__title">
          <button
            type="button"
            className="coll-back-btn"
            onClick={handleBackToLevels}
            aria-label="Back to levels"
          >← Levels</button>
          <span className="coll-browser__icon">{selectedLevel.icon}</span>
          {selectedLevel.name}
        </h3>
        <p className="coll-browser__subtitle">
          Pick a section, open a topic, and add collocations to your flashcard deck.
        </p>
      </div>

      {error && <div className="vocab-error-banner" role="alert">{error}</div>}

      {/* ── Layer 3: Items full-screen (replaces sidebar+panel when topic selected) ── */}
      {selectedTopic ? (
        <div className="coll-items-fullscreen">
          <div className="coll-items-fullscreen__head">
            <button
              type="button"
              className="coll-back-btn"
              onClick={() => { setSelectedTopic(null); setItems([]) }}
            >← Topics</button>
            <div className="coll-items-fullscreen__title-block">
              <h4 className="coll-items-panel__title">{selectedTopic.title}</h4>
              <span className="coll-items-panel__crumb">{selectedTopic.section_title}</span>
            </div>
          </div>

          {loadingItems && <div className="coll-items-loading">Loading collocations…</div>}

          {!loadingItems && items.length === 0 && (
            <div className="coll-items-empty">No collocations found in this topic.</div>
          )}

          {!loadingItems && items.length > 0 && (
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
        </div>
      ) : (
        <div className="coll-browser__body">
          {/* Two-level accordion sidebar: section → topic boxes */}
          <aside className="coll-section-nav" aria-label="Collocation sections">
            {loadingTopics && <div className="coll-topic-list__loading">Loading…</div>}
            {!loadingTopics && sections.length === 0 && (
              <div className="coll-topic-list__empty">No topics linked to your campaign.</div>
            )}

            {sections.map(section => {
              const isOpen = expandedSections.has(section.section_order)
              const statKey = section.topics[0]?.section_id || section.section_order
              const stat = sectionStats.get(statKey) || { completed: 0, total: 0 }
              const secPct = stat.total > 0 ? Math.round((stat.completed / stat.total) * 100) : 0
              const secRatio = secPct / 100

              return (
                <div key={section.section_order} className="coll-section-group">
                  <button
                    type="button"
                    className={`coll-section-btn ${isOpen ? 'is-open' : ''}`}
                    onClick={() => toggleSection(section.section_order)}
                    aria-expanded={isOpen}
                    style={{ '--coll-ratio': secRatio }}
                  >
                    <span className="coll-section-btn__chevron" aria-hidden="true">
                      {isOpen ? '▾' : '▸'}
                    </span>
                    <span className="coll-section-btn__title">{section.section_title}</span>
                    <span className="coll-section-btn__pct">{secPct}%</span>
                    <span className="coll-section-btn__count">{section.topics.length}</span>
                  </button>

                  {isOpen && (
                    <div className="coll-topic-box-grid">
                      {section.topics.map(topic => (
                        <TopicProgressBox
                          key={topic.id}
                          topic={topic}
                          isActive={false}
                          onSelect={loadItems}
                        />
                      ))}
                    </div>
                  )}
                </div>
              )
            })}
          </aside>

        </div>
      )}
    </div>
  )
}

export default CollocationForge
