"use client"

import React, { useState } from 'react'

export default function ForgotPage() {
  const [email, setEmail] = useState('')
  const [sent, setSent] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    try {
      const res = await fetch('/api/auth/forgot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email })
      })
      const data = await res.json()
      if (!res.ok) {
        setError(data?.error || 'Request failed')
      } else {
        setSent(true)
      }
    } catch (err: any) {
      setError(err.message || 'Network error')
    }
  }

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-md mx-auto bg-white dark:bg-card p-6 rounded-md shadow">
        <h1 className="text-2xl font-semibold mb-4">Forgot Password</h1>
        {sent ? (
          <div className="text-green-600">If the email exists, a reset link has been sent.</div>
        ) : (
          <form onSubmit={handleSubmit}>
            <label className="block mb-2">Email</label>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)} className="w-full p-2 mb-4 border rounded" required />
            {error && <div className="text-red-600 mb-2">{error}</div>}
            <div className="flex items-center justify-end">
              <button type="submit" className="px-4 py-2 bg-primary text-white rounded">Send Reset Link</button>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}
