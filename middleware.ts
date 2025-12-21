import { NextRequest, NextResponse } from 'next/server'

const PUBLIC_PATHS = ['/login', '/signup', '/api/', '/_next/', '/favicon.ico', '/assets/', '/public/']

export function middleware(req: NextRequest) {
  const { pathname } = req.nextUrl

  const { pathname } = req.nextUrl

  // Always allow the homepage
  if (pathname === '/') return NextResponse.next()

  // Allow public paths
  for (const p of PUBLIC_PATHS) {
    if (pathname.startsWith(p)) return NextResponse.next()
  }

  // Only require session for protected routes (history and saved results).
  // Allow homepage and analysis without login per product request.
  const protectedPrefixes = ['/history', '/results', '/report', '/technical-report']
  for (const p of protectedPrefixes) {
    if (pathname.startsWith(p)) {
      const session = req.cookies.get('session')
      if (!session) {
        const url = req.nextUrl.clone()
        url.pathname = '/login'
        return NextResponse.redirect(url)
      }
      break
    }
  }

  return NextResponse.next()
}

export const config = {
  // Only run middleware on routes that might require protection; keep home and analyze public
  matcher: ['/history/:path*', '/results/:path*', '/report/:path*', '/technical-report/:path*']
}
