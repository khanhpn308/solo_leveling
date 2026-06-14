import { useEffect, useRef, useState } from 'react'
import { speak, isSpeechSupported } from '../utils/speak'

// Reusable pronunciation button. Renders a 🔊 button that reads `text` aloud via
// the Web Speech API. Hidden entirely when the browser has no speech support.
// Shows an active state (🔈) while speaking. `text` is the raw word/collocation
// (NOT the IPA string — TTS pronounces the spelling).
function SpeakButton({ text, label, className = '' }) {
  const [speaking, setSpeaking] = useState(false)
  const mountedRef = useRef(true)

  useEffect(() => {
    mountedRef.current = true
    return () => {
      mountedRef.current = false
    }
  }, [])

  if (!isSpeechSupported() || !text) return null

  const aria = label || `Pronounce ${text}`

  function handleClick(e) {
    e.stopPropagation()
    speak(text, {
      onStart: () => mountedRef.current && setSpeaking(true),
      onEnd: () => mountedRef.current && setSpeaking(false),
    })
  }

  return (
    <button
      type="button"
      className={`speak-button ${speaking ? 'is-speaking' : ''} ${className}`.trim()}
      onClick={handleClick}
      aria-label={aria}
      title={aria}
    >
      <span aria-hidden="true">{speaking ? '🔈' : '🔊'}</span>
    </button>
  )
}

export default SpeakButton
