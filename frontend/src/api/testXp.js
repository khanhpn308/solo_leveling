import { apiFetch } from './client'

// Test-only XP tool — gated server-side to the seed account ad00000@gmail.com.

export function getTestXpSkills() {
  return apiFetch('/dev/test-xp/skills')
}

export function awardTestXp(skillId, delta = 0, reset = false) {
  return apiFetch('/dev/test-xp/award', {
    method: 'POST',
    body: JSON.stringify({ skill_id: skillId, delta, reset }),
  })
}
