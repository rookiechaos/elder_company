import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import api from '../utils/api'
import { Languages, ArrowLeftRight, Send, AlertCircle, CheckCircle } from 'lucide-react'
import './TranslationInterface.css'

const TranslationInterface = () => {
  const { t } = useTranslation(['translation', 'common'])
  const [inputText, setInputText] = useState('')
  const [translatedText, setTranslatedText] = useState('')
  const [sourceLang, setSourceLang] = useState('ja')
  const [targetLang, setTargetLang] = useState('en')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [providerInfo, setProviderInfo] = useState(null)

  const languages = [
    { code: 'ja', nameKey: 'languages.ja' },
    { code: 'en', nameKey: 'languages.en' },
  ]

  useEffect(() => {
    const fetchProviderInfo = async () => {
      try {
        const response = await api.get('/ai/provider')
        setProviderInfo(response.data)
      } catch (error) {
        console.error('Failed to fetch provider info:', error)
      }
    }
    fetchProviderInfo()
  }, [])

  const handleTranslate = async () => {
    if (!inputText.trim()) return

    setLoading(true)
    setError(null)
    setTranslatedText('')
    
    try {
      const response = await api.post('/translate', {
        text: inputText,
        source_language: sourceLang,
        target_language: targetLang,
      })
      setTranslatedText(response.data.translated_text)
    } catch (error) {
      console.error('Translation error:', error)
      const errorMessage = error.message || t('translation:translateFailed')
      setError(errorMessage)
      setTranslatedText('')
    } finally {
      setLoading(false)
    }
  }

  const swapLanguages = () => {
    const temp = sourceLang
    setSourceLang(targetLang)
    setTargetLang(temp)
    setInputText(translatedText)
    setTranslatedText(inputText)
  }

  return (
    <div className="translation-container">
      {providerInfo && (
        <div className={`provider-status ${providerInfo.status === 'available' ? 'available' : 'unavailable'}`}>
          {providerInfo.status === 'available' ? (
            <CheckCircle size={16} />
          ) : (
            <AlertCircle size={16} />
          )}
          <span>
            {t('translation:providerStatus', {
              provider: providerInfo.provider.toUpperCase(),
              status: providerInfo.status,
            })}
          </span>
        </div>
      )}
      
      {error && (
        <div className="error-message">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      <div className="language-selectors">
        <div className="language-selector">
          <label>{t('translation:sourceLanguage')}</label>
          <select
            value={sourceLang}
            onChange={(e) => setSourceLang(e.target.value)}
            className="language-select"
          >
            {languages.map((lang) => (
              <option key={lang.code} value={lang.code}>
                {t(`translation:${lang.nameKey}`)}
              </option>
            ))}
          </select>
        </div>

        <button
          onClick={swapLanguages}
          className="swap-button"
          aria-label={t('translation:swapLanguages')}
        >
          <ArrowLeftRight size={20} />
        </button>

        <div className="language-selector">
          <label>{t('translation:targetLanguage')}</label>
          <select
            value={targetLang}
            onChange={(e) => setTargetLang(e.target.value)}
            className="language-select"
          >
            {languages.map((lang) => (
              <option key={lang.code} value={lang.code}>
                {t(`translation:${lang.nameKey}`)}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="translation-panels">
        <div className="translation-panel">
          <div className="panel-header">
            <Languages size={18} />
            <span>{t('translation:inputText')}</span>
          </div>
          <textarea
            value={inputText}
            onChange={(e) => {
              setInputText(e.target.value)
              setError(null)
            }}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                handleTranslate()
              }
            }}
            placeholder={t('translation:inputPlaceholder')}
            className="translation-input"
            rows={8}
          />
        </div>

        <div className="translation-panel">
          <div className="panel-header">
            <Languages size={18} />
            <span>{t('translation:outputText')}</span>
          </div>
          <div className="translation-output">
            {loading ? (
              <div className="loading">{t('translation:translating')}</div>
            ) : (
              translatedText || <span className="placeholder">{t('translation:outputPlaceholder')}</span>
            )}
          </div>
        </div>
      </div>

      <button
        onClick={handleTranslate}
        disabled={!inputText.trim() || loading}
        className="translate-button"
      >
        <Send size={18} />
        {loading ? t('translation:translating') : t('translation:translate')}
      </button>
    </div>
  )
}

export default TranslationInterface
