import axios from "axios";
import type { ResearchRequest, ResearchResult } from "../types/api";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const startResearch = async (data: ResearchRequest): Promise<ResearchResult> => {
  const response = await apiClient.post<ResearchResult>("/research/", data);
  return response.data;
};

export const fetchHistory = async (): Promise<{company_name: string, website: string, created_at: string}[]> => {
  const response = await apiClient.get("/research/history");
  return response.data;
};

export const fetchResearch = async (companyName: string): Promise<ResearchResult> => {
  const response = await apiClient.get<ResearchResult>(`/research/${encodeURIComponent(companyName)}`);
  return response.data;
};

export const fetchLogs = async (): Promise<{logs: string[]}> => {
  const response = await apiClient.get("/research/logs");
  return response.data;
};

export const sendToDiscord = async (companyName: string, config: any) => {
  const response = await apiClient.post(`/discord/send/${encodeURIComponent(companyName)}`, config);
  return response.data;
};

export const downloadPdf = async (companyName: string) => {
  // Use native fetch/window.open or axios blob response for download
  window.open(`${API_BASE_URL}/pdf/${encodeURIComponent(companyName)}`, "_blank");
};
