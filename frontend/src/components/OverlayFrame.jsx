function OverlayFrame({ title, subtitle, onClose, children, className = '', actions }) {
  return (
    <div className="overlay-shell" role="dialog" aria-modal="true">
      <div className="overlay-shell__scrim" onClick={onClose} />
      <section className={`overlay-frame ${className}`.trim()}>
        <header className="overlay-frame__header">
          <div>
            <p className="overlay-frame__eyebrow">System Overlay</p>
            <h2>{title}</h2>
            {subtitle ? <p className="overlay-frame__subtitle">{subtitle}</p> : null}
          </div>
          <div className="overlay-frame__actions">
            {actions}
            <button className="system-icon-button" type="button" onClick={onClose} aria-label="Close overlay">
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
