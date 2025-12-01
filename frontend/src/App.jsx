import { useState, useEffect, useRef } from 'react'
import './App.css'
import { BACKEND_URL } from './config'

const STORAGE_KEY = 'image2video-progress'

function App() {
  const [provider, setProvider] = useState('a2e')
  const [imageUrl, setImageUrl] = useState('')
  const [selectedFile, setSelectedFile] = useState(null)
  const [imagePreview, setImagePreview] = useState('')
  const [uploadMode, setUploadMode] = useState('file') // 'file' or 'url'
  const [text, setText] = useState('')
  const [taskId, setTaskId] = useState('')
  const [status, setStatus] = useState('')
  const [resultUrl, setResultUrl] = useState('')
  const [failedMessage, setFailedMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [polling, setPolling] = useState(false)
  const intervalRef = useRef(null)
  const fileInputRef = useRef(null)
  const hasHydratedRef = useRef(false)

  const API_BASE = BACKEND_URL

  useEffect(() => {
    if (typeof window === 'undefined') return
    try {
      const saved = localStorage.getItem(STORAGE_KEY)
      if (saved) {
        const data = JSON.parse(saved)
        if (data.provider) setProvider(data.provider)
        if (data.imageUrl) setImageUrl(data.imageUrl)
        if (data.uploadMode) setUploadMode(data.uploadMode)
        if (data.text) setText(data.text)
        if (data.taskId) setTaskId(data.taskId)
        if (data.status) setStatus(data.status)
        if (data.resultUrl) setResultUrl(data.resultUrl)
        if (data.failedMessage) setFailedMessage(data.failedMessage)
      }
    } catch (error) {
      console.warn('Unable to restore previous progress', error)
    } finally {
      hasHydratedRef.current = true
    }
  }, [])

  useEffect(() => {
    if (!hasHydratedRef.current) return
    saveProgress()
  }, [provider, imageUrl, uploadMode, text, taskId, status, resultUrl, failedMessage])

  const saveProgress = (overrides = {}) => {
    if (typeof window === 'undefined') return
    const payload = {
      provider,
      imageUrl,
      uploadMode,
      text,
      taskId,
      status,
      resultUrl,
      failedMessage,
      lastUpdated: Date.now(),
      ...overrides,
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(payload))
  }

  const handleFileSelect = (e) => {
    const file = e.target.files[0]
    if (file) {
      setSelectedFile(file)
      setImageUrl('') // Clear URL when file is selected
      
      // Create preview
      const reader = new FileReader()
      reader.onloadend = () => {
        setImagePreview(reader.result)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) {
      alert('Please select an image file')
      return null
    }

    setUploading(true)
    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

      const response = await fetch(`${API_BASE}/api/upload-image`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        let errorMessage = 'Failed to upload image'
        try {
          const errorData = await response.json()
          errorMessage = errorData.detail || errorData.message || errorMessage
        } catch {
          const errorText = await response.text()
          errorMessage = errorText || errorMessage
        }
        throw new Error(errorMessage)
      }

      const data = await response.json()
      setImageUrl(data.image_url)
      return data.image_url
    } catch (error) {
      let errorMessage = error.message || 'An unexpected error occurred'
      
      // Make error messages more user-friendly
      if (errorMessage.includes('must be an image')) {
        errorMessage = 'Please select a valid image file (JPG, PNG, etc.)'
      } else if (errorMessage.includes('network') || errorMessage.includes('fetch')) {
        errorMessage = 'Network error: Could not connect to the server. Make sure the backend is running.'
      }
      
      alert(`Upload error: ${errorMessage}`)
      return null
    } finally {
      setUploading(false)
    }
  }

  const handleStart = async () => {
    let finalImageUrl = imageUrl

    // If file mode and file is selected but not uploaded, upload it first
    if (uploadMode === 'file' && selectedFile && !imageUrl) {
      finalImageUrl = await handleUpload()
      if (!finalImageUrl) {
        return // Upload failed
      }
    }

    if (!finalImageUrl || !finalImageUrl.trim()) {
      alert(uploadMode === 'file' 
        ? 'Please select and upload an image file' 
        : 'Please enter an image URL')
      return
    }

    if (!text.trim()) {
      alert('Please enter text for the video')
      return
    }

    setLoading(true)
    setTaskId('')
    setStatus('')
    setResultUrl('')
    setFailedMessage('')

    try {
      const response = await fetch(`${API_BASE}/api/start-image2video`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          provider: provider,
          image_url: finalImageUrl,
          text: text,
        }),
      })

      if (!response.ok) {
        let errorMessage = 'Failed to start video generation'
        try {
          const errorData = await response.json()
          errorMessage = errorData.detail || errorData.message || errorMessage
        } catch {
          const errorText = await response.text()
          errorMessage = errorText || errorMessage
        }
        throw new Error(errorMessage)
      }

      const data = await response.json()
      setTaskId(data.task_id)
      setStatus(data.status)
    } catch (error) {
      let errorMessage = error.message || 'An unexpected error occurred'
      
      // Make error messages more user-friendly
      if (errorMessage.includes('not configured') || errorMessage.includes('not found in environment')) {
        errorMessage = `API key missing! Please check your .env file and add the required API key for ${provider.toUpperCase()}.`
      } else if (errorMessage.includes('API error')) {
        errorMessage = `Provider API error: ${errorMessage}. Please check your API key and try again.`
      } else if (errorMessage.includes('network') || errorMessage.includes('fetch')) {
        errorMessage = 'Network error: Could not connect to the server. Make sure the backend is running on port 8000.'
      }
      
      alert(`Error: ${errorMessage}`)
      setFailedMessage(errorMessage)
    } finally {
      setLoading(false)
    }
  }

  const handleCheckStatus = async () => {
    if (!taskId) {
      alert('No task ID available. Please start a task first.')
      return
    }

    if (!provider) {
      alert('No provider selected')
      return
    }

    setPolling(true)
    try {
      const response = await fetch(`${API_BASE}/api/status/${provider}/${taskId}`)
      
      if (!response.ok) {
        let errorMessage = 'Failed to fetch status'
        try {
          const errorData = await response.json()
          errorMessage = errorData.detail || errorData.message || errorMessage
        } catch {
          const errorText = await response.text()
          errorMessage = errorText || errorMessage
        }
        throw new Error(errorMessage)
      }

      const data = await response.json()
      setStatus(data.status)
      setFailedMessage(data.failed_message || '')

      if (data.status === 'completed' && data.result_url) {
        setResultUrl(data.result_url)
        setPolling(false)
      } else if (data.status === 'failed') {
        setPolling(false)
        const failMsg = data.failed_message || 'Unknown error'
        alert(`Task failed: ${failMsg}`)
        setFailedMessage(failMsg)
      } else {
        setPolling(false)
      }
    } catch (error) {
      const errorMessage = error.message || 'An unexpected error occurred'
      alert(`Error checking status: ${errorMessage}`)
      setFailedMessage(errorMessage)
      setPolling(false)
    }
  }

  const startPolling = () => {
    if (!taskId || polling) return

    // Clear any existing interval
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
    }

    setPolling(true)

    // Initial check
    const checkStatus = async () => {
      try {
        const response = await fetch(`${API_BASE}/api/status/${provider}/${taskId}`)
        
        if (!response.ok) {
          clearInterval(intervalRef.current)
          setPolling(false)
          intervalRef.current = null
          return
        }

        const data = await response.json()
        setStatus(data.status)
        setFailedMessage(data.failed_message || '')

        if (data.status === 'completed' && data.result_url) {
          setResultUrl(data.result_url)
          clearInterval(intervalRef.current)
          setPolling(false)
          intervalRef.current = null
        } else if (data.status === 'failed') {
          clearInterval(intervalRef.current)
          setPolling(false)
          intervalRef.current = null
          const failMsg = data.failed_message || 'Unknown error'
          alert(`Task failed: ${failMsg}`)
          setFailedMessage(failMsg)
        }
      } catch (error) {
        clearInterval(intervalRef.current)
        setPolling(false)
        intervalRef.current = null
        const errorMessage = error.message || 'Error checking status'
        console.error('Polling error:', error)
        setFailedMessage(errorMessage)
      }
    }

    // Check immediately
    checkStatus()

    // Then poll every 3 seconds
    intervalRef.current = setInterval(checkStatus, 3000)
  }

  const stopPolling = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
      setPolling(false)
    }
  }

  useEffect(() => {
    if (!hasHydratedRef.current) return
    if (!taskId || !status || status === 'completed' || status === 'failed' || polling) {
      return
    }
    startPolling()
  }, [taskId, status])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [])

  return (
    <div className="app">
      <div className="container">
        <h1>🎬 Multi-Provider Image to Video Generator</h1>
        
        <div className="form-section">
          <div className="form-group">
            <label htmlFor="provider">AI Provider *</label>
            <select
              id="provider"
              value={provider}
              onChange={(e) => setProvider(e.target.value)}
              disabled={loading}
            >
              <option value="a2e">A2E</option>
              <option value="did">D-ID</option>
              <option value="heygen">HeyGen</option>
            </select>
          </div>

          <div className="form-group">
            <label>Image Source *</label>
            <div style={{ marginBottom: '10px' }}>
              <label style={{ marginRight: '20px' }}>
                <input
                  type="radio"
                  value="file"
                  checked={uploadMode === 'file'}
                  onChange={(e) => {
                    setUploadMode(e.target.value)
                    setImageUrl('')
                    setSelectedFile(null)
                    setImagePreview('')
                  }}
                  disabled={loading}
                />
                Upload from Device
              </label>
              <label>
                <input
                  type="radio"
                  value="url"
                  checked={uploadMode === 'url'}
                  onChange={(e) => {
                    setUploadMode(e.target.value)
                    setSelectedFile(null)
                    setImagePreview('')
                  }}
                  disabled={loading}
                />
                Enter URL
              </label>
            </div>

            {uploadMode === 'file' ? (
              <div>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleFileSelect}
                  disabled={loading || uploading}
                  style={{ marginBottom: '10px' }}
                />
                {selectedFile && (
                  <div style={{ marginBottom: '10px' }}>
                    <button
                      type="button"
                      onClick={handleUpload}
                      disabled={loading || uploading || imageUrl}
                      style={{
                        padding: '8px 16px',
                        backgroundColor: '#4CAF50',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        marginRight: '10px'
                      }}
                    >
                      {uploading ? 'Uploading...' : imageUrl ? 'Uploaded ✓' : 'Upload Image'}
                    </button>
                    {imagePreview && (
                      <img
                        src={imagePreview}
                        alt="Preview"
                        style={{
                          maxWidth: '200px',
                          maxHeight: '200px',
                          marginTop: '10px',
                          borderRadius: '4px'
                        }}
                      />
                    )}
                  </div>
                )}
                {imageUrl && (
                  <div style={{ color: 'green', fontSize: '14px', marginTop: '5px' }}>
                    ✓ Image uploaded: {imageUrl}
                  </div>
                )}
              </div>
            ) : (
              <input
                id="imageUrl"
                type="text"
                value={imageUrl}
                onChange={(e) => setImageUrl(e.target.value)}
                placeholder="https://example.com/image.jpg"
                disabled={loading}
              />
            )}
          </div>

          <div className="form-group">
            <label htmlFor="text">Text *</label>
            <textarea
              id="text"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Hello there, welcome to my video!"
              rows={3}
              disabled={loading}
            />
          </div>

          <div className="button-group">
            <button 
              onClick={handleStart} 
              disabled={loading || uploading || (!imageUrl.trim() && uploadMode === 'url') || (!selectedFile && uploadMode === 'file') || !text.trim()}
              className="btn btn-primary"
            >
              {loading ? 'Starting...' : uploading ? 'Uploading...' : 'Start Image2Video'}
            </button>
            <button 
              onClick={handleCheckStatus} 
              disabled={!taskId || polling}
              className="btn btn-secondary"
            >
              {polling ? 'Checking...' : 'Check Status'}
            </button>
            {taskId && status !== 'completed' && status !== 'failed' && (
              <>
                {!polling ? (
                  <button 
                    onClick={startPolling} 
                    className="btn btn-secondary"
                  >
                    Start Auto-Polling
                  </button>
                ) : (
                  <button 
                    onClick={stopPolling} 
                    className="btn btn-secondary"
                  >
                    Stop Polling
                  </button>
                )}
              </>
            )}
          </div>
        </div>

        {(taskId || status) && (
          <div className="status-section">
            <h2>Task Status</h2>
            {taskId && (
              <div className="status-item">
                <strong>Task ID:</strong> <code>{taskId}</code>
              </div>
            )}
            {provider && (
              <div className="status-item">
                <strong>Provider:</strong> <span className="status-badge">{provider.toUpperCase()}</span>
              </div>
            )}
            {status && (
              <div className="status-item">
                <strong>Status:</strong> <span className={`status-badge status-${status}`}>{status}</span>
              </div>
            )}
            {failedMessage && (
              <div className="status-item error">
                <strong>Error:</strong> {failedMessage}
              </div>
            )}
          </div>
        )}

        {resultUrl && (
          <div className="video-section">
            <h2>Generated Video</h2>
            <div className="video-container">
              <video controls src={resultUrl} className="video-player">
                Your browser does not support the video tag.
              </video>
            </div>
            <div className="video-link">
              <a href={resultUrl} target="_blank" rel="noopener noreferrer" style={{ marginRight: '15px' }}>
                Open video in new tab
              </a>
              <a 
                href={resultUrl} 
                download 
                style={{
                  padding: '8px 16px',
                  backgroundColor: '#2196F3',
                  color: 'white',
                  textDecoration: 'none',
                  borderRadius: '4px',
                  display: 'inline-block'
                }}
              >
                Download Video
              </a>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App

