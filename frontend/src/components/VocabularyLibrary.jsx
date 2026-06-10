import { useState, useEffect, useMemo } from "react"
import LevelBlock from "./LevelBlock"

// ── Neon box (reuse collocation pattern) for Topic/Unit/Section ──────────
function DrillBox({ item, label, pct, done, total, isActive, onSelect }) {
  const ratio = pct / 100
  return (
    <button
      type="button"
      className={`coll-topic-box ${isActive ? "is-active" : ""}`}
      onClick={() => onSelect(item)}
      aria-pressed={isActive}
      style={{ "--coll-ratio": ratio }}
    >
      <span className="coll-topic-box__fill" style={{ "--coll-pct": `${pct}%` }} aria-hidden="true" />
      <span className="coll-topic-box__content">
        <span className="coll-topic-box__title">{label}</span>
        <span className="coll-topic-box__stats">
          <span className="coll-topic-box__pct">{pct}%</span>
          <span className="coll-topic-box__frac">{done}/{total}</span>
        </span>
      </span>
    </button>
  )
}

// ── Word card ─────────────────────────────────────────────────────────────
function neonClass(fam) {
  switch (fam) {
    case "easy":  return "coll-neon-easy"
    case "good":  return "coll-neon-good"
    case "hard":  return "coll-neon-hard"
    default:      return "coll-neon-again"
  }
}
function famLabel(fam) {
  switch (fam) {
    case "easy":  return "★ Graduated"
    case "good":  return "◆ Good"
    case "hard":  return "◈ Hard"
    default:      return "○ New"
  }
}

