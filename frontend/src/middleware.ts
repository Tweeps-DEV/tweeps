import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

const ROUTE_CONFIG = {
  public: [
    '/',
    '/login',
    '/signup',
    '/forgot-password',
  ],

  protected: [
    '/dashboard',
    '/cart',
    '/menu',
    '/orders',
    '/track-order',
    '/profile',
  ],

  bypass: [
    '/api',
    '/_next/static',
    '/_next/image',
    '/favicon.ico',
    '/public',
  ]
}

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  const session = request.cookies.get('session')?.value

  if (ROUTE_CONFIG.bypass.some(path => pathname.startsWith(path))) {
    return NextResponse.next()
  }

  if (ROUTE_CONFIG.public.includes(pathname)) {
    if ((pathname === '/login' || pathname === '/signup') && session) {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/verify`, {
          headers: {
            Authorization: `Bearer ${session}`
          }
        });
        
        if (response.ok) {
          return NextResponse.redirect(new URL('/dashboard', request.url))
        }
      } catch (error) {
        return clearSessionAndRedirect(request)
      }
    }
    return NextResponse.next()
  }

  const requiresAuth = ROUTE_CONFIG.protected.some(path => pathname.startsWith(path))
  
  if (requiresAuth) {
    if (!session) {
      return redirectToLogin(request, pathname)
    }

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/verify`, {
        headers: {
          Authorization: `Bearer ${session}`
        }
      });
      
      if (!response.ok) {
        const data = await response.json().catch(() => ({}))
        
        if (response.status === 401) {
          let message = 'Session expired. Please login again.'
          
          if (data.message?.includes('Token has expired')) {
            message = 'Your session has expired. Please login again.'
          } else if (data.message?.includes('Token has been revoked')) {
            message = 'Your session was ended. Please login again.'
          } else if (data.message?.includes('User account is disabled')) {
            message = 'Your account has been disabled. Please contact support.'
          }
          
          return clearSessionAndRedirect(request, pathname, message)
        }
        
        return clearSessionAndRedirect(request, pathname)
      }
      
      return NextResponse.next()
    } catch (error) {
      return clearSessionAndRedirect(request, pathname, 'Authentication failed. Please login again.')
    }
  }

  return NextResponse.next()
}

function clearSessionAndRedirect(
  request: NextRequest, 
  returnPath?: string, 
  message?: string
) {
  const loginUrl = new URL('/login', request.url)
  
  if (returnPath) {
    loginUrl.searchParams.set('from', returnPath)
  }
  
  if (message) {
    loginUrl.searchParams.set('error', encodeURIComponent(message))
  }
  
  const response = NextResponse.redirect(loginUrl)
  
  response.cookies.delete('session', {
    secure: true,
    httpOnly: true,
    sameSite: 'strict'
  })
  
  return response
}

function redirectToLogin(request: NextRequest, returnPath: string) {
  const loginUrl = new URL('/login', request.url)
  loginUrl.searchParams.set('from', returnPath)
  return NextResponse.redirect(loginUrl)
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico|public/|api/).*)',
  ],
}
