// Browser text-to-speech helper (Web Speech API).
// No backend, no audio files — reads any text aloud with the device's voices.
// Used by <SpeakButton> for IPA-pronunciation playback across the app.

let cachedVoices = []

function loadVoices() {
  if (!isSpeechSupported()) return
  cachedVoices = window.speechSynthesis.getVoices() || []
}

// Voices load asynchronously in some browsers (first getVoices() returns []).
// Cache them and refresh on the voiceschanged event so en-US is picked on the
// very first speak() call.
if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
  loadVoices()
  window.speechSynthesis.addEventListener?.('voiceschanged', loadVoices)
}

export function isSpeechSupported() {
  return typeof window !== 'undefined' && 'speechSynthesis' in window
}

function pickVoice(lang) {
  const voices = cachedVoices.length ? cachedVoices : (isSpeechSupported() ? window.speechSynthesis.getVoices() : [])
  return (
    voices.find((v) => v.lang === lang) ||
    voices.find((v) => v.lang?.startsWith(lang.split('-')[0])) ||
    null
  )
}

// Speak `text` aloud. Cancels any ongoing utterance first (so repeated clicks
// restart cleanly). `opts.onStart` / `opts.onEnd` let the caller reflect the
// speaking state in the UI. lang/rate/pitch are overridable to leave room for a
// future settings UI; defaults are en-US at normal speed.
export function speak(text, opts = {}) {
  if (!isSpeechSupported() || !text) return
  const { lang = 'en-US', rate = 1, pitch = 1, onStart, onEnd } = opts

  window.speechSynthesis.cancel()
  const utterance = new SpeechSynthesisUtterance(text)
  utterance.lang = lang
  utterance.rate = rate
  utterance.pitch = pitch

  const voice = pickVoice(lang)
  if (voice) utterance.voice = voice

  if (onStart) utterance.onstart = onStart
  if (onEnd) {
    utterance.onend = onEnd
    utterance.onerror = onEnd
  }

  window.speechSynthesis.speak(utterance)
}
