import { apiFetch } from './client'

export function register(email, password, displayName) {
  return apiFetch('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, password, display_name: displayName }),
  })
}

export function login(email, password) {
  return apiFetch('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  })
}

export function logout() {
  return apiFetch('/auth/logout', { method: 'POST' })
}

export function getMe() {
  return apiFetch('/auth/me')
}

export function getOnboardingStatus() {
  return apiFetch('/onboarding/status')
}

export function postManualCertificate(scores) {
  return apiFetch('/certificates/manual', {
    method: 'POST',
    body: JSON.stringify(scores),
  })
}

export function activateCampaign(displayName, campaignTemplateCode, startDate, targets) {
  const body = {}
  if (displayName && displayName.trim()) body.display_name = displayName.trim()
  if (campaignTemplateCode) body.campaign_template_code = campaignTemplateCode
  if (startDate) body.start_date = startDate
  if (targets) {
    if (targets.overall) body.target_overall_band = targets.overall
    if (targets.listening) body.target_listening_band = targets.listening
    if (targets.reading) body.target_reading_band = targets.reading
    if (targets.writing) body.target_writing_band = targets.writing
    if (targets.speaking) body.target_speaking_band = targets.speaking
  }
  return apiFetch('/onboarding/activate-campaign', {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

export function updatePlayerTargets(targets) {
  const body = {}
  if (targets.overall != null) body.target_overall_band = targets.overall
  if (targets.listening != null) body.target_listening_band = targets.listening
  if (targets.reading != null) body.target_reading_band = targets.reading
  if (targets.writing != null) body.target_writing_band = targets.writing
  if (targets.speaking != null) body.target_speaking_band = targets.speaking
  return apiFetch('/player/targets', {
    method: 'PATCH',
    body: JSON.stringify(body),
  })
}

export function refreshTokens() {
  return apiFetch('/auth/refresh', { method: 'POST' })
}
