import { apiFetch } from './client'

export function unlockRankExam(skillId) {
  return apiFetch('/rank-exams/unlock', {
    method: 'POST',
    body: JSON.stringify({ skill_id: skillId }),
  })
}

export function startRankExam(skillId) {
  return apiFetch('/rank-exams/start', {
    method: 'POST',
    body: JSON.stringify({ skill_id: skillId }),
  })
}

export function getRankExamStatus(skillId) {
  return apiFetch(`/rank-exams/status/${skillId}`)
}

export function getRankExamAttempt(attemptId) {
  return apiFetch(`/rank-exams/${attemptId}`)
}

export function submitRankExam(attemptId, answers) {
  return apiFetch(`/rank-exams/${attemptId}/submit`, {
    method: 'POST',
    body: JSON.stringify({ answers }),
  })
}
