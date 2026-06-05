import { useId, useRef } from 'react'
import { usePresenceLayer } from './usePresenceLayer'

function NavigationDrawer({ open, onClose, onOpenQuestTab, onOpenCertificates, onOpenBoss }) {
  const closeButtonRef = useRef(null)
  const titleId = useId()
  const { isMounted, phase, rootRef } = usePresenceLayer({
    open,
    onClose,
    initialFocusRef: closeButtonRef,
    trapFocus: true,
    closeOnInteractOutside: true,
  })

  if (!isMounted) return null

  return (
    <div className={`drawer-shell ${phase === 'open' ? 'is-open' : phase === 'entering' ? 'is-entering' : 'is-closing'}`}>
      <div className="drawer-shell__scrim" aria-hidden="true" />
      <aside ref={rootRef} className="nav-drawer" role="dialog" aria-modal="true" aria-labelledby={titleId} data-presence={phase}>
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
