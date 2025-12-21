"use client"

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import Image from 'next/image'
import { Shield } from 'lucide-react'

export default function SignupPage() {
  const router = useRouter()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [dob, setDob] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    if (!name || !email || !dob || !password || !confirm) {
      setError('All fields are required')
      return
    }
    if (password !== confirm) {
      setError('Passwords do not match')
      return
    }
    setLoading(true)
    try {
      const res = await fetch('/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, password, dob })
      })
      const data = await res.json()
      if (!res.ok) {
        setError(data?.error || 'Signup failed')
      } else {
        router.push('/login')
      }
    } catch (err: any) {
      setError(err.message || 'Network error')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-md mx-auto bg-white dark:bg-card p-6 rounded-md shadow">
        <div className="flex items-center justify-center mb-4">
          {/* Show project logo if available, otherwise show shield icon */}
          <div className="hidden">
            <Image src="/apple-icon.png" alt="logo" width={56} height={56} className="rounded" />
          </div>
          <Shield className="h-12 w-12 text-primary" />
        </div>
        <h1 className="text-2xl font-semibold mb-4">Create Account</h1>
        <form onSubmit={handleSubmit}>
          <label className="block mb-2">Full name</label>
          <input value={name} onChange={e => setName(e.target.value)} className="w-full p-2 mb-4 border rounded" required />

          <label className="block mb-2">Email</label>
          <input type="email" value={email} onChange={e => setEmail(e.target.value)} className="w-full p-2 mb-4 border rounded" required />

          <label className="block mb-2">Date of birth</label>
          <input type="date" value={dob} onChange={e => setDob(e.target.value)} className="w-full p-2 mb-4 border rounded" required />

          <label className="block mb-2">Password</label>
          <input type="password" value={password} onChange={e => setPassword(e.target.value)} className="w-full p-2 mb-4 border rounded" required />

          <label className="block mb-2">Confirm Password</label>
          <input type="password" value={confirm} onChange={e => setConfirm(e.target.value)} className="w-full p-2 mb-4 border rounded" required />

          {error && <div className="text-red-600 mb-2">{error}</div>}

          <div className="flex items-center justify-end">
            <button type="submit" className="px-4 py-2 bg-primary text-white rounded" disabled={loading}>{loading ? 'Creating...' : 'Create Account'}</button>
          </div>
        </form>
      </div>
    </div>
  )
}
