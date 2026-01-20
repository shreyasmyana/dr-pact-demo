import { PactV3, MatchersV3 } from '@pact-foundation/pact';
import axios from 'axios';
import path from 'path';

const { string, number, eachLike, like, boolean } = MatchersV3;

const provider = new PactV3({
  consumer: 'InsulinClient',
  provider: 'RiskAlgoService',
  dir: path.resolve(process.cwd(), '../pacts'),
  logLevel: 'warn',
});

describe('RiskAlgoService Contract Tests', () => {
  it('should return health check response', async () => {
    await provider
      .given('the service is healthy')
      .uponReceiving('a health check request')
      .withRequest({
        method: 'GET',
        path: '/health',
      })
      .willRespondWith({
        status: 200,
        body: like({
          status: string('healthy'),
          service: string('RiskAlgoService'),
          version: string('1.0.0'),
        }),
      });

    await provider.executeTest(async (mockServer) => {
      const response = await axios.get(`${mockServer.url}/health`);
      expect(response.status).toBe(200);
      expect(response.data.status).toBe('healthy');
      expect(response.data.service).toBe('RiskAlgoService');
      expect(response.data.version).toBe('1.0.0');
    });
  });

  it('should calculate bolus insulin dosage', async () => {
    await provider
      .given('a patient with valid glucose and carb data')
      .uponReceiving('a bolus calculation request')
      .withRequest({
        method: 'POST',
        path: '/calculate/bolus',
        headers: { 'Content-Type': 'application/json' },
        body: like({
          patient_id: string('patient-123'),
          current_glucose_mg_dl: number(150),
          carbs_grams: number(30),
          insulin_on_board_units: number(5),
        }),
      })
      .willRespondWith({
        status: 200,
        body: like({
          patient_id: string('patient-123'),
          recommended_bolus_units: number(10),
          correction_units: number(5),
          carb_coverage_units: number(3),
          risk_level: string('low'),
          warnings: eachLike(string(''), 0),
        }),
      });

    await provider.executeTest(async (mockServer) => {
      const response = await axios.post(`${mockServer.url}/calculate/bolus`, {
        patient_id: 'patient-123',
        current_glucose_mg_dl: 150,
        carbs_grams: 30,
        insulin_on_board_units: 5,
      });
      expect(response.status).toBe(200);
      expect(response.data.patient_id).toBe('patient-123');
      expect(response.data.recommended_bolus_units).toBeGreaterThan(0);
      expect(response.data.correction_units).toBeGreaterThan(0);
      expect(response.data.carb_coverage_units).toBeGreaterThan(0);
      expect(['low', 'medium', 'high']).toContain(response.data.risk_level);
      expect(response.data.warnings).toEqual([]);
    });
  });

  it('should calculate basal rate adjustment', async () => {
    await provider
      .given('a patient with valid glucose readings and basal rate')
      .uponReceiving('a basal adjustment request')
      .withRequest({
        method: 'POST',
        path: '/calculate/basal-adjustment',
        headers: { 'Content-Type': 'application/json' },
        body: like({
          patient_id: string('patient-123'),
          glucose_readings: eachLike(number(100), 6),
          current_basal_rate: number(10),
        }),
      })
      .willRespondWith({
        status: 200,
        body: like({
          patient_id: string('patient-123'),
          adjusted_basal_rate: number(10),
          adjustment_percentage: number(0),
          trend: string('stable'),
          action: string('maintain'),
        }),
      });

    await provider.executeTest(async (mockServer) => {
      const response = await axios.post(`${mockServer.url}/calculate/basal-adjustment`, {
        patient_id: 'patient-123',
        glucose_readings: [100, 110, 120, 130, 140, 150],
        current_basal_rate: 10,
      });
      expect(response.status).toBe(200);
      expect(response.data.patient_id).toBe('patient-123');
      expect(response.data.adjusted_basal_rate).toBeGreaterThan(0);
      expect(response.data.adjustment_percentage).toBeGreaterThanOrEqual(0);
      expect(['rising', 'falling', 'stable']).toContain(response.data.trend);
      expect(['increase', 'decrease', 'maintain']).toContain(response.data.action);
    });
  });
});