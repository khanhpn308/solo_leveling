import { useState } from 'react'
import PanelFrame from './PanelFrame'
import { TEST_EVIDENCE } from '../dashboard-data'
import { updatePlayerTargets } from '../api/auth'

const BAND_OPTIONS = ['4.0', '4.5', '5.0', '5.5', '6.0', '6.5', '7.0', '7.5', '8.0', '8.5', '9.0']

const TARGET_SKILLS = [
  { key: 'overall', label: 'Overall', playerKey: 'targetOverall' },
  { key: 'listening', label: 'Listening', playerKey: 'targetListening' },
  { key: 'reading', label: 'Reading', playerKey: 'targetReading' },
  { key: 'writing', label: 'Writing', playerKey: 'targetWriting' },
  { key: 'speaking', label: 'Speaking', playerKey: 'targetSpeaking' },
]

function resolveInitialTargets(player) {
  const fallback = player.targetOverall || player.target || '6.5'
  return {
    overall: player.targetOverall || fallback,
    listening: player.targetListening || fallback,
    reading: player.targetReading || fallback,
    writing: player.targetWriting || fallback,
    speaking: player.targetSpeaking || fallback,
  }
}

function SetupSummaryPanel({ player, skills, onProfileRefresh }) {
  const [targets, setTargets] = useState(() => resolveInitialTargets(player))
  const [saved, setSaved] = useState(() => resolveInitialTargets(player))
  const [saving, setSaving] = useState(false)
  const [saveMsg, setSaveMsg] = useState('')

  const isDirty = TARGET_SKILLS.some(({ key }) => targets[key] !== saved[key])

  function handleChange(key, val) {
    setTargets((prev) => ({ ...prev, [key]: val }))
    setSaveMsg('')
  }

  async function handleSave() {
    setSaving(true)
    setSaveMsg('')
    try {
      await updatePlayerTargets(targets)
      setSaved({ ...targets })
      setSaveMsg('Đã lưu')
      if (onProfileRefresh) onProfileRefresh()
    } catch {
      setSaveMsg('Lỗi — thử lại')
    } finally {
      setSaving(false)
    }
  }

  return (
    <PanelFrame title="Campaign Setup" tag={player.hasStarted ? 'Start locked in' : `${player.daysUntilStart} days left`}>
      <div className="setup-grid">
        <div className="setup-card setup-card--target">
          <span className="setup-card__label">Mục tiêu IELTS</span>
          <div className="target-grid">
            {TARGET_SKILLS.map(({ key, label }) => (
              <label key={key} className="onboarding-score-row target-row">
                <span className="onboarding-score-label">{label}</span>
                <select
                  className="onboarding-score-input"
                  value={targets[key]}
                  onChange={(e) => handleChange(key, e.target.value)}
                >
                  {BAND_OPTIONS.map((band) => (
                    <option key={band} value={band}>
                      {band}
                    </option>
                  ))}
                </select>
              </label>
            ))}
          </div>
          {isDirty && (
            <button
              className="target-save-btn"
              onClick={handleSave}
              disabled={saving}
            >
              {saving ? 'Đang lưu…' : 'Lưu mục tiêu'}
            </button>
          )}
          {saveMsg && <p className="target-save-msg">{saveMsg}</p>}
        </div>
        <div className="setup-card">
          <span className="setup-card__label">Evidence</span>
          <strong>{TEST_EVIDENCE.length} baseline evidence sources</strong>
          <p>IELTS / TOEIC / Aptis / CEFR records are used to suggest skill ranks.</p>
        </div>
      </div>

      <div className="setup-section">
        <h3>Test History</h3>
        <ul className="compact-list">
          {TEST_EVIDENCE.map((item) => (
            <li key={`${item.exam}-${item.date}`}>
              <strong>{item.exam}</strong>
              <span>{item.date}</span>
              <p>{item.details}</p>
            </li>
          ))}
        </ul>
      </div>

      <div className="setup-section">
        <h3>Confirmed Skill Ranks</h3>
        <div className="rank-row">
          {skills.map((skill) => (
            <div key={skill.id} className={`rank-token rank-token--${skill.theme.accent}`}>
              <span>{skill.name}</span>
              <strong>{skill.rank}</strong>
            </div>
          ))}
        </div>
      </div>
    </PanelFrame>
  )
}

export default SetupSummaryPanel
