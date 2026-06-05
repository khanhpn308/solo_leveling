import { useId, useRef } from 'react'
import { usePresenceLayer } from './usePresenceLayer'

function OverlayFrame({ open, title, subtitle, onClose, children, className = '', actions }) {
  const closeButtonRef = useRef(null)
  const titleId = useId()
  const descriptionId = useId()
  const { isMounted, phase, rootRef } = usePresenceLayer({
    open,
    onClose,
    initialFocusRef: closeButtonRef,
    trapFocus: true,
    closeOnInteractOutside: true,
  })

  if (!isMounted) return null

  return (
    <div className={`overlay-shell ${phase === 'open' ? 'is-open' : phase === 'entering' ? 'is-entering' : 'is-closing'}`}>
      <div className="overlay-shell__scrim" aria-hidden="true" />
      <section
        ref={rootRef}
        className={`overlay-frame ${className}`.trim()}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        aria-describedby={subtitle ? descriptionId : undefined}
        data-presence={phase}
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
