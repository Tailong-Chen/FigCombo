import axios, { AxiosInstance, AxiosError } from 'axios';
import type { ApiResponse, FigureState, ExportOptions, JournalPreset, PlotType, LayoutTemplate } from '../types/index';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 60000, // 60s timeout for figure generation
    });

    // Request interceptor for auth tokens
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('figcombo_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('figcombo_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Figures
  async createFigure(figure: Partial<FigureState>): Promise<ApiResponse<FigureState>> {
    const response = await this.client.post('/figures', figure);
    return response.data;
  }

  async getFigure(id: string): Promise<ApiResponse<FigureState>> {
    const response = await this.client.get(`/figures/${id}`);
    return response.data;
  }

  async updateFigure(id: string, figure: Partial<FigureState>): Promise<ApiResponse<FigureState>> {
    const response = await this.client.put(`/figures/${id}`, figure);
    return response.data;
  }

  async deleteFigure(id: string): Promise<ApiResponse<void>> {
    const response = await this.client.delete(`/figures/${id}`);
    return response.data;
  }

  async listFigures(): Promise<ApiResponse<FigureState[]>> {
    const response = await this.client.get('/figures');
    return response.data;
  }

  // Preview
  async generatePreview(figure: FigureState): Promise<ApiResponse<string>> {
    const response = await this.client.post('/preview', figure);
    return response.data;
  }

  async generatePanelPreview(panel: unknown): Promise<ApiResponse<string>> {
    const response = await this.client.post('/preview/panel', panel);
    return response.data;
  }

  // Export
  async exportFigure(figureId: string, options: ExportOptions): Promise<Blob> {
    const response = await this.client.post(
      `/export/${figureId}`,
      options,
      { responseType: 'blob' }
    );
    return response.data;
  }

  async getExportFormats(): Promise<ApiResponse<string[]>> {
    const response = await this.client.get('/export/formats');
    return response.data;
  }

  // Plot Types
  async getPlotTypes(): Promise<ApiResponse<PlotType[]>> {
    const response = await this.client.get('/plot-types');
    return response.data;
  }

  async getPlotType(id: string): Promise<ApiResponse<PlotType>> {
    const response = await this.client.get(`/plot-types/${id}`);
    return response.data;
  }

  // Layout Templates
  async getLayoutTemplates(): Promise<ApiResponse<LayoutTemplate[]>> {
    const response = await this.client.get('/templates');
    return response.data;
  }

  async getLayoutTemplate(id: string): Promise<ApiResponse<LayoutTemplate>> {
    const response = await this.client.get(`/templates/${id}`);
    return response.data;
  }

  // Journal Presets
  async getJournalPresets(): Promise<ApiResponse<JournalPreset[]>> {
    const response = await this.client.get('/journals');
    return response.data;
  }

  async getJournalPreset(id: string): Promise<ApiResponse<JournalPreset>> {
    const response = await this.client.get(`/journals/${id}`);
    return response.data;
  }

  // Image Upload
  async uploadImage(file: File): Promise<ApiResponse<{ url: string; size: { width: number; height: number } }>> {
    const formData = new FormData();
    formData.append('image', file);

    const response = await this.client.post('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }

  // Layout Parsing
  async parseLayoutCode(code: string): Promise<ApiResponse<unknown>> {
    const response = await this.client.post('/layout/parse', { code });
    return response.data;
  }

  async validateLayout(layout: unknown): Promise<ApiResponse<{ valid: boolean; errors: string[] }>> {
    const response = await this.client.post('/layout/validate', layout);
    return response.data;
  }

  // Health Check
  async healthCheck(): Promise<ApiResponse<{ status: string; version: string }>> {
    const response = await this.client.get('/health');
    return response.data;
  }
}

export const apiClient = new ApiClient();
export default apiClient;
