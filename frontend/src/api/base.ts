import axios from 'axios'

// Base URL for the backend API. Can be overridden via VITE_API_BASE_URL in .env.
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string) ?? 'http://localhost:8000'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

export default apiClient
