import React, { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Send, X, AlertCircle, CheckCircle, Bug, Lightbulb, HelpCircle, ThumbsDown, Heart } from 'lucide-react'
import api from '../utils/api'
import './FeedbackForm.css'

const FeedbackForm = ({ onClose, initialType = null, initialPage = null }) => {
  const { t } = useTranslation(['feedback', 'common'])
  const [feedbackType, setFeedbackType] = useState(initialType || 'suggestion')
  const [category, setCategory] = useState('other')
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [contactEmail, setContactEmail] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)
  const [error, setError] = useState(null)

  const feedbackTypes = [
    { id: 'suggestion', icon: Lightbulb, color: '#f5e6e8' },
    { id: 'bug', icon: Bug, color: '#ffe6e6' },
    { id: 'question', icon: HelpCircle, color: '#e6f0ff' },
    { id: 'complaint', icon: ThumbsDown, color: '#ffe6e6' },
    { id: 'praise', icon: Heart, color: '#e6ffe6' }
  ]

  const categories = ['feature', 'ui', 'performance', 'translation', 'other']

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!title.trim() || !content.trim()) {
      setError(t('feedback:titleContentRequired'))
      return
    }

    setSubmitting(true)
    setError(null)

    try {
      await api.post('/feedback', {
        feedback_type: feedbackType,
        category: category,
        title: title.trim(),
        content: content.trim(),
        contact_email: contactEmail || undefined,
        page_url: initialPage || window.location.href
      })

      setSubmitted(true)
      setTimeout(() => {
        if (onClose) onClose()
      }, 2000)
    } catch (err) {
      console.error('Failed to submit feedback:', err)
      setError(t('feedback:submitFailed'))
    } finally {
      setSubmitting(false)
    }
  }

  if (submitted) {
    return (
      <div className="feedback-form-overlay">
        <div className="feedback-form-modal success">
          <CheckCircle size={48} className="success-icon" />
          <h2>{t('feedback:successTitle')}</h2>
          <p>{t('feedback:successMessage')}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="feedback-form-overlay" onClick={(e) => e.target === e.currentTarget && onClose && onClose()}>
      <div className="feedback-form-modal">
        <div className="feedback-form-header">
          <h2>{t('feedback:title')}</h2>
          {onClose && (
            <button className="close-button" onClick={onClose}>
              <X size={20} />
            </button>
          )}
        </div>

        <form onSubmit={handleSubmit} className="feedback-form">
          <div className="form-section">
            <label>{t('feedback:feedbackType')}</label>
            <div className="feedback-types">
              {feedbackTypes.map((type) => {
                const Icon = type.icon
                return (
                  <button
                    key={type.id}
                    type="button"
                    className={`type-button ${feedbackType === type.id ? 'active' : ''}`}
                    onClick={() => setFeedbackType(type.id)}
                    style={{ '--type-color': type.color }}
                  >
                    <Icon size={20} />
                    <span>{t(`feedback:types.${type.id}`)}</span>
                  </button>
                )
              })}
            </div>
          </div>

          <div className="form-section">
            <label htmlFor="category">{t('feedback:category')}</label>
            <select
              id="category"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
            >
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {t(`feedback:categories.${cat}`)}
                </option>
              ))}
            </select>
          </div>

          <div className="form-section">
            <label htmlFor="title">{t('feedback:titleLabel')} *</label>
            <input
              id="title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder={t('feedback:titlePlaceholder')}
              required
            />
          </div>

          <div className="form-section">
            <label htmlFor="content">{t('feedback:contentLabel')} *</label>
            <textarea
              id="content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder={t('feedback:contentPlaceholder')}
              rows={6}
              required
            />
          </div>

          <div className="form-section">
            <label htmlFor="email">{t('feedback:emailLabel')}</label>
            <input
              id="email"
              type="email"
              value={contactEmail}
              onChange={(e) => setContactEmail(e.target.value)}
              placeholder={t('feedback:emailPlaceholder')}
            />
          </div>

          {error && (
            <div className="error-message">
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
          )}

          <div className="form-actions">
            {onClose && (
              <button type="button" className="cancel-button" onClick={onClose}>
                {t('common:cancel')}
              </button>
            )}
            <button type="submit" className="submit-button" disabled={submitting}>
              {submitting ? t('common:submitting') : t('common:submit')}
              {!submitting && <Send size={16} />}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default FeedbackForm
