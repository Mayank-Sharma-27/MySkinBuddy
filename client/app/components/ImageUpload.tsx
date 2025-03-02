"use client";

import { useState, useRef } from "react";
import { API_URL } from "../config";

interface ImageUploadProps {
  onTextExtracted: (text: string) => void;
  userEmail?: string;
}

export function ImageUpload({ onTextExtracted, userEmail }: ImageUploadProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImageUpload = async (file: File) => {
    try {
      setIsLoading(true);
      setError(null);
      // Get signed URL
      const imageInfo = {
        file_name: `${Date.now()}-${file.name}`,
        file_type: file.type,
      };

      const uploadResponse = await fetch(`${API_URL}/upload-image`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          image_information: imageInfo,
          user_email: userEmail,
        }),
      });

      if (!uploadResponse.ok) {
        throw new Error("Failed to get upload URL");
      }

      const { signed_url } = await uploadResponse.json();

      // Upload to S3 with proper CORS headers
      const uploadResult = await fetch(signed_url, {
        method: "PUT",
        body: file,
        headers: {
          "Content-Type": file.type,
        },
      });

      if (!uploadResult.ok) {
        console.error("Upload failed with status:", uploadResult.status);
        const errorText = await uploadResult.text();
        console.error("Error details:", errorText);
        throw new Error(`Failed to upload image: ${uploadResult.status}`);
      }

      // Get text from image
      const textResponse = await fetch(`${API_URL}/get-data-from-image`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          image_information: imageInfo,
          user_email: userEmail,
        }),
      });

      if (!textResponse.ok) {
        throw new Error("Failed to extract text from image");
      }

      const { extracted_text } = await textResponse.json();
      onTextExtracted(extracted_text);
    } catch (err) {
      console.error("Upload error:", err);
      setError(err instanceof Error ? err.message : "Failed to process image");
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      handleImageUpload(file);
    }
  };

  const handleCameraCapture = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  return (
    <div className="flex flex-col items-center gap-4">
      <input
        type="file"
        ref={fileInputRef}
        accept="image/*"
        capture="environment"
        onChange={handleFileChange}
        className="hidden"
      />

      <button
        onClick={handleCameraCapture}
        disabled={isLoading}
        className={`flex items-center gap-2 px-4 py-2 rounded-full 
                   transition-all duration-200
                   ${
                     isLoading
                       ? "bg-gray-200 text-gray-500"
                       : "bg-primary-100 text-primary-700 hover:bg-primary-200"
                   }`}
      >
        <svg
          className="w-5 h-5"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"
          />
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"
          />
        </svg>
        {isLoading ? "Processing..." : "Search with Photo"}
      </button>

      {error && (
        <p className="text-sm text-red-500 text-center mt-2">{error}</p>
      )}
    </div>
  );
}
