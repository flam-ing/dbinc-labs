import { useState } from 'react'
import { addEntry } from './entries.js'
import { mask } from './privacy.js'

export default function App() {
  const [entries, setEntries] = useState([])
  const [name, setName] = useState('')
  const [message, setMessage] = useState('')

  function handleSubmit(event) {
    event.preventDefault()
    if (!name.trim() || !message.trim()) return
    setEntries(addEntry(entries, name, message))
    setMessage('')
  }

  return (
    <main style={{ maxWidth: 480, margin: '40px auto', fontFamily: 'sans-serif' }}>
      <h1>방명록</h1>
      <form onSubmit={handleSubmit}>
        <input placeholder="이름" value={name} onChange={(e) => setName(e.target.value)} />
        <input placeholder="남길 말" value={message} onChange={(e) => setMessage(e.target.value)} />
        <button type="submit">남기기</button>
      </form>
      <ul>
        {entries.map((entry, i) => (
          // 화면에 보여 주기 전에 개인정보를 가려요.
          <li key={i}>
            <b>{entry.name}</b> {mask(entry.message)}
          </li>
        ))}
      </ul>
    </main>
  )
}
