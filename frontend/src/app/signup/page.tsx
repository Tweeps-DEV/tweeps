'use client';

import type { NextPage } from 'next';
import React, { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertCircle, Eye, EyeOff, ArrowRight, Loader2, X, Home } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { toast } from '@/components/ui/use-toast';
import { Button } from '@/components/ui/button';
import { signup } from '@/lib/auth'

interface FormData {
  username: string;
  email: string;
  phone_contact: string;
  password: string;
  confirm_password: string;
}

interface ValidationErrors {
  username?: string;
  email?: string;
  phone_contact?: string;
  password?: string;
  confirm_password?: string;
}

const SignupPage: NextPage = () => {
  const router = useRouter();
  const [formData, setFormData] = useState<FormData>({
    username: '',
    email: '',
    phone_contact: '',
    password: '',
    confirm_password: '',
  });

  const [showPassword, setShowPassword] = useState({
    password: false,
    confirm: false,
  });

  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [validationErrors, setValidationErrors] = useState<ValidationErrors>({});

  const validateForm = useCallback((): boolean => {
    const errors: ValidationErrors = {};
    let isValid = true;

    // Validation
    if (!formData.username.trim()) {
      errors.username = 'Username is required';
      isValid = false;
    } else if (formData.username.trim().length < 3) {
      errors.username = 'Username must be at least 3 characters';
      isValid = false;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!formData.email) {
      errors.email = 'Email is required';
      isValid = false;
    } else if (!emailRegex.test(formData.email)) {
      errors.email = 'Please enter a valid email address';
      isValid = false;
    }

    const phoneRegex = /^\+?1?\d{9,15}$/;
    if (!formData.phone_contact) {
      errors.phone_contact = 'Phone number is required';
      isValid = false;
    } else if (!phoneRegex.test(formData.phone_contact)) {
      errors.phone_contact = 'Please enter a valid phone number';
      isValid = false;
    }

    if (!formData.password) {
      errors.password = 'Password is required';
      isValid = false;
    } else if (formData.password.length < 8) {
      errors.password = 'Password must be at least 8 characters';
      isValid = false;
    } else if (!/^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$/.test(formData.password)) {
      errors.password = 'Password must contain at least one letter, one number, and one special character (@$!%*#?&)';
      isValid = false;
    }

    if (!formData.confirm_password) {
      errors.confirm_password = 'Please confirm your password';
      isValid = false;
    } else if (formData.password !== formData.confirm_password) {
      errors.confirm_password = 'Passwords do not match';
      isValid = false;
    }

    setValidationErrors(errors);
    return isValid;
  }, [formData]);


  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!validateForm()) {
      return;
    }

    setLoading(true);

    try {
      await signup({
        username: formData.username.trim(),
        email: formData.email.toLowerCase(),
        phone_contact: formData.phone_contact,
        password: formData.password,
      });

      toast({
        title: "Account created successfully",
        description: "Redirecting to login...",
        duration: 2000,
      });

      setTimeout(() => {
        router.push('/login');
      }, 500);

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An unexpected error occurred';
      setError(errorMessage);

      toast({
        variant: "destructive",
        title: "Signup failed",
        description: errorMessage,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (validationErrors[name as keyof ValidationErrors]) {
      setValidationErrors(prev => ({ ...prev, [name]: undefined }));
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-[#FFD6E0]/20 flex flex-col justify-center relative">
      <Link 
        href="/"
        className="absolute top-4 left-4 p-2 text-gray-600 hover:text-gray-900 transition-colors"
        aria-label="Back to home"
      >
        <Home className="w-6 h-6" />
      </Link>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="w-full px-4 py-8 sm:px-6 lg:px-8"
      >
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          <img 
            src="/tweeps-logo.svg" 
            alt="Tweeps Logo" 
            className="mx-auto h-20 w-auto sm:h-20" 
          />
          <h1 className="mt-6 text-center text-2xl sm:text-3xl font-extrabold text-gray-900 tracking-tight">
            Create your account
          </h1>
          <p className="mt-2 text-center text-sm text-gray-600">
            Join Tweeps today and start ordering
          </p>
        </div>

        <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
          <div className="bg-white py-8 px-4 shadow-xl shadow-black/5 sm:rounded-lg sm:px-10 border border-gray-100">
            <AnimatePresence mode="wait">
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="mb-4"
                >
                  <Alert variant="destructive" className="flex items-center">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription className="ml-2">{error}</AlertDescription>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="ml-auto p-0 h-auto"
                      onClick={() => setError('')}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </Alert>
                </motion.div>
              )}
            </AnimatePresence>

            <form className="space-y-6" onSubmit={handleSubmit} noValidate>
              {/* Name Input */}
              <div>
                <label 
                  htmlFor="username" 
                  className="block text-sm font-medium text-gray-700"
                >
                  Username
                </label>
                <div className="mt-1">
                  <input
                    id="username"
                    name="username"
                    type="text"
                    autoComplete="name"
                    required
                    value={formData.username}
                    onChange={handleChange}
                    className={`appearance-none block w-full px-3 py-2 border ${
                      validationErrors.username ? 'border-red-300' : 'border-gray-300'
                    } rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-[#f2ae2a] focus:border-[#f2ae2a] sm:text-sm transition-colors hover:border-gray-400`}
                    placeholder="JohnDoe"
                    aria-invalid={!!validationErrors.username}
                    aria-describedby={validationErrors.username ? "name-error" : undefined}
                  />
                  {validationErrors.username && (
                    <p className="mt-1 text-sm text-red-600" id="name-error">
                      {validationErrors.username}
                    </p>
                  )}
                </div>
              </div>

              {/* Email Input */}
              <div>
                <label 
                  htmlFor="email" 
                  className="block text-sm font-medium text-gray-700"
                >
                  Email address
                </label>
                <div className="mt-1">
                  <input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    value={formData.email}
                    onChange={handleChange}
                    className={`appearance-none block w-full px-3 py-2 border ${
                      validationErrors.email ? 'border-red-300' : 'border-gray-300'
                    } rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-[#f2ae2a] focus:border-[#f2ae2a] sm:text-sm transition-colors hover:border-gray-400`}
                    placeholder="you@example.com"
                    aria-invalid={!!validationErrors.email}
                    aria-describedby={validationErrors.email ? "email-error" : undefined}
                  />
                  {validationErrors.email && (
                    <p className="mt-1 text-sm text-red-600" id="email-error">
                      {validationErrors.email}
                    </p>
                  )}
                </div>
              </div>

              {/* Phone Input */}
              <div>
                <label 
                  htmlFor="phone" 
                  className="block text-sm font-medium text-gray-700"
                >
                  Phone Number
                </label>
                <div className="mt-1">
                  <input
                    id="phone_contact"
                    name="phone_contact"
                    type="tel"
                    autoComplete="tel"
                    required
                    value={formData.phone}
                    onChange={handleChange}
                    className={`appearance-none block w-full px-3 py-2 border ${
                      validationErrors.phone ? 'border-red-300' : 'border-gray-300'
                    } rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-[#f2ae2a] focus:border-[#f2ae2a] sm:text-sm transition-colors hover:border-gray-400`}
                    placeholder="+254 712345678"
                    aria-invalid={!!validationErrors.phone}
                    aria-describedby={validationErrors.phone ? "phone-error" : undefined}
                  />
                  {validationErrors.phone && (
                    <p className="mt-1 text-sm text-red-600" id="phone-error">
                      {validationErrors.phone}
                    </p>
                  )}
                </div>
              </div>

              {/* Password Input */}
              <div>
                <label 
                  htmlFor="password" 
                  className="block text-sm font-medium text-gray-700"
                >
                  Password
                </label>
                <div className="mt-1 relative">
                  <input
                    id="password"
                    name="password"
                    type={showPassword.password ? 'text' : 'password'}
                    autoComplete="new-password"
                    required
                    value={formData.password}
                    onChange={handleChange}
                    className={`appearance-none block w-full px-3 py-2 border ${
                      validationErrors.password ? 'border-red-300' : 'border-gray-300'
                    } rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-[#f2ae2a] focus:border-[#f2ae2a] sm:text-sm transition-colors hover:border-gray-400`}
                    placeholder="••••••••"
                    aria-invalid={!!validationErrors.password}
                    aria-describedby={validationErrors.password ? "password-error" : undefined}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(prev => ({ ...prev, password: !prev.password }))}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    aria-label={showPassword.password ? "Hide password" : "Show password"}
                  >
                    {showPassword.password ? (
                      <EyeOff className="h-4 w-4 text-gray-400 hover:text-gray-600" />
                    ) : (
                      <Eye className="h-4 w-4 text-gray-400 hover:text-gray-600" />
                    )}
                  </button>
                  {validationErrors.password && (
                    <p className="mt-1 text-sm text-red-600" id="password-error">
                      {validationErrors.password}
                    </p>
                  )}
                </div>
              </div>

              {/* Confirm Password Input */}
              <div>
                <label 
                  htmlFor="confirm_password" 
                  className="block text-sm font-medium text-gray-700"
                >
                  Confirm Password
                </label>
                <div className="mt-1 relative">
                  <input
                    id="confirm_password"
                    name="confirm_password"
                    type={showPassword.confirm ? 'text' : 'password'}
                    autoComplete="new-password"
                    required
                    value={formData.confirm_password}
                    onChange={handleChange}
                    className={`appearance-none block w-full px-3 py-2 border ${
                      validationErrors.confirm_password ? 'border-red-300' : 'border-gray-300'
                    } rounded-m} rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-[#f2ae2a] focus:border-[#f2ae2a] sm:text-sm transition-colors hover:border-gray-400`}
                    placeholder="••••••••"
                    aria-invalid={!!validationErrors.confirm_password}
                    aria-describedby={validationErrors.confirm_password ? "confirm-password-error" : undefined}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(prev => ({ ...prev, confirm: !prev.confirm }))}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    aria-label={showPassword.confirm ? "Hide password" : "Show password"}
                  >
                    {showPassword.confirm ? (
                      <EyeOff className="h-4 w-4 text-gray-400 hover:text-gray-600" />
                    ) : (
                      <Eye className="h-4 w-4 text-gray-400 hover:text-gray-600" />
                    )}
                  </button>
                  {validationErrors.confirm_password && (
                    <p className="mt-1 text-sm text-red-600" id="confirm-password-error">
                      {validationErrors.confirm_password}
                    </p>
                  )}
                </div>
              </div>

              {/* Submit Button */}
              <div>
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full flex justify-center items-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-[#f2ae2a] hover:bg-[#d99b24] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#f2ae2a] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin mr-2" />
                      <span>Creating account...</span>
                    </>
                  ) : (
                    <>
                      <ArrowRight className="h-4 w-4 mr-2" />
                      <span>Create account</span>
                    </>
                  )}
                </button>
              </div>
            </form>

            {/* Divider and Login Link */}
            <div className="mt-6">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-300" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-white text-gray-500">
                    Already have an account?
                  </span>
                </div>
              </div>

              <div className="mt-6">
                <Link href="/login" passHref>
                  <Button
                    variant="outline"
                    className="w-full"
                  >
                    Sign in instead
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default SignupPage;
