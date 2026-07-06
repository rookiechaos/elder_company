/**
 * Web Vitals integration — collect and send performance metrics to the backend.
 */

import api from './api'

const METRICS = {
  LCP: 'LCP',
  FID: 'FID',
  TTI: 'TTI',
  FCP: 'FCP',
  CLS: 'CLS',
  TTFB: 'TTFB',
}

const collectedMetrics = {}

async function sendMetricsToBackend(metrics) {
  try {
    await api.post('/metrics/web-vitals', {
      metrics,
      timestamp: new Date().toISOString(),
      url: window.location.href,
      userAgent: navigator.userAgent,
      connection: navigator.connection ? {
        effectiveType: navigator.connection.effectiveType,
        downlink: navigator.connection.downlink,
        rtt: navigator.connection.rtt
      } : null
    })
  } catch (error) {
    console.warn('Error sending Web Vitals metrics:', error)
  }
}

function measureLCP() {
  try {
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries()
        const lastEntry = entries[entries.length - 1]

        const lcpValue = lastEntry.renderTime || lastEntry.loadTime

        collectedMetrics[METRICS.LCP] = {
          value: Math.round(lcpValue),
          rating: getLCPRating(lcpValue),
          element: lastEntry.element ? lastEntry.element.tagName : null,
          url: lastEntry.url || null
        }

        sendMetricsToBackend({
          metric: METRICS.LCP,
          value: lcpValue,
          rating: collectedMetrics[METRICS.LCP].rating
        })

        observer.disconnect()
      })

      observer.observe({ entryTypes: ['largest-contentful-paint'] })
    }
  } catch (error) {
    console.warn('Error measuring LCP:', error)
  }
}

function measureFID() {
  try {
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries()
        entries.forEach((entry) => {
          const fidValue = entry.processingStart - entry.startTime

          collectedMetrics[METRICS.FID] = {
            value: Math.round(fidValue),
            rating: getFIDRating(fidValue),
            eventType: entry.name,
            target: entry.target ? entry.target.tagName : null
          }

          sendMetricsToBackend({
            metric: METRICS.FID,
            value: fidValue,
            rating: collectedMetrics[METRICS.FID].rating
          })

          observer.disconnect()
        })
      })

      observer.observe({ entryTypes: ['first-input'] })
    }
  } catch (error) {
    console.warn('Error measuring FID:', error)
  }
}

function measureFCP() {
  try {
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries()
        entries.forEach((entry) => {
          if (entry.name === 'first-contentful-paint') {
            const fcpValue = entry.startTime

            collectedMetrics[METRICS.FCP] = {
              value: Math.round(fcpValue),
              rating: getFCPRating(fcpValue)
            }

            sendMetricsToBackend({
              metric: METRICS.FCP,
              value: fcpValue,
              rating: collectedMetrics[METRICS.FCP].rating
            })

            observer.disconnect()
          }
        })
      })

      observer.observe({ entryTypes: ['paint'] })
    }
  } catch (error) {
    console.warn('Error measuring FCP:', error)
  }
}

function measureCLS() {
  try {
    if ('PerformanceObserver' in window) {
      let clsValue = 0
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries()
        entries.forEach((entry) => {
          if (!entry.hadRecentInput) {
            clsValue += entry.value
          }
        })

        collectedMetrics[METRICS.CLS] = {
          value: Math.round(clsValue * 1000) / 1000,
          rating: getCLSRating(clsValue)
        }
      })

      observer.observe({ entryTypes: ['layout-shift'] })

      window.addEventListener('beforeunload', () => {
        sendMetricsToBackend({
          metric: METRICS.CLS,
          value: clsValue,
          rating: collectedMetrics[METRICS.CLS].rating
        })
      })
    }
  } catch (error) {
    console.warn('Error measuring CLS:', error)
  }
}

function measureTTI() {
  try {
    if ('PerformanceObserver' in window) {
      const navigationEntry = performance.getEntriesByType('navigation')[0]

      if (navigationEntry) {
        const domContentLoaded = navigationEntry.domContentLoadedEventEnd - navigationEntry.domContentLoadedEventStart
        const ttiValue = domContentLoaded + 5000

        setTimeout(() => {
          const longTasks = performance.getEntriesByType('long-task')
          const quietWindow = longTasks.length === 0

          if (quietWindow) {
            collectedMetrics[METRICS.TTI] = {
              value: Math.round(ttiValue),
              rating: getTTIRating(ttiValue)
            }

            sendMetricsToBackend({
              metric: METRICS.TTI,
              value: ttiValue,
              rating: collectedMetrics[METRICS.TTI].rating
            })
          }
        }, 5000)
      }
    }
  } catch (error) {
    console.warn('Error measuring TTI:', error)
  }
}

function measureTTFB() {
  try {
    const navigationEntry = performance.getEntriesByType('navigation')[0]

    if (navigationEntry) {
      const ttfbValue = navigationEntry.responseStart - navigationEntry.requestStart

      collectedMetrics[METRICS.TTFB] = {
        value: Math.round(ttfbValue),
        rating: getTTFBRating(ttfbValue)
      }

      sendMetricsToBackend({
        metric: METRICS.TTFB,
        value: ttfbValue,
        rating: collectedMetrics[METRICS.TTFB].rating
      })
    }
  } catch (error) {
    console.warn('Error measuring TTFB:', error)
  }
}

function getLCPRating(value) {
  if (value <= 2500) return 'good'
  if (value <= 4000) return 'needs-improvement'
  return 'poor'
}

function getFIDRating(value) {
  if (value <= 100) return 'good'
  if (value <= 300) return 'needs-improvement'
  return 'poor'
}

function getFCPRating(value) {
  if (value <= 1800) return 'good'
  if (value <= 3000) return 'needs-improvement'
  return 'poor'
}

function getCLSRating(value) {
  if (value <= 0.1) return 'good'
  if (value <= 0.25) return 'needs-improvement'
  return 'poor'
}

function getTTIRating(value) {
  if (value <= 3800) return 'good'
  if (value <= 7300) return 'needs-improvement'
  return 'poor'
}

function getTTFBRating(value) {
  if (value <= 800) return 'good'
  if (value <= 1800) return 'needs-improvement'
  return 'poor'
}

export function initWebVitals() {
  measureFCP()
  measureTTFB()

  if (document.readyState === 'complete') {
    measureLCP()
    measureFID()
    measureCLS()
    measureTTI()
  } else {
    window.addEventListener('load', () => {
      measureLCP()
      measureFID()
      measureCLS()
      measureTTI()
    })
  }

  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') {
      sendMetricsToBackend({
        allMetrics: collectedMetrics
      })
    }
  })
}

export function getCollectedMetrics() {
  return { ...collectedMetrics }
}

export default {
  initWebVitals,
  getCollectedMetrics,
  METRICS
}
