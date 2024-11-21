import NextAuth, { AuthOptions } from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'
import { apiClient } from '@/lib/auth';

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
          const user = await apiClient('/api/auth/login', {
            method: 'POST',
            body: JSON.stringify(credentials),
          });
          return user.user;
        } catch (error) {
          console.error("NextAuth CredentialsProvider authorize Error:", error);
          return null;
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
      session.user = token.user as { id: string, name: string, email: string };
      return session;
    }
  },
  pages: {
    signIn: '/login',
    signOut: '/', // Redirect after sign out
    error: '/login', // Error code is passed in query string as ?error=
  }
};

export default NextAuth(authOptions);
