import { NextRequest } from 'next/server'
import auth from '@/lib/auth'

export async function POST(req: NextRequest) {
  try {
    const body = await req.json()
    const { email, password } = body || {}
    if (!email || !password) {
      return new Response(JSON.stringify({ error: 'Email and password required' }), { status: 400, headers: { 'Content-Type': 'application/json' } })
    }

    const ok = await auth.verifyPassword(email, password)
    if (!ok) {
      return new Response(JSON.stringify({ error: 'Invalid credentials' }), { status: 401, headers: { 'Content-Type': 'application/json' } })
    }

    const { token, expiresAt } = await auth.createSession(email)

    const cookie = `session=${token}; HttpOnly; Path=/; Max-Age=${Math.floor((expiresAt - Date.now()) / 1000)}`

    return new Response(JSON.stringify({ success: true, user: { email }, token }), { status: 200, headers: { 'Content-Type': 'application/json', 'Set-Cookie': cookie } })
  } catch (e: any) {
    return new Response(JSON.stringify({ error: e?.message || 'Server error' }), { status: 500, headers: { 'Content-Type': 'application/json' } })
  }
}
