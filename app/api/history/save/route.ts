import { NextRequest } from 'next/server'
import auth from '@/lib/auth'
import { promises as fs } from 'fs'
import { join } from 'path'

const HISTORY_FILE = process.cwd() + '/data/history.json'

async function readJSON(path: string, fallback: any) {
  try {
    const raw = await fs.readFile(path, 'utf8')
    return JSON.parse(raw)
  } catch (e) {
    return fallback
  }
}

async function writeJSON(path: string, data: any) {
  await fs.writeFile(path, JSON.stringify(data, null, 2), 'utf8')
}

export async function POST(req: NextRequest) {
  try {
    const cookie = req.cookies.get('session')
    if (!cookie) return new Response(JSON.stringify({ error: 'Unauthorized' }), { status: 401, headers: { 'Content-Type': 'application/json' } })

    const user = await auth.getUserFromSession(cookie.value)
    if (!user) return new Response(JSON.stringify({ error: 'Unauthorized' }), { status: 401, headers: { 'Content-Type': 'application/json' } })

    const body = await req.json()
    const history = await readJSON(HISTORY_FILE, {})
    const userList = history[user.email] || []
    const entry = { id: Date.now().toString(), timestamp: new Date().toISOString(), data: body }
    userList.push(entry)
    history[user.email] = userList
    await writeJSON(HISTORY_FILE, history)

    return new Response(JSON.stringify({ success: true, entry }), { status: 201, headers: { 'Content-Type': 'application/json' } })
  } catch (e: any) {
    return new Response(JSON.stringify({ error: e?.message || 'Server error' }), { status: 500, headers: { 'Content-Type': 'application/json' } })
  }
}
