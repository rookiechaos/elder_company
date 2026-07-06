import React from 'react'
import { useTranslation } from 'react-i18next'
import { Info } from 'lucide-react'
import './AboutDisclaimer.css'

function AboutDisclaimer() {
  const { t } = useTranslation('about')

  return (
    <div className="about-disclaimer">
      <div className="about-disclaimer-header">
        <Info size={28} aria-hidden />
        <h2>{t('title')}</h2>
        <p className="subtitle">{t('subtitle')}</p>
      </div>

      <section className="about-section">
        <h3>{t('productNatureTitle')}</h3>
        <p>{t('productNature1')}</p>
        <p>{t('productNature2')}</p>
      </section>

      <section className="about-section disclaimer-section">
        <h3>{t('boundariesTitle')}</h3>
        <ul>
          <li>{t('boundary1')}</li>
          <li>{t('boundary2')}</li>
          <li>{t('boundary3')}</li>
        </ul>
      </section>

      <section className="about-section">
        <h3>{t('featuresTitle')}</h3>
        <p>{t('featuresText')}</p>
      </section>

      <p className="about-footer-note">
        {t('footerNote')}
      </p>
    </div>
  )
}

export default AboutDisclaimer
