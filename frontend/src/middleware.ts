import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

const publicPaths = ['/', '/login', '/signup', '/forgot-password', '/cart']

export async function middleware(request: NextRequest) {
  const session = request.cookies.get('session')?.value
  const { pathname } = request.nextUrl

  // For public paths
  if (publicPaths.includes(pathname)) {
    if (pathname === '/login' || pathname === '/signup') {
      // Only redirect if session is valid
      if (session) {
        try {
          // Verify token with your backend
          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/verify`, {
            headers: {
              Authorization: `Bearer ${session}`
            }
          });
          
          if (response.ok) {
            return NextResponse.redirect(new URL('/dashboard', request.url))
          }
        } catch (error) {
          // If verification fails, clear the invalid session cookie
          const response = NextResponse.next()
          response.cookies.delete('session')
          return response
        }
      }
    }
    return NextResponse.next()
  }

  // For protected routes
  if (!session) {
    const loginUrl = new URL('/login', request.url)
    loginUrl.searchParams.set('from', pathname)
    return NextResponse.redirect(loginUrl)
  }

  try {
    // Verify token with your backend
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/verify`, {
      headers: {
        Authorization: `Bearer ${session}`
      }
    });
    
    if (!response.ok) {
      const loginUrl = new URL('/login', request.url)
      loginUrl.searchParams.set('from', pathname)
      return NextResponse.redirect(loginUrl)
    }
    
    return NextResponse.next()
  } catch (error) {
    const loginUrl = new URL('/login', request.url)
    loginUrl.searchParams.set('from', pathname)
    return NextResponse.redirect(loginUrl)
  }
}

export const config = {
  matcher: [
    '/((?!api|_next/static|_next/image|favicon.ico|public/*|.*\\.svg|.*\\.png|.*\\.gif|.*\\.webp).*)',
  ],
}
