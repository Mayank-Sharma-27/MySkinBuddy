
"use client";
export const dynamic = "force-dynamic";
export const revalidate = 0;

import React from "react";
import UserProfileForm from "../components/UserProfileForm";
import { ProtectedRoute } from "../components/ProtectedRoute";
import { Container } from "../components/ui/Container";
import Navbar from "../components/Navbar";
import { Footer } from "../components/Footer";

export default function ProfilePage() {
  return (
    <ProtectedRoute>
      <div className="min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-grow">
          <Container>
            <div className="py-8">
              <h1 className="text-3xl font-bold text-center mb-8 bg-gradient-to-r from-primary-600 to-secondary-600 bg-clip-text text-transparent">
                Your Skin Profile
              </h1>
              <p className="text-gray-600 text-center mb-8 max-w-2xl mx-auto">
                Tell us about your skin to help us provide better personalized
                recommendations and answers to your questions.
              </p>
              <UserProfileForm />
            </div>
          </Container>
        </main>
        <Footer />
      </div>
    </ProtectedRoute>
  );
}
