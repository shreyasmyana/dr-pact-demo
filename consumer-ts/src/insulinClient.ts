/**
 * Insulin Client - TypeScript Wrapper for Risk Algorithm Service
 * 
 * This client communicates with the Python RiskAlgoService
 * to calculate insulin dosages for patients.
 * 
 * ⚠️ DEMO ONLY - Not for actual medical use
 */

import axios, { AxiosInstance } from 'axios';

// ============== TYPE DEFINITIONS ==============

export interface BolusRequest {
  patient_id: string;
  current_glucose_mg_dl: number;
  carbs_grams: number;
  insulin_on_board_units: number;
}

export interface BolusResponse {
  patient_id: string;
  recommended_bolus_units: number;
  correction_units: number;
  carb_coverage_units: number;
  risk_level: 'low' | 'medium' | 'high';
  warnings: string[];
}

export interface BasalAdjustmentRequest {
  patient_id: string;
  glucose_readings: number[];
  current_basal_rate: number;
}

export interface BasalAdjustmentResponse {
  patient_id: string;
  adjusted_basal_rate: number;
  adjustment_percentage: number;
  trend: 'rising' | 'falling' | 'stable';
  action: 'increase' | 'decrease' | 'maintain';
}

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
}

// ============== CLIENT CLASS ==============

export class InsulinClient {
  private client: AxiosInstance;
  private baseUrl: string;

  constructor(baseUrl: string = 'http://localhost:7001') {
    this.baseUrl = baseUrl;
    this.client = axios.create({
      baseURL: baseUrl,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * Check if the RiskAlgoService is healthy
   */
  async healthCheck(): Promise<HealthResponse> {
    const response = await this.client.get<HealthResponse>('/health');
    return response.data;
  }

  /**
   * Calculate bolus insulin dosage
   * 
   * @param request - Patient glucose and carb data
   * @returns Recommended bolus dosage with risk assessment
   */
  async calculateBolus(request: BolusRequest): Promise<BolusResponse> {
    const response = await this.client.post<BolusResponse>(
      '/calculate/bolus',
      request
    );
    return response.data;
  }

  /**
   * Calculate basal rate adjustment based on glucose trends
   * 
   * @param request - Recent glucose readings and current basal rate
   * @returns Adjusted basal rate with trend analysis
   */
  async calculateBasalAdjustment(
    request: BasalAdjustmentRequest
  ): Promise<BasalAdjustmentResponse> {
    const response = await this.client.post<BasalAdjustmentResponse>(
      '/calculate/basal-adjustment',
      request
    );
    return response.data;
  }
}

// ============== CONVENIENCE FUNCTIONS ==============

/**
 * Quick helper to create a client and calculate bolus
 */
export async function quickBolusCalculation(
  patientId: string,
  glucoseMgDl: number,
  carbsGrams: number,
  insulinOnBoard: number = 0,
  serviceUrl: string = 'http://localhost:7001'
): Promise<BolusResponse> {
  const client = new InsulinClient(serviceUrl);
  return client.calculateBolus({
    patient_id: patientId,
    current_glucose_mg_dl: glucoseMgDl,
    carbs_grams: carbsGrams,
    insulin_on_board_units: insulinOnBoard,
  });
}

// Export default instance for quick usage
export default new InsulinClient();
