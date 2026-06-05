import { useEffect, useRef, useState } from 'react'

const EXIT_DURATION_MS = 140

function getFocusableElements(container) {
  if (!container) return []

  return [...container.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])')]
    .filter((element) => !element.hasAttribute('disabled') && element.getAttribute('aria-hidden') !== 'true')
}

export function usePresenceLayer({
  open,
  onClose,
  initialFocusRef,
  trapFocus = false,
  closeOnInteractOutside = false,
  exitDurationMs = EXIT_DURATION_MS,
}) {
  const rootRef = useRef(null)
  const onCloseRef = useRef(onClose)
  const restoreFocusRef = useRef(null)
  const exitTimerRef = useRef(null)
  const enterFrameRef = useRef(null)
  const [isMounted, setIsMounted] = useState(open)
  const [phase, setPhase] = useState(open ? 'open' : 'closed')

  onCloseRef.current = onClose

  useEffect(() => {
    if (open) {
      if (exitTimerRef.current) {
        window.clearTimeout(exitTimerRef.current)
        exitTimerRef.current = null
      }

      if (!isMounted) {
        restoreFocusRef.current = document.activeElement instanceof HTMLElement ? document.activeElement : null
        setIsMounted(true)
        setPhase('entering')
      } else {
        setPhase('open')
      }

      enterFrameRef.current = window.requestAnimationFrame(() => {
        setPhase('open')
        initialFocusRef?.current?.focus?.()
      })

      return () => {
        if (enterFrameRef.current) {
          window.cancelAnimationFrame(enterFrameRef.current)
          enterFrameRef.current = null
        }
      }
    }

    if (!isMounted) {
      setPhase('closed')
      return undefined
    }

    setPhase('closing')
    exitTimerRef.current = window.setTimeout(() => {
      setIsMounted(false)
      setPhase('closed')
      restoreFocusRef.current?.focus?.()
    }, exitDurationMs)

    return () => {
      if (exitTimerRef.current) {
        window.clearTimeout(exitTimerRef.current)
        exitTimerRef.current = null
      }
    }
  }, [exitDurationMs, initialFocusRef, isMounted, open])

  useEffect(() => {
    if (!isMounted) return undefined

    function handleKeyDown(event) {
      if (event.key === 'Escape') {
        event.preventDefault()
        onCloseRef.current?.()
        return
      }

      if (!trapFocus || event.key !== 'Tab') return

      const focusable = getFocusableElements(rootRef.current)
      if (focusable.length === 0) return

      const first = focusable[0]
      const last = focusable[focusable.length - 1]

      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault()
        last.focus()
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault()
        first.focus()
      }
    }

    function handlePointerDown(event) {
      if (!closeOnInteractOutside) return
      if (rootRef.current?.contains(event.target)) return
      onCloseRef.current?.()
    }

    document.addEventListener('keydown', handleKeyDown)
    document.addEventListener('pointerdown', handlePointerDown)

    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      document.removeEventListener('pointerdown', handlePointerDown)
    }
  }, [closeOnInteractOutside, isMounted, trapFocus])

  useEffect(() => {
    return () => {
      if (exitTimerRef.current) window.clearTimeout(exitTimerRef.current)
      if (enterFrameRef.current) window.cancelAnimationFrame(enterFrameRef.current)
    }
  }, [])

  return {
    isMounted,
    phase,
    rootRef,
  }
}
