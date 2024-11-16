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

export const storeTokens = (tokens: AuthTokens) => {
  localStorage.setItem('access_token', tokens.access_token);
  if (tokens.refresh_token) {
    localStorage.setItem('refresh_token', tokens.refresh_token);
  }
};

export const removeTokens = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
};

export const getAccessToken = () => {
  return localStorage.getItem('access_token');
};

export const apiClient = async (endpoint: string, options: RequestInit = {}) => {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';
  const accessToken = getAccessToken();
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
    ...options.headers,
  };

  const response = await fetch(`${baseUrl}${endpoint}`, {
    ...options,
    headers,
    credentials: 'include', // Add this to handle cookies properly
  });

  if (response.status === 401) {
    removeTokens();
    window.location.href = '/login';
    throw new Error('Session expired. Please login again.');
  }

  const data = await response.json();
  
  if (!response.ok) {
    if (response.status === 400 && data.errors) {
      // Handle validation errors
      throw new Error(Object.values(data.errors).join(', '));
    }
    throw new Error(data.message || 'An error occurred');
  }

  return data;
};

export const login = async (credentials: LoginCredentials): Promise<AuthResponse> => {
  const data = await apiClient('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify(credentials),
  });
  
  storeTokens(data.tokens);
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
  
  if (data.tokens) {
    storeTokens(data.tokens);
  }
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
    removeTokens();
  }
};
