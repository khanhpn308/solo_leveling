import { useEffect, useMemo, useState } from 'react'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
const RANKS = ['F', 'E', 'D', 'C', 'B', 'A', 'S']
const STAGES = ['Tháng 1–3', 'Tháng 4–6', 'Tháng 7–9', 'Tháng 10–12', 'Tháng 13–18']

function formatDate(value) {
  if (!value) return '—'
  return new Intl.DateTimeFormat('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' }).format(new Date(value))
}

function rankProgress(xp) {
  const thresholds = [0, 200, 500, 1000, 1700, 2500, 3500]
  const next = thresholds.find((t) => t > xp) || 3500
  const prev = [...thresholds].reverse().find((t) => t <= xp) || 0
  if (xp >= 3500) return 100
  return Math.round(((xp - prev) / (next - prev)) * 100)
}

function getTodayISO() {
  const today = new Date()
  const yyyy = today.getFullYear()
  const mm = String(today.getMonth() + 1).padStart(2, '0')
  const dd = String(today.getDate()).padStart(2, '0')
  return `${yyyy}-${mm}-${dd}`
}

async function api(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || 'API error')
  }
  return response.json()
}

function App() {
  const [summary, setSummary] = useState(null)
  const [quests, setQuests] = useState([])
  const [checkins, setCheckins] = useState([])
  const [selectedStage, setSelectedStage] = useState('')
  const [selectedWeek, setSelectedWeek] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [mood, setMood] = useState(3)
  const [energy, setEnergy] = useState(3)
  const [note, setNote] = useState('')

  const completedThisWeek = useMemo(() => quests.filter(q => q.completed).length, [quests])
  const totalThisWeek = quests.length

  async function loadData() {
    try {
      setLoading(true)
      setError('')
      const [summaryData, questData, checkinData] = await Promise.all([
        api('/summary'),
        api(selectedStage || selectedWeek ? `/quests?${new URLSearchParams({
          ...(selectedStage ? { stage: selectedStage } : {}),
          ...(selectedWeek ? { week_no: selectedWeek } : {}),
        })}` : '/quests'),
        api('/checkins'),
      ])
      setSummary(summaryData)
      setQuests(questData)
      setCheckins(checkinData)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedStage, selectedWeek])

  async function toggleQuest(quest) {
    await api(`/quests/${quest.id}/${quest.completed ? 'uncomplete' : 'complete'}`, { method: 'POST' })
    await loadData()
  }

  async function saveCheckIn() {
    await api('/checkins', {
      method: 'POST',
      body: JSON.stringify({ checkin_date: getTodayISO(), mood, energy, note }),
    })
    setNote('')
    await loadData()
  }

  if (loading && !summary) {
    return <div className="boot-screen">SYSTEM LOADING<span>.</span><span>.</span><span>.</span></div>
  }

  if (error) {
    return <div className="boot-screen error">API ERROR: {error}</div>
  }

  return (
    <main className="app-shell">
      <section className="hero-panel glass-frame">
        <div className="scanline" />
        <div className="hero-left">
          <p className="eyebrow">IELTS SYSTEM INTERFACE</p>
          <h1>IELTS Quest Dashboard</h1>
          <p className="subtitle">18 months to Band 7.0–7.5 · Local React + FastAPI + MySQL</p>
          <div className="player-grid">
            <Stat label="Level" value={summary.player.total_xp < 500 ? '18' : Math.floor(summary.player.total_xp / 180) + 18} />
            <Stat label="Title" value={summary.player.title} />
            <Stat label="Target" value={summary.player.target} />
            <Stat label="Start" value={formatDate(summary.player.start_date)} />
          </div>
        </div>
        <div className="status-card">
          <p className="card-label">STATUS</p>
          <div className="big-level">{summary.player.total_xp}</div>
          <p className="xp-label">TOTAL XP</p>
          <div className="bar-wrap"><div style={{ width: `${Math.min(100, summary.player.total_xp / 35)}%` }} /></div>
          <p className="tiny">Week: {formatDate(summary.player.week_start)} → {formatDate(summary.player.week_end)}</p>
        </div>
      </section>

      <section className="dashboard-grid">
        <section className="panel rank-panel">
          <PanelHeader title="Skill Progress" tag="F → S Rank" />
          <div className="rank-ladder">
            {RANKS.slice().reverse().map(rank => <span key={rank} className={`rank-chip rank-${rank}`}>{rank}</span>)}
          </div>
          <div className="skill-list">
            {summary.skills.map(skill => <SkillCard key={skill.id} skill={skill} />)}
          </div>
        </section>

        <section className="panel quests-panel">
          <PanelHeader title="Quest Board" tag={`${completedThisWeek}/${totalThisWeek} done`} />
          <div className="filters">
            <select value={selectedStage} onChange={(e) => { setSelectedStage(e.target.value); setSelectedWeek('') }}>
              <option value="">Current week</option>
              {STAGES.map(stage => <option key={stage} value={stage}>{stage}</option>)}
            </select>
            <input
              value={selectedWeek}
              onChange={(e) => { setSelectedWeek(e.target.value); setSelectedStage('') }}
              placeholder="Week no."
              type="number"
              min="1"
              max="78"
            />
          </div>
          <div className="quest-list">
            {quests.slice(0, 21).map(quest => (
              <button key={quest.id} className={`quest-card ${quest.completed ? 'completed' : ''}`} onClick={() => toggleQuest(quest)}>
                <div>
                  <p className="quest-date">Week {quest.week_no} · {formatDate(quest.quest_date)} · {quest.stage}</p>
                  <h3>{quest.title}</h3>
                  <p>{quest.details}</p>
                  <span className="source">Source: {quest.source}</span>
                </div>
                <div className="quest-reward">
                  <strong>+{quest.xp}</strong>
                  <span>XP</span>
                  <small>{quest.skill_name}</small>
                </div>
              </button>
            ))}
          </div>
        </section>

        <section className="panel mood-panel">
          <PanelHeader title="Mood / Energy" tag="Daily Check-in" />
          <div className="slider-row">
            <label>Mood</label>
            <input type="range" min="1" max="5" value={mood} onChange={(e) => setMood(Number(e.target.value))} />
            <strong>{'★'.repeat(mood)}{'☆'.repeat(5 - mood)}</strong>
          </div>
          <div className="slider-row">
            <label>Energy</label>
            <input type="range" min="1" max="5" value={energy} onChange={(e) => setEnergy(Number(e.target.value))} />
            <strong>{'⚡'.repeat(energy)}</strong>
          </div>
          <textarea value={note} onChange={(e) => setNote(e.target.value)} placeholder="Ghi chú ngắn: hôm nay mệt vì..., học tốt vì..." />
          <button className="primary-btn" onClick={saveCheckIn}>Save Check-in</button>
          <div className="checkin-list">
            {checkins.slice(0, 5).map(item => (
              <div key={item.id} className="checkin-item">
                <span>{formatDate(item.checkin_date)}</span>
                <strong>M{item.mood}/E{item.energy}</strong>
                <p>{item.note || 'No note'}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="panel badge-panel">
          <PanelHeader title="Badge Wall" tag="Achievements" />
          <div className="badge-grid">
            {summary.badges.map(badge => (
              <div key={badge.id} className={`badge ${badge.unlocked ? 'unlocked' : 'locked'}`}>
                <span>{badge.icon}</span>
                <strong>{badge.name}</strong>
                <p>{badge.description}</p>
              </div>
            ))}
          </div>
        </section>

        <section className="panel boss-panel">
          <PanelHeader title="Boss Battles" tag="Monthly checkpoints" />
          <div className="boss-list">
            {summary.boss_battles.map(boss => (
              <div key={boss.id} className="boss-card">
                <div>
                  <p>{formatDate(boss.battle_date)} · {boss.stage}</p>
                  <h3>{boss.title}</h3>
                  <span>{boss.goal}</span>
                </div>
                <strong>{boss.status}</strong>
              </div>
            ))}
          </div>
        </section>
      </section>
    </main>
  )
}

function Stat({ label, value }) {
  return <div className="stat"><span>{label}</span><strong>{value}</strong></div>
}

function PanelHeader({ title, tag }) {
  return <div className="panel-header"><h2>{title}</h2><span>{tag}</span></div>
}

function SkillCard({ skill }) {
  const pct = rankProgress(skill.xp)
  return (
    <div className="skill-card">
      <div className={`rank-badge rank-${skill.rank}`}>{skill.rank}</div>
      <div className="skill-main">
        <div className="skill-title-row">
          <h3>{skill.icon} {skill.name}</h3>
          <span>Lv.{skill.level}</span>
        </div>
        <div className="bar-wrap"><div style={{ width: `${pct}%` }} /></div>
        <p>{skill.xp} XP · Last practiced: {formatDate(skill.last_practiced)}</p>
        <small>{skill.weak_point}</small>
      </div>
    </div>
  )
}

export default App
