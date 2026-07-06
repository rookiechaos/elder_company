import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import api from '../utils/api'
import { Settings, Save, Sparkles, Languages, Activity, MessageSquare, AlertCircle } from 'lucide-react'
import './PersonalizationSettings.css'

const CATEGORY_KEYS = ['cognitive', 'crafts', 'music', 'exercise', 'social', 'memory']

const PersonalizationSettings = () => {
  const { t } = useTranslation(['personalization', 'common'])
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(false)
  const [customerId, setCustomerId] = useState('')
  const [customers, setCustomers] = useState([])
  
  const [settings, setSettings] = useState({
    translation: {
      style: 'professional',
      detail_level: 'moderate',
      use_honorifics: true,
      preferred_languages: {
        source: 'ja',
        target: 'en'
      }
    },
    activity: {
      favorite_categories: [],
      preferred_difficulty: 'medium',
      preferred_duration: 30,
      interests: []
    },
    communication: {
      tone: 'warm',
      pace: 'moderate',
      use_visual_aids: true
    }
  })

  useEffect(() => {
    loadCustomers()
  }, [])

  const loadCustomers = async () => {
    try {
      setCustomers([
        { id: '1', name: 'Taro Tanaka', name_ja: '田中太郎', type: 'caregiver' },
        { id: '2', name: 'Hanako Tanaka', name_ja: '田中花子', type: 'elder' }
      ])
    } catch (err) {
      setError(err.message)
    }
  }

  const loadPersonalization = async (id) => {
    if (!id) return
    
    setLoading(true)
    setError(null)
    try {
      const response = await api.get(`/customers/${id}/personalization`)
      if (response.data && response.data.length > 0) {
        const data = response.data[0]
        if (data.preference_data) {
          setSettings(prev => ({
            ...prev,
            ...data.preference_data
          }))
        }
      }
    } catch (err) {
      console.error('Failed to load personalization:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    if (!customerId) {
      setError(t('personalization:selectCustomerFirst'))
      return
    }

    setSaving(true)
    setError(null)
    setSuccess(false)

    try {
      await api.post(`/customers/${customerId}/personalization`, {
        data_type: 'combined',
        preference_data: settings
      })
      setSuccess(true)
      setTimeout(() => setSuccess(false), 3000)
    } catch (err) {
      setError(err.message || t('common:saveFailed'))
    } finally {
      setSaving(false)
    }
  }

  const updateSetting = (category, key, value) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [key]: value
      }
    }))
  }

  const customerTypeLabel = (type) =>
    type === 'caregiver' ? t('common:caregiver') : t('common:elder')

  return (
    <div className="personalization-settings">
      <div className="settings-header">
        <div className="header-content">
          <Settings size={24} />
          <h2>{t('personalization:title')}</h2>
        </div>
        <button
          className="btn-primary"
          onClick={handleSave}
          disabled={saving || !customerId}
        >
          <Save size={18} />
          {saving ? t('common:saving') : t('personalization:saveSettings')}
        </button>
      </div>

      {error && (
        <div className="error-banner">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div className="success-banner">
          <Sparkles size={18} />
          <span>{t('personalization:settingsSaved')}</span>
        </div>
      )}

      <div className="customer-selector">
        <label>{t('personalization:selectCustomer')}</label>
        <select
          value={customerId}
          onChange={(e) => {
            setCustomerId(e.target.value)
            loadPersonalization(e.target.value)
          }}
          className="form-input"
        >
          <option value="">{t('personalization:selectCustomerPlaceholder')}</option>
          {customers.map(customer => (
            <option key={customer.id} value={customer.id}>
              {customer.name} ({customerTypeLabel(customer.type)})
            </option>
          ))}
        </select>
      </div>

      {loading ? (
        <div className="loading-state">{t('common:loading')}</div>
      ) : (
        <div className="settings-content">
          <div className="settings-section">
            <div className="section-header">
              <Languages size={20} />
              <h3>{t('personalization:translationPreferences')}</h3>
            </div>
            <div className="settings-grid">
              <div className="setting-item">
                <label>{t('personalization:translationStyle')}</label>
                <select
                  value={settings.translation.style}
                  onChange={(e) => updateSetting('translation', 'style', e.target.value)}
                  className="form-input"
                >
                  <option value="professional">{t('personalization:styleProfessional')}</option>
                  <option value="casual">{t('personalization:styleCasual')}</option>
                  <option value="formal">{t('personalization:styleFormal')}</option>
                </select>
              </div>
              <div className="setting-item">
                <label>{t('personalization:detailLevel')}</label>
                <select
                  value={settings.translation.detail_level}
                  onChange={(e) => updateSetting('translation', 'detail_level', e.target.value)}
                  className="form-input"
                >
                  <option value="brief">{t('personalization:detailBrief')}</option>
                  <option value="moderate">{t('personalization:detailModerate')}</option>
                  <option value="detailed">{t('personalization:detailDetailed')}</option>
                </select>
              </div>
              <div className="setting-item">
                <label>
                  <input
                    type="checkbox"
                    checked={settings.translation.use_honorifics}
                    onChange={(e) => updateSetting('translation', 'use_honorifics', e.target.checked)}
                  />
                  {t('personalization:useHonorifics')}
                </label>
              </div>
            </div>
          </div>

          <div className="settings-section">
            <div className="section-header">
              <Activity size={20} />
              <h3>{t('personalization:activityPreferences')}</h3>
            </div>
            <div className="settings-grid">
              <div className="setting-item">
                <label>{t('personalization:preferredDifficulty')}</label>
                <select
                  value={settings.activity.preferred_difficulty}
                  onChange={(e) => updateSetting('activity', 'preferred_difficulty', e.target.value)}
                  className="form-input"
                >
                  <option value="easy">{t('common:easy')}</option>
                  <option value="medium">{t('common:medium')}</option>
                  <option value="hard">{t('common:hard')}</option>
                </select>
              </div>
              <div className="setting-item">
                <label>{t('personalization:preferredDuration')}</label>
                <input
                  type="number"
                  value={settings.activity.preferred_duration}
                  onChange={(e) => updateSetting('activity', 'preferred_duration', parseInt(e.target.value))}
                  className="form-input"
                  min="5"
                  max="120"
                />
              </div>
              <div className="setting-item full-width">
                <label>{t('personalization:favoriteCategories')}</label>
                <div className="checkbox-group">
                  {CATEGORY_KEYS.map(key => {
                    const label = t(`personalization:categories.${key}`)
                    return (
                      <label key={key} className="checkbox-label">
                        <input
                          type="checkbox"
                          checked={settings.activity.favorite_categories.includes(label)}
                          onChange={(e) => {
                            const categories = e.target.checked
                              ? [...settings.activity.favorite_categories, label]
                              : settings.activity.favorite_categories.filter(c => c !== label)
                            updateSetting('activity', 'favorite_categories', categories)
                          }}
                        />
                        <span>{label}</span>
                      </label>
                    )
                  })}
                </div>
              </div>
            </div>
          </div>

          <div className="settings-section">
            <div className="section-header">
              <MessageSquare size={20} />
              <h3>{t('personalization:communicationPreferences')}</h3>
            </div>
            <div className="settings-grid">
              <div className="setting-item">
                <label>{t('personalization:tone')}</label>
                <select
                  value={settings.communication.tone}
                  onChange={(e) => updateSetting('communication', 'tone', e.target.value)}
                  className="form-input"
                >
                  <option value="warm">{t('personalization:toneWarm')}</option>
                  <option value="professional">{t('personalization:toneProfessional')}</option>
                  <option value="friendly">{t('personalization:toneFriendly')}</option>
                  <option value="gentle">{t('personalization:toneGentle')}</option>
                </select>
              </div>
              <div className="setting-item">
                <label>{t('personalization:pace')}</label>
                <select
                  value={settings.communication.pace}
                  onChange={(e) => updateSetting('communication', 'pace', e.target.value)}
                  className="form-input"
                >
                  <option value="slow">{t('personalization:paceSlow')}</option>
                  <option value="moderate">{t('personalization:paceModerate')}</option>
                  <option value="fast">{t('personalization:paceFast')}</option>
                </select>
              </div>
              <div className="setting-item">
                <label>
                  <input
                    type="checkbox"
                    checked={settings.communication.use_visual_aids}
                    onChange={(e) => updateSetting('communication', 'use_visual_aids', e.target.checked)}
                  />
                  {t('personalization:useVisualAids')}
                </label>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default PersonalizationSettings
