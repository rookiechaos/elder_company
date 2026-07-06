import i18n from 'i18next'
import { initReactI18next } from 'react-i18next'
import LanguageDetector from 'i18next-browser-languagedetector'

import en from './locales/en.json'
import ja from './locales/ja.json'

const namespaces = [
  'common',
  'app',
  'auth',
  'nightMode',
  'translation',
  'customer',
  'onboarding',
  'helpCenter',
  'feedback',
  'emergency',
  'about',
  'activity',
  'personalization',
  'performance',
  'installPrompt',
  'notification',
  'voiceInput',
  'collaborativeDesign',
  'activityCustomization',
]

const buildResources = (locale) =>
  namespaces.reduce((acc, ns) => {
    acc[ns] = locale[ns] || {}
    return acc
  }, {})

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      en: buildResources(en),
      ja: buildResources(ja),
    },
    lng: 'ja',
    fallbackLng: 'en',
    defaultNS: 'common',
    ns: namespaces,
    interpolation: {
      escapeValue: false,
    },
    detection: {
      order: ['localStorage', 'navigator'],
      caches: ['localStorage'],
    },
  })

export default i18n
