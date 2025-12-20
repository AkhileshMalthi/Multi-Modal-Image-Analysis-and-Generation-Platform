// API configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

// Types
export interface AnalysisResult {
  success: boolean;
  data: {
    id: number;
    caption?: string;
    objects?: string;
    question?: string;
    answer?: string;
    created_at: string;
  };
}

export interface GenerationJob {
  success: boolean;
  message: string;
  data: {
    job_id: string;
    status: string;
    check_status_url: string;
  };
}

export interface JobStatus {
  success: boolean;
  data: {
    job_id: string;
    task_type: string;
    status: 'pending' | 'processing' | 'completed' | 'failed';
    created_at: string;
    completed_at?: string;
    result_image_url?: string;
    error?: string;
  };
}

export interface UploadResponse {
  message: string;
  data: {
    id: number;
    url: string;
    filename: string;
  };
}

// API functions
export const apiService = {
  // Upload image
  async uploadImage(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Failed to upload image');
    }

    return response.json();
  },

  // Analysis endpoints
  async analyzeCaption(imageUrl: string): Promise<AnalysisResult> {
    const response = await fetch(`${API_BASE_URL}/api/analyze/caption`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image_url: imageUrl }),
    });

    if (!response.ok) {
      throw new Error('Failed to generate caption');
    }

    return response.json();
  },

  async analyzeVQA(imageUrl: string, question: string): Promise<AnalysisResult> {
    const response = await fetch(`${API_BASE_URL}/api/analyze/vqa`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image_url: imageUrl, question }),
    });

    if (!response.ok) {
      throw new Error('Failed to answer question');
    }

    return response.json();
  },

  async analyzeObjects(imageUrl: string): Promise<AnalysisResult> {
    const response = await fetch(`${API_BASE_URL}/api/analyze/object-detection`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image_url: imageUrl }),
    });

    if (!response.ok) {
      throw new Error('Failed to detect objects');
    }

    return response.json();
  },

  // Generation endpoints
  async generateTextToImage(prompt: string, provider?: string): Promise<GenerationJob> {
    const response = await fetch(`${API_BASE_URL}/api/generate/text-to-image`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, provider }),
    });

    if (!response.ok) {
      throw new Error('Failed to start image generation');
    }

    return response.json();
  },

  async generateVariation(imageUrl: string, prompt: string, provider?: string): Promise<GenerationJob> {
    const response = await fetch(`${API_BASE_URL}/api/generate/variation`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image_url: imageUrl, prompt, provider }),
    });

    if (!response.ok) {
      throw new Error('Failed to start variation generation');
    }

    return response.json();
  },

  // Job status
  async getJobStatus(jobId: string): Promise<JobStatus> {
    const response = await fetch(`${API_BASE_URL}/api/jobs/${jobId}`);

    if (!response.ok) {
      throw new Error('Failed to get job status');
    }

    return response.json();
  },

  // Poll job until completion
  async pollJobStatus(
    jobId: string,
    onUpdate?: (status: JobStatus) => void,
    maxAttempts = 30,
    interval = 3000
  ): Promise<JobStatus> {
    for (let i = 0; i < maxAttempts; i++) {
      const status = await this.getJobStatus(jobId);
      
      if (onUpdate) {
        onUpdate(status);
      }

      if (status.data.status === 'completed' || status.data.status === 'failed') {
        return status;
      }

      await new Promise(resolve => setTimeout(resolve, interval));
    }

    throw new Error('Job polling timeout');
  },
};
