import { useState, useEffect, useRef } from 'react'
import './App.css'

function App() {
  const [ledOn, setLedOn] = useState(false)
  const [connected, setConnected] = useState(false)
  const [buttonPresses, setButtonPresses] = useState(0)
  const [events, setEvents] = useState([])
  const [flash, setFlash] = useState(false)
  const wsRef = useRef(null)

  useEffect(() => {
    wsRef.current = new WebSocket('ws://localhost:8765')

    wsRef.current.onopen = () => {
      console.log('Connected to WebSocket server')
      setConnected(true)
    }

    wsRef.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        // Messages tagged "device" originated from the Pico via the bridge
        if (data.source === 'device' && data.line) {
          setEvents((prev) => [{ line: data.line, timestamp: data.timestamp }, ...prev].slice(0, 20))
          if (data.line === 'BTN:PRESSED') {
            setButtonPresses((prev) => prev + 1)
            setFlash(true)
            setTimeout(() => setFlash(false), 200)
          }
        }
      } catch (e) {
        console.error('Error parsing message:', e)
      }
    }

    wsRef.current.onerror = (error) => console.error('WebSocket error:', error)
    wsRef.current.onclose = () => {
      console.log('Disconnected from WebSocket server')
      setConnected(false)
    }

    return () => {
      wsRef.current?.close()
    }
  }, [])

  const sendCommand = (command) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ command }))
    }
  }

  const toggleLed = () => {
    const next = !ledOn
    setLedOn(next)
    sendCommand(next ? 'LED_ON' : 'LED_OFF')
  }

  return (
    <section id="center" style={{ fontFamily: 'sans-serif', padding: '30px', maxWidth: '420px', margin: '0 auto', textAlign: 'center' }}>
      <h2>LED &amp; Button Control</h2>
      <p style={{ color: connected ? '#2f9e44' : '#d64545', fontSize: '14px' }}>
        {connected ? 'Connected to device bridge' : 'Not connected — is the server/bridge running?'}
      </p>

      <div
        style={{
          width: '60px',
          height: '60px',
          borderRadius: '50%',
          backgroundColor: ledOn ? '#ffd23f' : '#333',
          boxShadow: ledOn ? '0 0 30px 10px rgba(255,210,63,0.7)' : 'none',
          margin: '20px auto',
          transition: 'all 0.2s ease',
        }}
      />

      <button
        onClick={toggleLed}
        style={{
          padding: '10px 20px',
          fontSize: '16px',
          borderRadius: '6px',
          border: 'none',
          cursor: 'pointer',
          backgroundColor: ledOn ? '#d64545' : '#2f9e44',
          color: 'white',
        }}
      >
        {ledOn ? 'Turn LED Off' : 'Turn LED On'}
      </button>

      <div
        style={{
          marginTop: '30px',
          padding: '20px',
          borderRadius: '8px',
          backgroundColor: flash ? '#ffe066' : '#f1f3f5',
          transition: 'background-color 0.15s',
        }}
      >
        <h3 style={{ margin: 0 }}>Physical button presses</h3>
        <p style={{ fontSize: '36px', margin: '10px 0', fontWeight: 'bold' }}>{buttonPresses}</p>
      </div>

      <div style={{ marginTop: '20px', textAlign: 'left' }}>
        <h4>Device log</h4>
        <div style={{ maxHeight: '200px', overflowY: 'auto', border: '1px solid #ddd', borderRadius: '4px', padding: '10px' }}>
          {events.length === 0 ? (
            <p style={{ color: '#999' }}>No events yet</p>
          ) : (
            events.map((e, i) => (
              <div key={i} style={{ fontSize: '13px', marginBottom: '6px' }}>
                <span style={{ color: '#888' }}>{new Date(e.timestamp).toLocaleTimeString()}</span> — {e.line}
              </div>
            ))
          )}
        </div>
      </div>
    </section>
  )
}

export default App