function WordCard({ word, onAdd, onRemove, loading }) {
  return (
    <div className={`coll-item-card ${neonClass(word.effective_familiarity)}`}>
      <div className="coll-item-card__header">
        <h4 className="coll-item-card__word">{word.word}</h4>
        <div className="coll-item-card__badges">
          {word.part_of_speech && <span className="coll-tag coll-tag--type">{word.part_of_speech}</span>}
          {word.is_added && (
            <span className={`coll-tag coll-tag--fam ${neonClass(word.effective_familiarity)}`}>
              {famLabel(word.effective_familiarity)}
            </span>
          )}
        </div>
      </div>
      <div className="coll-item-card__body">
        {word.pronunciation_us && <p className="coll-item-card__pron">/{word.pronunciation_us}/</p>}
        {word.meaning_vi      && <p className="coll-item-card__meaning">{word.meaning_vi}</p>}
        {word.example_en      && <p className="coll-item-card__example"><em>"{word.example_en}"</em></p>}
        {word.example_vi      && <p className="coll-item-card__example-vi">↳ {word.example_vi}</p>}
      </div>
      <div className="coll-item-card__footer">
        {!word.is_added ? (
          <button className="system-button system-button--primary coll-add-btn" onClick={() => onAdd(word.id)} disabled={loading}>
            {loading ? "…" : "+ Add to Flashcard"}
          </button>
        ) : (
          <div className="coll-added-row">
            <span className="coll-added-badge">✓ Added</span>
            {word.effective_familiarity !== "easy" && (
              <button className="system-button coll-remove-btn" onClick={() => onRemove(word.id)} disabled={loading}>
                {loading ? "…" : "Remove"}
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

// ── Breadcrumb ────────────────────────────────────────────────────────────
function Breadcrumb({ crumbs, onBack }) {
  return (
    <div className="vl-breadcrumb">
      {crumbs.map((c, i) => (
        <span key={i} className="vl-breadcrumb__item">
          {i < crumbs.length - 1
            ? <button type="button" className="vl-breadcrumb__link" onClick={() => onBack(i)}>{c}</button>
            : <span className="vl-breadcrumb__current">{c}</span>
          }
          {i < crumbs.length - 1 && <span className="vl-breadcrumb__sep"> › </span>}
        </span>
      ))}
    </div>
  )
}

// ── Main component ────────────────────────────────────────────────────────
function VocabularyLibrary({ api }) {
  // Navigation stack: each entry is { type, data }
  // type: "levels" | "topics" | "units" | "sections" | "words"
  const [stack, setStack] = useState([{ type: "levels", data: [] }])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [actionLoading, setActionLoading] = useState({})

  const current = stack[stack.length - 1]

  useEffect(() => {
    if (current.type === "levels" && current.data.length === 0) {
      fetchLevels()
    }
  }, [])

  async function fetchLevels() {
    try {
      setLoading(true)
      const data = await api("/vocab-library/levels")
      setStack([{ type: "levels", data }])
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  async function drillInto(type, fetchPath, label, parentItem) {
    try {
      setLoading(true)
      const data = await api(fetchPath)
      setStack(prev => [...prev, { type, data, label, parentItem }])
    } catch (e) { setError(e.message) }
    finally { setLoading(false) }
  }

  function goBack(toIndex) {
    setStack(prev => prev.slice(0, toIndex + 1))
  }

  async function refreshWords() {
    const frame = stack[stack.length - 1]
    if (frame.type !== "words") return
    try {
      const data = await api(`/vocab-library/sections/${frame.parentItem.id}/words`)
      setStack(prev => {
        const next = [...prev]
        next[next.length - 1] = { ...frame, data }
        return next
      })
    } catch (e) { setError(e.message) }
  }

  async function handleAdd(wordId) {
    setActionLoading(p => ({ ...p, [wordId]: true }))
    try {
      await api(`/vocab-library/words/${wordId}/flashcard`, { method: "POST" })
      await refreshWords()
    } catch (e) { setError(e.message) }
    finally { setActionLoading(p => ({ ...p, [wordId]: false })) }
  }

  async function handleRemove(wordId) {
    setActionLoading(p => ({ ...p, [wordId]: true }))
    try {
      await api(`/vocab-library/words/${wordId}/flashcard`, { method: "DELETE" })
      await refreshWords()
    } catch (e) { setError(e.message) }
    finally { setActionLoading(p => ({ ...p, [wordId]: false })) }
  }

  // Build breadcrumb labels from stack
  const crumbs = ["Library", ...stack.slice(1).map(f => f.label || f.type)]

  return (
    <div className="vl-shell">
      {stack.length > 1 && (
        <div className="vl-nav">
          <Breadcrumb crumbs={crumbs} onBack={(i) => goBack(i)} />
        </div>
      )}
      {error && <div className="vocab-error-banner" role="alert">{error}</div>}
      {loading && <div className="coll-topic-list__loading">Loading…</div>}

      {!loading && current.type === "levels" && (
        <div className="level-block-grid">
          {current.data.map(lv => (
            <LevelBlock
              key={lv.id}
              level={lv}
              isActive={false}
              onSelect={lv => drillInto("topics", `/vocab-library/levels/${lv.id}/topics`, lv.name, lv)}
            />
          ))}
        </div>
      )}

      {!loading && current.type === "topics" && (
        <div className="coll-topic-box-grid vl-drill-grid">
          {current.data.map(t => (
            <DrillBox
              key={t.id} item={t} label={t.title}
              pct={Math.round(t.pct)} done={t.completed_words} total={t.total_words}
              isActive={false}
              onSelect={t => drillInto("units", `/vocab-library/topics/${t.id}/units`, t.title, t)}
            />
          ))}
        </div>
      )}

      {!loading && current.type === "units" && (
        <div className="coll-topic-box-grid vl-drill-grid">
          {current.data.map(u => (
            <DrillBox
              key={u.id} item={u} label={`Unit ${u.unit_number}: ${u.title}`}
              pct={Math.round(u.pct)} done={u.completed_words} total={u.total_words}
              isActive={false}
              onSelect={u => drillInto("sections", `/vocab-library/units/${u.id}/sections`, `Unit ${u.unit_number}`, u)}
            />
          ))}
        </div>
      )}

      {!loading && current.type === "sections" && (
        <div className="coll-topic-box-grid vl-drill-grid">
          {current.data.map(s => (
            <DrillBox
              key={s.id} item={s} label={`${s.section_letter}. ${s.title}`}
              pct={Math.round(s.pct)} done={s.completed_words} total={s.total_words}
              isActive={false}
              onSelect={s => drillInto("words", `/vocab-library/sections/${s.id}/words`, `§${s.section_letter} ${s.title}`, s)}
            />
          ))}
        </div>
      )}

      {!loading && current.type === "words" && (
        <div className="coll-items-grid">
          {current.data.length === 0 && <div className="coll-items-empty">No words in this section.</div>}
          {current.data.map(w => (
            <WordCard
              key={w.id}
              word={w}
              onAdd={handleAdd}
              onRemove={handleRemove}
              loading={!!actionLoading[w.id]}
            />
          ))}
        </div>
      )}
    </div>
  )
}

export default VocabularyLibrary
