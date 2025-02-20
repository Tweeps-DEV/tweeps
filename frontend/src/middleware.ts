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
  const { pathname } = request.nextUrl;
  const session = request.cookies.get('session')?.value;

  if (ROUTE_CONFIG.bypass.some(path => pathname.startsWith(path))) {
    return NextResponse.next();
  }

  if (ROUTE_CONFIG.public.includes(pathname)) {
    if ((pathname === '/login' || pathname === '/signup') && session) {
      const { valid } = await fetchSessionValidity(session, request);
      if (valid) {
        return NextResponse.redirect(new URL('/dashboard', request.url));
      }
    }
    return NextResponse.next();
  }

  const requiresAuth = ROUTE_CONFIG.protected.some(path => pathname.startsWith(path));
  
  if (requiresAuth) {
    if (!session) {
      return redirectToLogin(request, pathname);
    }

    const { valid, message } = await fetchSessionValidity(session, request);
    
    if (!valid) {
      return clearSessionAndRedirect(request, pathname, message);
    }
    
    return NextResponse.next();
  }

  return NextResponse.next();
}

async function fetchSessionValidity(session: string, request: NextRequest) {
  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/verify`, {
      headers: {
        'Authorization': `Bearer ${session}`
      },
      credentials: 'include'
    });

    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      return { valid: false, message: data.message || 'Session verification failed' };
    }

    return { valid: true, message: 'Session is valid' };
  } catch (error) {
    console.error('Session verification failed:', error);
    return { valid: false, message: 'Session could not be verified due to an error' };
  }
}

function clearSessionAndRedirect(request: NextRequest, returnPath?: string, message?: string) {
  const loginUrl = new URL('/login', request.url);
  
  if (returnPath) {
    loginUrl.searchParams.set('from', returnPath);
  }
  
  if (message) {
    loginUrl.searchParams.set('error', encodeURIComponent(message));
  }
  
  const response = NextResponse.redirect(loginUrl);
  
  response.cookies.delete('session', {
    secure: true,
    httpOnly: true,
    sameSite: 'strict'
  });
  
  return response;
}

function redirectToLogin(request: NextRequest, returnPath: string) {
  const loginUrl = new URL('/login', request.url);
  loginUrl.searchParams.set('from', returnPath);
  return NextResponse.redirect(loginUrl);
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico|public/|api/).*)',
  ],
}
