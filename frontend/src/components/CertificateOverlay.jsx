import { useState } from 'react'
import { CERTIFICATE_TYPES, formatDate, toIsoDate } from '../dashboard-data'
import OverlayFrame from './OverlayFrame'

const INITIAL_FORM = {
  test_type: 'IELTS',
  test_date: toIsoDate(new Date()),
  overall_score: '',
  listening_score: '',
  reading_score: '',
  writing_score: '',
  speaking_score: '',
  cefr_level: '',
  note: '',
}

function CertificateOverlay({ open, loading, error, records, onClose, onCreate }) {
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [form, setForm] = useState(INITIAL_FORM)
  const [submitting, setSubmitting] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    try {
      setSubmitting(true)
      await onCreate(form)
      setForm(INITIAL_FORM)
      setIsFormOpen(false)
    } finally {
      setSubmitting(false)
    }
  }

  function updateField(field, value) {
    setForm((current) => ({ ...current, [field]: value }))
  }

  return (
    <OverlayFrame
      open={open}
      title="Certificate Records"
      subtitle="Existing test records filtered to exam certificates, with live create via the current API."
      onClose={onClose}
      className="overlay-frame--certificate"
      actions={
        <button className="system-button" type="button" onClick={() => setIsFormOpen((current) => !current)}>
          {isFormOpen ? 'Close form' : '+ Add record'}
        </button>
      }
    >
      {isFormOpen ? (
        <form className="certificate-form" onSubmit={handleSubmit}>
          <label>
            <span>Exam</span>
            <select value={form.test_type} onChange={(event) => updateField('test_type', event.target.value)}>
              {CERTIFICATE_TYPES.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </label>

          <label>
            <span>Test date</span>
            <input
              type="date"
              value={form.test_date}
              onChange={(event) => updateField('test_date', event.target.value)}
              required
            />
          </label>

          <label>
            <span>Overall</span>
            <input value={form.overall_score} onChange={(event) => updateField('overall_score', event.target.value)} />
          </label>

          <label>
            <span>Listening</span>
            <input
              value={form.listening_score}
              onChange={(event) => updateField('listening_score', event.target.value)}
            />
          </label>

          <label>
            <span>Reading</span>
            <input
              value={form.reading_score}
              onChange={(event) => updateField('reading_score', event.target.value)}
            />
          </label>

          <label>
            <span>Writing</span>
            <input
              value={form.writing_score}
              onChange={(event) => updateField('writing_score', event.target.value)}
            />
          </label>

          <label>
            <span>Speaking</span>
            <input
              value={form.speaking_score}
              onChange={(event) => updateField('speaking_score', event.target.value)}
            />
          </label>

          <label>
            <span>CEFR</span>
            <input value={form.cefr_level} onChange={(event) => updateField('cefr_level', event.target.value)} />
          </label>

          <label className="certificate-form__full">
            <span>Note</span>
            <textarea value={form.note} onChange={(event) => updateField('note', event.target.value)} />
          </label>

          <button className="system-button" type="submit" disabled={submitting}>
            {submitting ? 'Saving...' : 'Save record'}
          </button>
        </form>
      ) : null}

      {loading ? <div className="empty-state">Loading certificate records...</div> : null}
      {!loading && error ? <div className="empty-state empty-state--warning">{error}</div> : null}

      {!loading && !error ? (
        <div className="certificate-list">
          {records.length === 0 ? (
            <div className="empty-state">No IELTS / Aptis / TOEIC / TOEFL certificate records yet.</div>
          ) : (
            records.map((record) => (
              <article key={record.id} className="certificate-card">
                <header>
                  <div>
                    <p>{record.test_type}</p>
                    <strong>{formatDate(record.test_date)}</strong>
                  </div>
                  <span>{record.overall_score || record.cefr_level || '--'}</span>
                </header>
                <div className="certificate-card__scores">
                  <span>L {record.listening_score || '--'}</span>
                  <span>R {record.reading_score || '--'}</span>
                  <span>W {record.writing_score || '--'}</span>
                  <span>S {record.speaking_score || '--'}</span>
                </div>
                <p>{record.note || 'No note.'}</p>
              </article>
            ))
          )}
        </div>
      ) : null}
    </OverlayFrame>
  )
}

export default CertificateOverlay
