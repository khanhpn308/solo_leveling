import { useEffect, useId, useRef } from 'react'

function getFocusableElements(container) {
  if (!container) return []

  return [...container.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])')]
    .filter((element) => !element.hasAttribute('disabled') && element.getAttribute('aria-hidden') !== 'true')
}

function NavigationDrawer({ open, onClose, onOpenQuestTab, onOpenCertificates, onOpenBoss }) {
  const drawerRef = useRef(null)
  const closeButtonRef = useRef(null)
  const onCloseRef = useRef(onClose)
  const titleId = useId()

  onCloseRef.current = onClose

  useEffect(() => {
    if (!open) return undefined

    const previousActive = document.activeElement
    closeButtonRef.current?.focus()

    function handleKeyDown(event) {
      if (event.key === 'Escape') {
        event.preventDefault()
        onCloseRef.current()
        return
      }

      if (event.key !== 'Tab') return

      const focusable = getFocusableElements(drawerRef.current)
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
  }, [open])

  if (!open) return null

  return (
    <div className="drawer-shell">
      <button className="drawer-shell__scrim" type="button" onClick={onClose} aria-label="Close navigation" />
      <aside ref={drawerRef} className="nav-drawer" role="dialog" aria-modal="true" aria-labelledby={titleId}>
        <header className="nav-drawer__header">
          <div>
            <p>System Access</p>
            <strong id={titleId}>Mission Gates</strong>
          </div>
          <button
            ref={closeButtonRef}
            className="system-icon-button nav-drawer__close"
            type="button"
            onClick={onClose}
            aria-label="Close navigation"
          >
            <span />
            <span />
          </button>
        </header>

        <div className="nav-drawer__actions">
          <div className="nav-drawer__group">
            <div className="nav-drawer__group-header">
              <span>Quest</span>
              <small>Main / Daily / Weekly / Archive</small>
            </div>
            <div className="nav-drawer__subactions">
              <button type="button" onClick={() => onOpenQuestTab('main')}>
                Main
              </button>
              <button type="button" onClick={() => onOpenQuestTab('daily')}>
                Daily
              </button>
              <button type="button" onClick={() => onOpenQuestTab('weekly')}>
                Weekly
              </button>
              <button type="button" onClick={() => onOpenQuestTab('archive')}>
                Archive
              </button>
            </div>
          </div>
          <button type="button" onClick={onOpenCertificates}>
            <span>Certificate</span>
            <small>IELTS / Aptis / TOEIC / TOEFL</small>
          </button>
          <button type="button" onClick={onOpenBoss}>
            <span>Boss</span>
            <small>Current target + timeline</small>
          </button>
        </div>
      </aside>
    </div>
  )
}

export default NavigationDrawer
