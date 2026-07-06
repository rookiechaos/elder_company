import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import api from '../utils/api'
import { AlertTriangle, Heart, Brain, Activity, Save, Play, Volume2, CheckCircle, X, Clock } from 'lucide-react'
import './EmergencyRecord.css'

const EmergencyRecord = ({ elderId, caregiverId, onClose }) => {
  const { t, i18n } = useTranslation(['emergency', 'common'])
  const [showFirstUseHint, setShowFirstUseHint] = useState(false)
  const [formData, setFormData] = useState({
    emergency_type: 'emotional',
    severity: 'medium',
    description: '',
    actions_taken: []
  })
  const [currentAction, setCurrentAction] = useState('')
  const [loading, setLoading] = useState(false)
  const [guidance, setGuidance] = useState(null)
  const [showGuidance, setShowGuidance] = useState(false)
  const [playingAudio, setPlayingAudio] = useState(false)

  useEffect(() => {
    const seen = localStorage.getItem('emergency_disclaimer_seen')
    if (!seen) setShowFirstUseHint(true)
  }, [])

  const dismissFirstUseHint = () => {
    localStorage.setItem('emergency_disclaimer_seen', '1')
    setShowFirstUseHint(false)
  }

  const emergencyTypes = [
    { value: 'health', icon: Heart, color: '#ef4444' },
    { value: 'emotional', icon: Brain, color: '#f59e0b' },
    { value: 'behavioral', icon: Activity, color: '#8b5cf6' }
  ]

  const severityOptions = [
    { value: 'low', color: '#4caf50' },
    { value: 'medium', color: '#ff9800' },
    { value: 'high', color: '#ef4444' }
  ]

  const severityLabels = {
    low: t('common:low'),
    medium: t('common:medium'),
    high: t('common:high'),
  }

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const addAction = () => {
    if (currentAction.trim()) {
      setFormData(prev => ({
        ...prev,
        actions_taken: [...prev.actions_taken, currentAction.trim()]
      }))
      setCurrentAction('')
    }
  }

  const removeAction = (index) => {
    setFormData(prev => ({
      ...prev,
      actions_taken: prev.actions_taken.filter((_, i) => i !== index)
    }))
  }

  const getGuidance = async () => {
    if (!formData.description.trim()) {
      alert(t('emergency:descriptionRequired'))
      return
    }

    setLoading(true)
    try {
      const lang = i18n.language?.startsWith('zh') ? 'zh' : (i18n.language?.startsWith('en') ? 'en' : 'ja')
      const response = await api.post('/emergency/guidance', {
        elder_id: elderId,
        emergency_type: formData.emergency_type,
        current_situation: formData.description,
        language: lang
      })
      setGuidance(response.data)
      setShowGuidance(true)
    } catch (error) {
      console.error('Failed to get guidance:', error)
      alert(t('emergency:guidanceFailed'))
    } finally {
      setLoading(false)
    }
  }

  const playVoiceGuidance = () => {
    if (!guidance?.voice_guidance_url) {
      alert(t('emergency:voiceUnavailable'))
      return
    }

    setPlayingAudio(true)
    const audio = new Audio(guidance.voice_guidance_url)
    audio.onended = () => setPlayingAudio(false)
    audio.onerror = () => {
      setPlayingAudio(false)
      alert(t('emergency:playFailed'))
    }
    audio.play()
  }

  const handleSubmit = async () => {
    if (!formData.description.trim()) {
      alert(t('emergency:descriptionRequired'))
      return
    }

    setLoading(true)
    try {
      await api.post('/emergency/record', {
        elder_id: elderId,
        caregiver_id: caregiverId,
        emergency_type: formData.emergency_type,
        severity: formData.severity,
        description: formData.description,
        actions_taken: formData.actions_taken,
        generate_guidance: true,
        generate_summary: true
      })
      
      alert(t('emergency:recordSaved'))
      if (onClose) {
        onClose()
      }
    } catch (error) {
      console.error('Failed to record emergency:', error)
      alert(t('emergency:recordSaveFailed'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="emergency-record-overlay" onClick={onClose}>
      <div className="emergency-record-container" onClick={(e) => e.stopPropagation()}>
        <div className="emergency-record-header">
          <AlertTriangle size={24} color="#ef4444" />
          <h2>{t('emergency:title')}</h2>
          {onClose && (
            <button className="close-button" onClick={onClose}>
              <X size={20} />
            </button>
          )}
        </div>

        <div className="emergency-record-content">
          {showFirstUseHint && (
            <div className="first-use-hint">
              <p>{t('emergency:firstUseHint')}</p>
              <button type="button" className="first-use-hint-dismiss" onClick={dismissFirstUseHint}>
                {t('common:understood')}
              </button>
            </div>
          )}

          <div className="form-group">
            <label>{t('emergency:emergencyType')}</label>
            <div className="emergency-type-options">
              {emergencyTypes.map(type => {
                const Icon = type.icon
                return (
                  <button
                    key={type.value}
                    className={`emergency-type-option ${formData.emergency_type === type.value ? 'active' : ''}`}
                    onClick={() => handleInputChange('emergency_type', type.value)}
                    style={{ '--type-color': type.color }}
                  >
                    <Icon size={20} />
                    <span>{t(`emergency:types.${type.value}`)}</span>
                  </button>
                )
              })}
            </div>
          </div>

          <div className="form-group">
            <label>{t('emergency:severity')}</label>
            <div className="severity-options">
              {severityOptions.map(severity => (
                <button
                  key={severity.value}
                  className={`severity-option ${formData.severity === severity.value ? 'active' : ''}`}
                  onClick={() => handleInputChange('severity', severity.value)}
                  style={{ '--severity-color': severity.color }}
                >
                  {severityLabels[severity.value]}
                </button>
              ))}
            </div>
          </div>

          <div className="form-group">
            <label>{t('emergency:description')} <span className="required">*</span></label>
            <textarea
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              placeholder={t('emergency:descriptionPlaceholder')}
              rows={4}
              className="description-input"
            />
          </div>

          <div className="form-group">
            <label>{t('emergency:actionsTaken')}</label>
            <div className="actions-input-group">
              <input
                type="text"
                value={currentAction}
                onChange={(e) => setCurrentAction(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && addAction()}
                placeholder={t('emergency:actionPlaceholder')}
                className="action-input"
              />
              <button className="add-action-button" onClick={addAction}>
                <CheckCircle size={18} />
              </button>
            </div>
            {formData.actions_taken.length > 0 && (
              <div className="actions-list">
                {formData.actions_taken.map((action, index) => (
                  <div key={index} className="action-item">
                    <Clock size={14} />
                    <span>{action}</span>
                    <button
                      className="remove-action-button"
                      onClick={() => removeAction(index)}
                    >
                      <X size={14} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {showGuidance && guidance && (
            <div className="guidance-section">
              <h3>{t('emergency:aiGuidance')}</h3>
              
              <div className="guidance-item">
                <div className="guidance-header">
                  <Volume2 size={18} />
                  <span>{t('emergency:voiceGuidance')}</span>
                  {guidance.voice_guidance_url && (
                    <button
                      className="play-audio-button"
                      onClick={playVoiceGuidance}
                      disabled={playingAudio}
                    >
                      <Play size={16} />
                      {playingAudio ? t('emergency:playing') : t('emergency:play')}
                    </button>
                  )}
                </div>
                <p className="guidance-text">{guidance.voice_guidance}</p>
              </div>

              {guidance.relief_actions && guidance.relief_actions.length > 0 && (
                <div className="guidance-item">
                  <h4>{t('emergency:reliefActions')}</h4>
                  <ul className="relief-actions-list">
                    {guidance.relief_actions.map((action, index) => (
                      <li key={index}>{action}</li>
                    ))}
                  </ul>
                </div>
              )}

              {guidance.risk_notes && (
                <div className="guidance-item risk-notes">
                  <h4>{t('emergency:riskNotes')}</h4>
                  <p>{guidance.risk_notes}</p>
                </div>
              )}

              <div className="disclaimer">
                <p>{guidance.disclaimer || t('emergency:disclaimer')}</p>
              </div>
            </div>
          )}

          <div className="action-buttons">
            <button
              className="button-secondary"
              onClick={getGuidance}
              disabled={loading || !formData.description.trim()}
            >
              {t('emergency:getGuidance')}
            </button>
            <button
              className="button-primary"
              onClick={handleSubmit}
              disabled={loading || !formData.description.trim()}
            >
              {loading ? t('common:saving') : t('emergency:saveRecord')}
              <Save size={18} />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default EmergencyRecord
