import { NextRequest, NextResponse } from 'next/server'

const PUBLIC_PATHS = ['/login', '/signup', '/api/', '/_next/', '/favicon.ico', '/assets/', '/public/']

export function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl

  // Allow public paths
  for (const p of PUBLIC_PATHS) {
    if (pathname.startsWith(p)) return NextResponse.next()
  }

  // If session cookie missing, redirect to login
  const session = req.cookies.get('session')
  if (!session) {
    const url = req.nextUrl.clone()
    url.pathname = '/login'
    return NextResponse.redirect(url)
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/', '/upload', '/analyze', '/results', '/history', '/about', '/presentation', '/report', '/technical-report']
}
