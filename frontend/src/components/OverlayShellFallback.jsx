function OverlayShellFallback({ title }) {
  return (
    <div className="overlay-shell overlay-shell--fallback is-open">
      <div className="overlay-shell__scrim" />
      <section className="overlay-frame overlay-frame--fallback" role="dialog" aria-modal="true" aria-busy="true">
        <header className="overlay-frame__header">
          <div>
            <p className="overlay-frame__eyebrow">System Overlay</p>
            <h2>{title}</h2>
            <p className="overlay-frame__subtitle">Preparing interface shell...</p>
          </div>
        </header>
        <div className="overlay-frame__body">
          <div className="overlay-fallback-grid">
            <div className="overlay-fallback-block overlay-fallback-block--hero" />
            <div className="overlay-fallback-block" />
            <div className="overlay-fallback-block" />
          </div>
        </div>
      </section>
    </div>
  )
}

export default OverlayShellFallback
