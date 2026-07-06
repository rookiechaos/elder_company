import React, { useState, useRef, useEffect } from 'react'

/**
 * LazyImage — lazy-loaded image with optional WebP support.
 */
const LazyImage = ({
  src,
  webpSrc,
  alt = '',
  className = '',
  placeholder = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1"%3E%3C/svg%3E',
  loading = 'lazy',
  ...props
}) => {
  const [imageSrc, setImageSrc] = useState(placeholder)
  const [isLoaded, setIsLoaded] = useState(false)
  const [isInView, setIsInView] = useState(false)
  const imgRef = useRef(null)

  useEffect(() => {
    // Check if Intersection Observer is supported
    if (!('IntersectionObserver' in window)) {
      // Fallback: load image immediately
      setImageSrc(webpSrc || src)
      setIsInView(true)
      return
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsInView(true)
            observer.disconnect()
          }
        })
      },
      {
        rootMargin: '50px', // Start loading 50px before image enters viewport
        threshold: 0.01
      }
    )

    if (imgRef.current) {
      observer.observe(imgRef.current)
    }

    return () => {
      if (imgRef.current) {
        observer.unobserve(imgRef.current)
      }
      observer.disconnect()
    }
  }, [])

  useEffect(() => {
    if (isInView && !isLoaded) {
      // Check WebP support
      const supportsWebP = checkWebPSupport()
      
      // Load appropriate image format
      const imageToLoad = supportsWebP && webpSrc ? webpSrc : src
      
      const img = new Image()
      img.onload = () => {
        setImageSrc(imageToLoad)
        setIsLoaded(true)
      }
      img.onerror = () => {
        // Fallback to original src if WebP fails
        if (webpSrc && imageToLoad === webpSrc) {
          const fallbackImg = new Image()
          fallbackImg.onload = () => {
            setImageSrc(src)
            setIsLoaded(true)
          }
          fallbackImg.src = src
        } else {
          setImageSrc(src)
          setIsLoaded(true)
        }
      }
      img.src = imageToLoad
    }
  }, [isInView, src, webpSrc, isLoaded])

  /**
   * Check if browser supports WebP format
   */
  const checkWebPSupport = () => {
    const canvas = document.createElement('canvas')
    canvas.width = 1
    canvas.height = 1
    return canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0
  }

  return (
    <img
      ref={imgRef}
      src={imageSrc}
      alt={alt}
      className={`lazy-image ${className} ${isLoaded ? 'loaded' : 'loading'}`}
      loading={loading}
      style={{
        opacity: isLoaded ? 1 : 0.3,
        transition: 'opacity 0.3s ease-in-out'
      }}
      {...props}
    />
  )
}

export default LazyImage
