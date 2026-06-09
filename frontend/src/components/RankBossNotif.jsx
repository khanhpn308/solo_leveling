import { useState } from 'react'

function RankBossNotif({ skills = [], onUnlock, onStartExam }) {
  const [pendingSkillId, setPendingSkillId] = useState(null)

  const eligibleSkills = skills.filter((s) => s.promotion_status === 'eligible')
  const bossReadySkills = skills.filter((s) => s.promotion_status === 'boss_required')
  const inProgressSkills = skills.filter((s) => s.promotion_status === 'in_progress')

  if (eligibleSkills.length === 0 && bossReadySkills.length === 0 && inProgressSkills.length === 0) return null

  async function handleUnlock(skill) {
    if (pendingSkillId) return
    setPendingSkillId(skill.id)
    try {
      await onUnlock(skill)
    } finally {
      setPendingSkillId(null)
    }
  }

  async function handleStart(skill) {
    if (pendingSkillId) return
    setPendingSkillId(skill.id)
    try {
      await onStartExam(skill)
    } finally {
      setPendingSkillId(null)
    }
  }

  return (
    <div className="rank-boss-notif-stack">
      {eligibleSkills.map((skill) => (
        <div key={skill.id} className="rank-boss-notif rank-boss-notif--eligible">
          <div className="rank-boss-notif__icon">⚔️</div>
          <div className="rank-boss-notif__body">
            <strong>{skill.name}</strong>
            <span>
              Rank {skill.confirmed_rank} → {skill.pending_rank} promotion available
            </span>
          </div>
          <button
            className="rank-boss-notif__btn"
            disabled={pendingSkillId === skill.id}
            onClick={() => handleUnlock(skill)}
          >
            {pendingSkillId === skill.id ? 'Unlocking...' : 'Unlock Boss'}
          </button>
        </div>
      ))}

      {bossReadySkills.map((skill) => (
        <div key={skill.id} className="rank-boss-notif rank-boss-notif--ready">
          <div className="rank-boss-notif__icon">🔴</div>
          <div className="rank-boss-notif__body">
            <strong>{skill.name}</strong>
            <span>
              Boss Exam ready — Rank {skill.confirmed_rank} → {skill.pending_rank}
            </span>
          </div>
          <button
            className="rank-boss-notif__btn rank-boss-notif__btn--danger"
            disabled={pendingSkillId === skill.id}
            onClick={() => handleStart(skill)}
          >
            {pendingSkillId === skill.id ? 'Starting...' : 'Start Exam'}
          </button>
        </div>
      ))}

      {inProgressSkills.map((skill) => (
        <div key={skill.id} className="rank-boss-notif rank-boss-notif--active">
          <div className="rank-boss-notif__icon">⏱️</div>
          <div className="rank-boss-notif__body">
            <strong>{skill.name}</strong>
            <span>Exam in progress — resume before time runs out</span>
          </div>
          <button
            className="rank-boss-notif__btn rank-boss-notif__btn--danger"
            disabled={pendingSkillId === skill.id}
            onClick={() => handleStart(skill)}
          >
            {pendingSkillId === skill.id ? 'Loading...' : 'Resume Exam'}
          </button>
        </div>
      ))}
    </div>
  )
}

export default RankBossNotif
