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

export function activateCampaign(displayName, campaignTemplateCode, startDate, targetBand) {
  const body = {}
  if (displayName && displayName.trim()) body.display_name = displayName.trim()
  if (campaignTemplateCode) body.campaign_template_code = campaignTemplateCode
  if (startDate) body.start_date = startDate
  if (targetBand) body.target_band = targetBand
  return apiFetch('/onboarding/activate-campaign', {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

export function refreshTokens() {
  return apiFetch('/auth/refresh', { method: 'POST' })
}
