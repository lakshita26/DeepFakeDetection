"use client"

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import Image from 'next/image'
import { Shield } from 'lucide-react'

export default function LoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      })
      const data = await res.json()
      if (!res.ok) {
        setError(data?.error || 'Login failed')
      } else {
        // on success, navigate to home
        router.push('/')
      }
    } catch (err: any) {
      setError(err.message || 'Network error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="w-full max-w-sm bg-white dark:bg-card p-6 rounded-md shadow">
        <div className="flex flex-col items-center justify-center mb-4">
          {/* show logo if available */}
          <Image src="/logo.png" alt="logo" width={120} height={120} className="rounded mb-2" />
          <h1 className="text-2xl font-semibold mb-1">Darpana</h1>
          <p className="text-sm text-muted-foreground mb-2">Deepfake Detection</p>
        </div>
        <form onSubmit={handleSubmit}>
          <label className="block mb-2">Email</label>
          <input type="email" value={email} onChange={e => setEmail(e.target.value)} className="w-full p-2 mb-4 border rounded" required />

          <label className="block mb-2">Password</label>
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} className="w-full p-2 mb-4 border rounded" required />

          {error && <div className="text-red-600 mb-2">{error}</div>}

          <div className="flex items-center justify-between">
            <button type="submit" className="px-4 py-2 bg-primary text-white rounded" disabled={loading}>{loading ? 'Signing in...' : 'Sign In'}</button>
            <a href="/forgot" className="text-sm text-muted-foreground">Forgot?</a>
          </div>
        </form>
      </div>
    </div>
  )
}
