import { NextRequest } from 'next/server'
import auth from '@/lib/auth'

export async function POST(req: NextRequest) {
  try {
    const body = await req.json()
    const { name, email, password, dob } = body || {}
    if (!name || !email || !password || !dob) {
      return new Response(JSON.stringify({ error: 'All fields are required' }), { status: 400, headers: { 'Content-Type': 'application/json' } })
    }

    // Basic validation
    if (String(password).length < 4) {
      return new Response(JSON.stringify({ error: 'Password too short' }), { status: 400, headers: { 'Content-Type': 'application/json' } })
    }

    try {
      const user = await auth.createUser(name, email, dob, password)
      return new Response(JSON.stringify({ success: true, user: { name: user.name, email: user.email } }), { status: 201, headers: { 'Content-Type': 'application/json' } })
    } catch (err: any) {
      return new Response(JSON.stringify({ error: err?.message || 'Could not create user' }), { status: 409, headers: { 'Content-Type': 'application/json' } })
    }
  } catch (e: any) {
    return new Response(JSON.stringify({ error: e?.message || 'Server error' }), { status: 500, headers: { 'Content-Type': 'application/json' } })
  }
}
