import { useState, useEffect } from 'react'
import './App.css'
import DeviceCard from './components/DeviceCard'
import AlertBanner from './components/AlertBanner'
import { calculateStatus, getHealthScore } from './utils/healthScore'



function App() {

  const [devices, setDevices] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const fetchDevices = () => {
      fetch('http://localhost:8000/health')
        .then(res => res.json())
        .then(health => {
          if (health.drives_readable === 0) {
            throw new Error("No drives found. Try running as Administrator")
          }
          return fetch('http://localhost:8000/devices')

        })
        .then(res => res.json())
        .then(data => {
          const computed = data.map(device => ({
            ...device,
            status: calculateStatus(device),
            health: getHealthScore(device),
          }))
          setDevices(computed)
          setLoading(false)
        })
        .catch(err => {
          console.error('Failed to fetch devices:', err)
          setLoading(false)
        })

    }

    fetchDevices()
    const interval = setInterval(fetchDevices, 30000)
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return <div className="app"><p style={{ color: 'var(--color-muted)' }}>Scanning devices...</p></div>
  }

  if (error) {
    return (
      <div className="app">
        <header className="topbar">
          <h1>Storage Health Monitor</h1>
        </header>
        <div style={{
          background: '#450a0a',
          border: '1px solid #ef4444',
          borderRadius: 'var(--radius)',
          padding: '16px 20px',
          color: '#ef4444',
          fontSize: '14px'
        }}>
          ⚠ {error}
        </div>
      </div>
    )
  }

  return (
    <div className="app">
      <header className="topbar">
        <h1>Storage Health Monitor</h1>
        <span className="subtitle">{devices.length} {devices.length === 1 ? 'device' : 'devices'} connected</span>
      </header>
      <main className="dashboard">
        <AlertBanner devices={devices} />
        {devices.map(device => (
          <DeviceCard key={device.id} device={device} />
        ))}
      </main>
    </div>
  )

}

export default App