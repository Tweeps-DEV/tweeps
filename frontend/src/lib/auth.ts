interface AuthTokens {
  access_token: string;
  refresh_token?: string;
}

interface AuthResponse {
  tokens: AuthTokens;
  user: {
    id: string;
    name: string;
    email: string;
  };
}

interface LoginCredentials {
  email: string;
  password: string;
}

// Store user data in a more structured way
interface UserData {
  id: string;
  name: string;
  email: string;
}

// Helper to handle user data
export const storeUserData = (user: UserData) => {
  localStorage.setItem('user_data', JSON.stringify(user));
};

export const getUserData = (): UserData | null => {
  const data = localStorage.getItem('user_data');
  return data ? JSON.parse(data) : null;
};

export const getUserName = () => {
  const userData = getUserData();
  return userData?.name || 'Guest';
};

// Remove localStorage token storage since we're using HTTP-only cookies
export const clearUserData = () => {
  localStorage.removeItem('user_data');
};

export const apiClient = async (endpoint: string, options: RequestInit = {}) => {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  try {
    const response = await fetch(`${baseUrl}${endpoint}`, {
      ...options,
      headers,
      credentials: 'include', // This ensures cookies are sent with requests
    });

    if (response.status === 401) {
      clearUserData();
      window.location.href = '/login';
      throw new Error('Session expired. Please login again.');
    }

    const data = await response.json();
    
    if (!response.ok) {
      if (response.status === 400 && data.errors) {
        throw new Error(Object.values(data.errors).join(', '));
      }
      throw new Error(data.message || 'An error occurred');
    }

    return data;
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    }
    throw new Error('An unexpected error occurred');
  }
};

export const login = async (credentials: LoginCredentials): Promise<AuthResponse> => {
  const data = await apiClient('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify(credentials),
  });
  
  // Store only user data, not tokens (tokens are in HTTP-only cookies)
  storeUserData(data.user);
  return data;
};

export const signup = async (userData: {
  username: string;
  email: string;
  phone: string;
  password: string;
}): Promise<AuthResponse> => {
  const data = await apiClient('/api/auth/signup', {
    method: 'POST',
    body: JSON.stringify(userData),
  });
  
  storeUserData(data.user);
  return data;
};

export const logout = async () => {
  try {
    await apiClient('/api/auth/logout', {
      method: 'POST',
    });
  } catch (error) {
    console.error('Logout API error:', error);
  } finally {
    clearUserData();
    window.location.href = '/login';
  }
};
