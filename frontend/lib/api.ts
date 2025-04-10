// API service for handling requests to the backend

// Base API URL
const API_URL = "/api"

// Helper function to handle API responses
async function handleResponse(response: Response) {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.message || "An error occurred")
  }
  return response.json()
}

// Helper function to get auth headers
function getAuthHeaders() {
  const token = localStorage.getItem("auth_token")
  return {
    "Content-Type": "application/json",
    Authorization: token ? `Bearer ${token}` : "",
  }
}

// User API
export const userApi = {
  getProfile: async () => {
    const response = await fetch(`${API_URL}/users/profile`, {
      headers: getAuthHeaders(),
    })
    return handleResponse(response)
  },

  updateProfile: async (profileData: any) => {
    const response = await fetch(`${API_URL}/users/profile`, {
      method: "PUT",
      headers: getAuthHeaders(),
      body: JSON.stringify(profileData),
    })
    return handleResponse(response)
  },

  changePassword: async (passwordData: { currentPassword: string; newPassword: string }) => {
    const response = await fetch(`${API_URL}/users/change-password`, {
      method: "PUT",
      headers: getAuthHeaders(),
      body: JSON.stringify(passwordData),
    })
    return handleResponse(response)
  },
}

// Learning prompts API
export const promptsApi = {
  getPrompts: async () => {
    const response = await fetch(`${API_URL}/prompts`, {
      headers: getAuthHeaders(),
    })
    return handleResponse(response)
  },

  createPrompt: async (promptData: { name: string; prompt: string }) => {
    const response = await fetch(`${API_URL}/prompts`, {
      method: "POST",
      headers: getAuthHeaders(),
      body: JSON.stringify(promptData),
    })
    return handleResponse(response)
  },

  updatePrompt: async (id: string, promptData: { prompt: string }) => {
    const response = await fetch(`${API_URL}/prompts/${id}`, {
      method: "PUT",
      headers: getAuthHeaders(),
      body: JSON.stringify(promptData),
    })
    return handleResponse(response)
  },

  deletePrompt: async (id: string) => {
    const response = await fetch(`${API_URL}/prompts/${id}`, {
      method: "DELETE",
      headers: getAuthHeaders(),
    })
    return handleResponse(response)
  },
}

// History API
export const historyApi = {
  getHistory: async () => {
    const response = await fetch(`${API_URL}/history`, {
      headers: getAuthHeaders(),
    })
    return handleResponse(response)
  },
}

