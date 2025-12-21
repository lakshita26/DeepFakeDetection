import { promises as fs } from 'fs'
import { join } from 'path'
import bcrypt from 'bcryptjs'
import crypto from 'crypto'

const DATA_DIR = process.cwd() + '/data'
const USERS_FILE = join(DATA_DIR, 'users.json')
const SESSIONS_FILE = join(DATA_DIR, 'sessions.json')

type User = {
  name: string
  email: string
  dob: string
  passwordHash: string
  createdAt: string
}

async function _readJSON(path: string, fallback: any) {
  try {
    const raw = await fs.readFile(path, 'utf8')
    return JSON.parse(raw)
  } catch (e) {
    return fallback
  }
}

async function _writeJSON(path: string, data: any) {
  await fs.mkdir(DATA_DIR, { recursive: true })
  await fs.writeFile(path, JSON.stringify(data, null, 2), 'utf8')
}

export async function findUserByEmail(email: string): Promise<User | null> {
  const users: User[] = await _readJSON(USERS_FILE, [])
  const u = users.find((x) => x.email.toLowerCase() === String(email).toLowerCase())
  return u || null
}

export async function createUser(name: string, email: string, dob: string, password: string) {
  const users: User[] = await _readJSON(USERS_FILE, [])
  const existing = users.find((x) => x.email.toLowerCase() === String(email).toLowerCase())
  if (existing) throw new Error('User already exists')

  const salt = bcrypt.genSaltSync(10)
  const passwordHash = bcrypt.hashSync(password, salt)

  const user: User = {
    name,
    email,
    dob,
    passwordHash,
    createdAt: new Date().toISOString()
  }

  users.push(user)
  await _writeJSON(USERS_FILE, users)
  return user
}

export async function verifyPassword(email: string, password: string) {
  const user = await findUserByEmail(email)
  if (!user) return false
  return bcrypt.compareSync(password, user.passwordHash)
}

export async function createSession(email: string, maxAgeSeconds = 60 * 60 * 24 * 7) {
  const sessions = await _readJSON(SESSIONS_FILE, {})
  const token = crypto.randomBytes(32).toString('hex')
  const expiresAt = Date.now() + maxAgeSeconds * 1000
  sessions[token] = { email, expiresAt }
  await _writeJSON(SESSIONS_FILE, sessions)
  return { token, expiresAt }
}

export async function getSession(token: string) {
  const sessions = await _readJSON(SESSIONS_FILE, {})
  const s = sessions[token]
  if (!s) return null
  if (s.expiresAt < Date.now()) {
    // cleanup expired
    delete sessions[token]
    await _writeJSON(SESSIONS_FILE, sessions)
    return null
  }
  return s
}

export async function deleteSession(token: string) {
  const sessions = await _readJSON(SESSIONS_FILE, {})
  if (sessions[token]) {
    delete sessions[token]
    await _writeJSON(SESSIONS_FILE, sessions)
  }
}

export async function getUserFromSession(token: string) {
  const s = await getSession(token)
  if (!s) return null
  const user = await findUserByEmail(s.email)
  return user
}

export default {
  findUserByEmail,
  createUser,
  verifyPassword,
  createSession,
  getSession,
  deleteSession,
  getUserFromSession
}
