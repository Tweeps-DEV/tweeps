import NextAuth, { AuthOptions } from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'
import { apiClient } from '@/lib/auth';

const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'; // Use environment variable

export const authOptions: AuthOptions = {
  providers: [
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        email: { label: 'Email', type: 'text', placeholder: 'jsmith@example.com' },
        password: { label: 'Password', type: 'password' }
      },
      async authorize(credentials, req) {
        try {
          const response = await fetch(`${backendUrl}/api/auth/login`, { // Use backendUrl
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(credentials),
          });

          if (!response.ok) {
            const errorData = await response.json();
            console.error("Backend login error:", errorData);
            throw new Error(errorData.message || 'Backend login failed'); // Throw error with message
          }
          const user = await response.json();
          return user.user;
        } catch (error: any) { // Correct type annotation
          console.error("NextAuth CredentialsProvider authorize Error:", error);
          throw new Error(error.message || 'Authentication failed'); // Re-throw error for NextAuth to handle
        }
      }
    })
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.user = user;
      }
      return token;
    },
    async session({ session, token }) {
      session.user = token.user as { id: string; name: string; email: string }; // Add type safety
      return session;
    },
  },
  pages: {
    signIn: '/login',
    signOut: '/',
    error: '/login',
  },
  secret: process.env.NEXTAUTH_SECRET, // Add secret for production
};

export default NextAuth(authOptions);
