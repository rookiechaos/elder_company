import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import api from '../utils/api'
import { Moon, Sun, Volume2, VolumeX, Type, Palette, Clock, Check, X } from 'lucide-react'
import './NightMode.css'

const NightMode = ({ userId, userType }) => {
  const { t } = useTranslation(['nightMode', 'common'])
  const [config, setConfig] = useState(null)
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [isActive, setIsActive] = useState(false)

  useEffect(() => {
    loadConfig()
    checkActiveStatus()
    const interval = setInterval(checkActiveStatus, 60000)
    return () => clearInterval(interval)
  }, [userId])

  const loadConfig = async () => {
    if (!userId) return

    setLoading(true)
    try {
      const response = await api.get(`/night-mode/config?user_id=${userId}`)
      if (response.data.config) {
        setConfig(response.data.config)
        applyNightMode(response.data.config)
      }
    } catch (error) {
      console.error('Failed to load night mode config:', error)
    } finally {
      setLoading(false)
    }
  }

  const checkActiveStatus = async () => {
    if (!userId) return

    try {
      const response = await api.get(`/night-mode/active?user_id=${userId}`)
      setIsActive(response.data.is_active)
      if (response.data.is_active && config) {
        applyNightMode(config)
      } else {
        removeNightMode()
      }
    } catch (error) {
      console.error('Failed to check night mode status:', error)
    }
  }

  const applyNightMode = (config) => {
    if (!config || !config.enabled) {
      removeNightMode()
      return
    }

    const root = document.documentElement

    if (config.brightness === 'low') {
      root.style.setProperty('--night-brightness', '0.3')
    } else if (config.brightness === 'medium') {
      root.style.setProperty('--night-brightness', '0.5')
    } else {
      root.style.setProperty('--night-brightness', '0.7')
    }

    if (config.color_scheme === 'dark') {
      root.classList.add('night-mode-dark')
    } else if (config.color_scheme === 'dim') {
      root.classList.add('night-mode-dim')
    }

    if (config.font_size === 'large') {
      root.classList.add('night-mode-large-font')
    } else if (config.font_size === 'extra_large') {
      root.classList.add('night-mode-extra-large-font')
    }

    root.classList.add('night-mode-active')
  }

  const removeNightMode = () => {
    const root = document.documentElement
    root.classList.remove('night-mode-active', 'night-mode-dark', 'night-mode-dim', 'night-mode-large-font', 'night-mode-extra-large-font')
    root.style.removeProperty('--night-brightness')
  }

  const saveConfig = async (updates) => {
    if (!userId) return

    setSaving(true)
    try {
      const newConfig = { ...config, ...updates, user_id: userId, user_type: userType }
      const response = await api.put('/night-mode/config', newConfig)
      setConfig(response.data.config)
      applyNightMode(response.data.config)
      setIsActive(response.data.config.enabled)
    } catch (error) {
      console.error('Failed to save night mode config:', error)
      alert(t('nightMode:saveFailed'))
    } finally {
      setSaving(false)
    }
  }

  const toggleNightMode = () => {
    saveConfig({ enabled: !config?.enabled })
  }

  const brightnessLabels = {
    low: t('nightMode:brightnessLow'),
    medium: t('nightMode:brightnessMedium'),
    high: t('nightMode:brightnessHigh'),
  }

  const colorSchemeLabels = {
    dark: t('nightMode:colorDark'),
    dim: t('nightMode:colorDim'),
    custom: t('nightMode:colorCustom'),
  }

  const fontSizeLabels = {
    small: t('nightMode:fontSmall'),
    medium: t('nightMode:fontMedium'),
    large: t('nightMode:fontLarge'),
    extra_large: t('nightMode:fontExtraLarge'),
  }

  const soundTypeLabels = {
    gentle: t('nightMode:soundGentle'),
    calm: t('nightMode:soundCalm'),
    silent: t('nightMode:soundSilent'),
  }

  if (loading) {
    return (
      <div className="night-mode-container">
        <div className="loading">{t('nightMode:loading')}</div>
      </div>
    )
  }

  const currentConfig = config || {
    enabled: false,
    brightness: 'low',
    sound_enabled: false,
    text_prompts: true,
    start_time: '22:00',
    end_time: '07:00',
    sound_type: 'gentle',
    volume: 50,
    font_size: 'large',
    color_scheme: 'dark'
  }

  return (
    <div className="night-mode-container">
      <div className="night-mode-header">
        <Moon size={24} />
        <h2>{t('nightMode:title')}</h2>
        {isActive && <span className="active-badge">{t('nightMode:active')}</span>}
      </div>

      <div className="night-mode-content">
        <div className="setting-group">
          <div className="setting-item">
            <div className="setting-label">
              <Moon size={20} />
              <span>{t('nightMode:enableNightMode')}</span>
            </div>
            <button
              className={`toggle-button ${currentConfig.enabled ? 'active' : ''}`}
              onClick={toggleNightMode}
              disabled={saving}
            >
              {currentConfig.enabled ? <Check size={16} /> : <X size={16} />}
            </button>
          </div>
        </div>

        {currentConfig.enabled && (
          <>
            <div className="setting-group">
              <h3 className="setting-group-title">
                <Clock size={18} />
                {t('nightMode:schedule')}
              </h3>
              <div className="time-settings">
                <div className="time-input-group">
                  <label>{t('nightMode:startTime')}</label>
                  <input
                    type="time"
                    value={currentConfig.start_time || '22:00'}
                    onChange={(e) => saveConfig({ start_time: e.target.value })}
                    disabled={saving}
                  />
                </div>
                <div className="time-input-group">
                  <label>{t('nightMode:endTime')}</label>
                  <input
                    type="time"
                    value={currentConfig.end_time || '07:00'}
                    onChange={(e) => saveConfig({ end_time: e.target.value })}
                    disabled={saving}
                  />
                </div>
              </div>
            </div>

            <div className="setting-group">
              <h3 className="setting-group-title">
                <Sun size={18} />
                {t('nightMode:brightness')}
              </h3>
              <div className="brightness-options">
                {['low', 'medium', 'high'].map((level) => (
                  <button
                    key={level}
                    className={`brightness-option ${currentConfig.brightness === level ? 'active' : ''}`}
                    onClick={() => saveConfig({ brightness: level })}
                    disabled={saving}
                  >
                    {brightnessLabels[level]}
                  </button>
                ))}
              </div>
            </div>

            <div className="setting-group">
              <h3 className="setting-group-title">
                <Palette size={18} />
                {t('nightMode:colorScheme')}
              </h3>
              <div className="color-scheme-options">
                {['dark', 'dim', 'custom'].map((scheme) => (
                  <button
                    key={scheme}
                    className={`color-scheme-option ${currentConfig.color_scheme === scheme ? 'active' : ''}`}
                    onClick={() => saveConfig({ color_scheme: scheme })}
                    disabled={saving}
                  >
                    {colorSchemeLabels[scheme]}
                  </button>
                ))}
              </div>
            </div>

            <div className="setting-group">
              <h3 className="setting-group-title">
                <Type size={18} />
                {t('nightMode:fontSize')}
              </h3>
              <div className="font-size-options">
                {['small', 'medium', 'large', 'extra_large'].map((size) => (
                  <button
                    key={size}
                    className={`font-size-option ${currentConfig.font_size === size ? 'active' : ''}`}
                    onClick={() => saveConfig({ font_size: size })}
                    disabled={saving}
                  >
                    {fontSizeLabels[size]}
                  </button>
                ))}
              </div>
            </div>

            <div className="setting-group">
              <h3 className="setting-group-title">
                {currentConfig.sound_enabled ? <Volume2 size={18} /> : <VolumeX size={18} />}
                {t('nightMode:sound')}
              </h3>
              <div className="setting-item">
                <div className="setting-label">
                  <span>{t('nightMode:enableSound')}</span>
                </div>
                <button
                  className={`toggle-button ${currentConfig.sound_enabled ? 'active' : ''}`}
                  onClick={() => saveConfig({ sound_enabled: !currentConfig.sound_enabled })}
                  disabled={saving}
                >
                  {currentConfig.sound_enabled ? <Check size={16} /> : <X size={16} />}
                </button>
              </div>
              {currentConfig.sound_enabled && (
                <>
                  <div className="sound-type-options">
                    {['gentle', 'calm', 'silent'].map((type) => (
                      <button
                        key={type}
                        className={`sound-type-option ${currentConfig.sound_type === type ? 'active' : ''}`}
                        onClick={() => saveConfig({ sound_type: type })}
                        disabled={saving}
                      >
                        {soundTypeLabels[type]}
                      </button>
                    ))}
                  </div>
                  <div className="volume-control">
                    <label>{t('nightMode:volume', { percent: currentConfig.volume })}</label>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={currentConfig.volume || 50}
                      onChange={(e) => saveConfig({ volume: parseInt(e.target.value) })}
                      disabled={saving}
                    />
                  </div>
                </>
              )}
            </div>

            <div className="setting-group">
              <div className="setting-item">
                <div className="setting-label">
                  <Type size={20} />
                  <span>{t('nightMode:enableTextPrompts')}</span>
                </div>
                <button
                  className={`toggle-button ${currentConfig.text_prompts ? 'active' : ''}`}
                  onClick={() => saveConfig({ text_prompts: !currentConfig.text_prompts })}
                  disabled={saving}
                >
                  {currentConfig.text_prompts ? <Check size={16} /> : <X size={16} />}
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default NightMode
