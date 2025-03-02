import React, { useState, useEffect } from "react";
import {
  UserProfile,
  getUserProfile,
  saveUserProfile,
} from "../api/userProfile";
import { Button } from "./ui/Button";
import { useAuth } from "../contexts/AuthContext";

const skinTypes = ["Normal", "Dry", "Oily", "Combination", "Sensitive"];

const commonSkinIssues = [
  "Acne",
  "Aging",
  "Dark spots",
  "Dryness",
  "Redness",
  "Sensitivity",
  "Uneven texture",
  "Large pores",
  "Fine lines",
  "Wrinkles",
];

export default function UserProfileForm() {
  const { userProfile, updateUserProfile } = useAuth();
  const [profile, setProfile] = useState<UserProfile>(
    userProfile || {
      skin_type: "",
      skin_issues: [],
      additional_info: "",
      location: "",
    }
  );
  const [loading, setLoading] = useState(!userProfile);
  const [hasAttemptedLoad, setHasAttemptedLoad] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (userProfile) {
      setProfile(userProfile);
      setLoading(false);
    } else if (!hasAttemptedLoad) {
      setHasAttemptedLoad(true);
      loadProfile();
    }
  }, [userProfile, hasAttemptedLoad]);

  const loadProfile = async () => {
    try {
      const data = await getUserProfile();
      setProfile(data);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setIsSaving(true);

    try {
      await saveUserProfile(profile);
      setSuccess("Profile saved successfully!");
      setIsEditing(false);
      // Update the context with the new profile
      updateUserProfile(profile);
      // Reload the profile to ensure we have the latest data
      await loadProfile();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save profile");
    } finally {
      setIsSaving(false);
    }
  };

  const handleSkinIssueToggle = (issue: string) => {
    setProfile((prev) => ({
      ...prev,
      skin_issues: prev.skin_issues.includes(issue)
        ? prev.skin_issues.filter((i) => i !== issue)
        : [...prev.skin_issues, issue],
    }));
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        Loading...
      </div>
    );
  }

  if (!isEditing && profile.skin_type) {
    return (
      <div className="max-w-2xl mx-auto p-6 space-y-8">
        <div className="flex justify-between items-center">
          {success && <div className="text-green-600 text-sm">{success}</div>}
          <Button
            variant="outline"
            onClick={() => setIsEditing(true)}
            className="text-primary-600 border-primary-600 hover:bg-primary-50"
          >
            Edit Profile
          </Button>
        </div>

        <div className="space-y-6">
          <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-100">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Your Skin Profile
            </h3>

            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-medium text-gray-700">Skin Type</h4>
                <p className="mt-1 text-gray-900">{profile.skin_type}</p>
              </div>

              <div>
                <h4 className="text-sm font-medium text-gray-700">
                  Skin Issues
                </h4>
                <div className="mt-1 flex flex-wrap gap-2">
                  {profile.skin_issues.map((issue) => (
                    <span
                      key={issue}
                      className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800"
                    >
                      {issue}
                    </span>
                  ))}
                </div>
              </div>

              {profile.additional_info && (
                <div>
                  <h4 className="text-sm font-medium text-gray-700">
                    Additional Information
                  </h4>
                  <p className="mt-1 text-gray-900 whitespace-pre-wrap">
                    {profile.additional_info}
                  </p>
                </div>
              )}

              {profile.location && (
                <div>
                  <h4 className="text-sm font-medium text-gray-700">
                    Location
                  </h4>
                  <p className="mt-1 text-gray-900">{profile.location}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="max-w-2xl mx-auto p-6 space-y-6">
      {!profile.skin_type && (
        <div className="bg-primary-50 border border-primary-200 rounded-lg p-4 mb-6">
          <p className="text-primary-800 text-sm">
            Please complete your skin profile to help us provide better
            recommendations.
          </p>
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Skin Type
        </label>
        <select
          value={profile.skin_type}
          onChange={(e) =>
            setProfile((prev) => ({ ...prev, skin_type: e.target.value }))
          }
          className="w-full p-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
          required
        >
          <option value="">Select your skin type</option>
          {skinTypes.map((type) => (
            <option key={type} value={type}>
              {type}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Skin Issues (Select all that apply)
        </label>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {commonSkinIssues.map((issue) => (
            <label key={issue} className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={profile.skin_issues.includes(issue)}
                onChange={() => handleSkinIssueToggle(issue)}
                className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
              />
              <span className="text-sm text-gray-700">{issue}</span>
            </label>
          ))}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Additional Information About Your Skin
        </label>
        <textarea
          value={profile.additional_info}
          onChange={(e) =>
            setProfile((prev) => ({ ...prev, additional_info: e.target.value }))
          }
          className="w-full p-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
          rows={4}
          placeholder="Tell us more about your skin concerns, goals, or any other relevant information..."
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Location
        </label>
        <input
          type="text"
          value={profile.location}
          onChange={(e) =>
            setProfile((prev) => ({ ...prev, location: e.target.value }))
          }
          className="w-full p-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
          placeholder="City, Country"
        />
      </div>

      {error && <div className="text-red-600 text-sm">{error}</div>}

      <div className="flex gap-4">
        {isEditing && (
          <Button
            variant="outline"
            type="button"
            onClick={() => {
              setIsEditing(false);
              loadProfile(); // Reset to saved data
            }}
            className="flex-1"
            disabled={isSaving}
          >
            Cancel
          </Button>
        )}
        <Button
          variant="primary"
          type="submit"
          className="flex-1"
          disabled={isSaving}
        >
          {isSaving ? "Saving..." : isEditing ? "Save Changes" : "Save Profile"}
        </Button>
      </div>
    </form>
  );
}
