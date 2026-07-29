import axios from "axios";

const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || DEFAULT_API_BASE_URL
).replace(/\/+$/, "");

const HEALTH_TIMEOUT_MS = 5_000;
const UPLOAD_TIMEOUT_MS = 300_000;
const CHAT_TIMEOUT_MS = 300_000;

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30_000,
  headers: {
    Accept: "application/json",
  },
});

export interface HealthResponse {
  status: string;
  application: string;
}

export interface UploadResponse {
  filename: string;
  source_path: string;
  status: "success" | "skipped" | "failed";
  document_id: number | null;
  chunk_count: number;
  embedding_count: number;
  message: string;
}

export interface SourceResponse {
  document_id: number;
  chunk_id: number;
  chunk_index: number | null;
  filename: string | null;
  file_type: string | null;
  source_path: string | null;
  content: string | null;
  similarity_score: number;
}

export interface ChatResponse {
  question: string;
  answer: string;
  sources: SourceResponse[];
}

interface ApiErrorResponse {
  detail?: string;
  message?: string;
}

export async function getHealth(): Promise<HealthResponse> {
  const response = await api.get<HealthResponse>(
    "/api/health",
    {
      timeout: HEALTH_TIMEOUT_MS,
    },
  );

  return response.data;
}

export async function uploadDocument(
  file: File,
): Promise<UploadResponse> {
  const formData = new FormData();

  formData.append("file", file);

  const response = await api.post<UploadResponse>(
    "/api/upload",
    formData,
    {
      timeout: UPLOAD_TIMEOUT_MS,
    },
  );

  return response.data;
}

export async function askQuestion(
  question: string,
  documentIds: number[],
): Promise<ChatResponse> {
  const response = await api.post<ChatResponse>(
    "/api/chat",
    {
      question,
      document_ids: documentIds,
    },
    {
      timeout: CHAT_TIMEOUT_MS,
    },
  );

  return response.data;
}

export function getApiErrorMessage(
  error: unknown,
  fallbackMessage = "An unexpected error occurred.",
): string {
  if (!axios.isAxiosError<ApiErrorResponse>(error)) {
    return fallbackMessage;
  }

  const backendMessage =
    error.response?.data?.detail ??
    error.response?.data?.message;

  if (backendMessage) {
    return backendMessage;
  }

  if (error.code === "ECONNABORTED") {
    return "The request timed out. Please try again.";
  }

  if (!error.response) {
    return "Unable to connect to the backend service.";
  }

  return error.message || fallbackMessage;
}

export default api;