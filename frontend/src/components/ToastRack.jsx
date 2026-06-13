function ToastRack({ toasts, onDismiss }) {
  if (toasts.length === 0) return null

  return (
    <div className="toast-rack" aria-live="polite" aria-atomic="true">
      {toasts.map((toast) => (
        <article key={toast.id} className={`toast-card toast-card--${toast.tone || 'neutral'}`}>
          {onDismiss ? (
            <button
              type="button"
              className="toast-card__close"
              aria-label="Dismiss notification"
              onClick={() => onDismiss(toast.id)}
            >
              ×
            </button>
          ) : null}
          <strong>{toast.title}</strong>
          {toast.detail ? <span>{toast.detail}</span> : null}
        </article>
      ))}
    </div>
  )
}

export default ToastRack
