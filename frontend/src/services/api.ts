import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
  timeout: 0,
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

export async function getHealth(): Promise<HealthResponse> {
  const response = await api.get<HealthResponse>(
    "/api/health",
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
  );

  return response.data;
}

export async function askQuestion(
  question: string,
): Promise<ChatResponse> {
  const response = await api.post<ChatResponse>(
    "/api/chat",
    {
      question,
    },
  );

  return response.data;
}

export default api;