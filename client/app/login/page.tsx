'use client';
import { useState } from 'react';
import { LoginForm } from '../components/LoginForm';
import { RegisterForm } from '../components/RegisterForm';
import { Navbar } from '../components/Navbar';

export default function AuthPage() {
  const [isLogin, setIsLogin] = useState(true);

  return (
    <div>
      <Navbar />
      <div className="min-h-screen bg-[#faf4f4]">
        <div className="max-w-4xl mx-auto px-4 py-12">
          <h1 className="text-4xl font-bold text-center mb-8 text-[#a984b2]">
            {isLogin ? 'Welcome Back' : 'Create Account'}
          </h1>
          
          <div className="flex justify-center">
            {isLogin ? (
              <LoginForm onToggleForm={() => setIsLogin(false)} />
            ) : (
              <RegisterForm onToggleForm={() => setIsLogin(true)} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
} 