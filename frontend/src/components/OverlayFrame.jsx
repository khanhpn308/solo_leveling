import { useEffect, useId, useRef } from 'react'

function getFocusableElements(container) {
  if (!container) return []

  return [...container.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])')]
    .filter((element) => !element.hasAttribute('disabled') && element.getAttribute('aria-hidden') !== 'true')
}

function OverlayFrame({ title, subtitle, onClose, children, className = '', actions }) {
  const dialogRef = useRef(null)
  const closeButtonRef = useRef(null)
  const onCloseRef = useRef(onClose)
  const titleId = useId()
  const descriptionId = useId()

  onCloseRef.current = onClose

  useEffect(() => {
    const previousActive = document.activeElement
    closeButtonRef.current?.focus()

    function handleKeyDown(event) {
      if (event.key === 'Escape') {
        event.preventDefault()
        onCloseRef.current()
        return
      }

      if (event.key !== 'Tab') return

      const focusable = getFocusableElements(dialogRef.current)
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

    document.addEventListener('keydown', handleKeyDown)

    return () => {
      document.removeEventListener('keydown', handleKeyDown)
      if (previousActive instanceof HTMLElement) {
        previousActive.focus()
      }
    }
  }, [])

  return (
    <div className="overlay-shell">
      <button className="overlay-shell__scrim" type="button" onClick={onClose} aria-label="Close overlay background" />
      <section
        ref={dialogRef}
        className={`overlay-frame ${className}`.trim()}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        aria-describedby={subtitle ? descriptionId : undefined}
      >
        <header className="overlay-frame__header">
          <div>
            <p className="overlay-frame__eyebrow">System Overlay</p>
            <h2 id={titleId}>{title}</h2>
            {subtitle ? (
              <p className="overlay-frame__subtitle" id={descriptionId}>
                {subtitle}
              </p>
            ) : null}
          </div>
          <div className="overlay-frame__actions">
            {actions}
            <button
              ref={closeButtonRef}
              className="system-icon-button"
              type="button"
              onClick={onClose}
              aria-label="Close overlay"
            >
              <span />
              <span />
            </button>
          </div>
        </header>
        <div className="overlay-frame__body">{children}</div>
      </section>
    </div>
  )
}

export default OverlayFrame
