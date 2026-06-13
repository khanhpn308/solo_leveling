import { useCallback, useEffect, useState } from 'react'
import { getTestXpSkills, awardTestXp } from '../api/testXp'

// Floating test-XP panel. Rendered only for the seed account (gate in App.jsx),
// but the backend re-checks the account on every call (403 otherwise).
// Hidden while any full-screen overlay (exam, status, quest, boss, certificate)
// is open so it never covers a modal — notably the Rank Exam screen.
function TestXpPanel({ onXpChange, hidden = false }) {
  const [open, setOpen] = useState(false)
  const [skills, setSkills] = useState([])
  const [loading, setLoading] = useState(false)
  const [drafts, setDrafts] = useState({})       // skill_id -> input string
  const [pendingId, setPendingId] = useState(null)
  const [error, setError] = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const data = await getTestXpSkills()
      setSkills(data)
    } catch (err) {
      setError(err.message || 'Failed to load skills')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    if (open && skills.length === 0) load()
  }, [open, skills.length, load])

  async function applyDelta(skillId, delta, reset = false) {
    setPendingId(skillId)
    setError('')
    try {
      const updated = await awardTestXp(skillId, delta, reset)
      setSkills((prev) => prev.map((s) => (s.skill_id === skillId ? updated : s)))
      if (reset) setDrafts((d) => ({ ...d, [skillId]: '' }))
      if (onXpChange) onXpChange()
    } catch (err) {
      setError(err.message || 'Award failed')
    } finally {
      setPendingId(null)
    }
  }

  function handleAdd(skillId) {
    const raw = drafts[skillId]
    const delta = parseInt(raw, 10)
    if (!Number.isFinite(delta) || delta === 0) return
    applyDelta(skillId, delta)
  }

  if (hidden) return null

  return (
    <div className="test-xp-panel">
      <button className="test-xp-panel__toggle" type="button" onClick={() => setOpen((v) => !v)}>
        🧪 Test XP {open ? '▾' : '▸'}
      </button>

      {open && (
        <div className="test-xp-panel__body">
          <div className="test-xp-panel__head">
            <strong>Add XP (seed account)</strong>
            <button className="test-xp-panel__refresh" type="button" onClick={load} disabled={loading}>
              {loading ? '…' : '↻'}
            </button>
          </div>

          {error && <div className="test-xp-panel__error">{error}</div>}

          <div className="test-xp-panel__list">
            {skills.map((s) => (
              <div key={s.skill_id} className="test-xp-row">
                <div className="test-xp-row__info">
                  <span className="test-xp-row__name">{s.name}</span>
                  <span className="test-xp-row__meta">
                    {s.xp} XP · {s.rank}{s.level} · bonus {s.manual_xp_bonus}
                  </span>
                </div>
                <div className="test-xp-row__controls">
                  <input
                    className="test-xp-row__input"
                    type="number"
                    placeholder="+XP"
                    value={drafts[s.skill_id] ?? ''}
                    onChange={(e) => setDrafts((d) => ({ ...d, [s.skill_id]: e.target.value }))}
                    disabled={pendingId === s.skill_id}
                  />
                  <button
                    className="test-xp-row__add"
                    type="button"
                    onClick={() => handleAdd(s.skill_id)}
                    disabled={pendingId === s.skill_id}
                  >
                    Add
                  </button>
                  <button
                    className="test-xp-row__reset"
                    type="button"
                    onClick={() => applyDelta(s.skill_id, 0, true)}
                    disabled={pendingId === s.skill_id || s.manual_xp_bonus === 0}
                    title="Reset manual bonus to 0"
                  >
                    Reset
                  </button>
                </div>
              </div>
            ))}
            {!loading && skills.length === 0 && (
              <div className="test-xp-panel__empty">No skills loaded.</div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default TestXpPanel
