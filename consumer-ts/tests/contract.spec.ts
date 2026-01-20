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
  it('should return healthy status', async () => {
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
          status: 'healthy',
          service: 'RiskAlgoService',
          version: '1.0.0',
        }),
      });

    await provider.executeTest(async (mockServer) => {
      const response = await axios.get(`${mockServer.url}/health`);
      expect(response.status).toBe(200);
      expect(response.data).toEqual(expect.objectContaining({
        status: 'healthy',
        service: 'RiskAlgoService',
        version: '1.0.0',
      }));
    });
  });

  it('should calculate bolus dosage', async () => {
    await provider
      .given('a patient with valid data')
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
          warnings: eachLike(string('warning-1'), 0),
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
      expect(response.data).toEqual(expect.objectContaining({
        patient_id: 'patient-123',
        recommended_bolus_units: expect.any(Number),
        correction_units: expect.any(Number),
        carb_coverage_units: expect.any(Number),
        risk_level: expect.any(String),
        warnings: expect.any(Array),
      }));
    });
  });

  it('should calculate basal rate adjustment', async () => {
    await provider
      .given('a patient with valid glucose readings')
      .uponReceiving('a basal rate adjustment request')
      .withRequest({
        method: 'POST',
        path: '/calculate/basal-adjustment',
        headers: { 'Content-Type': 'application/json' },
        body: like({
          patient_id: string('patient-123'),
          glucose_readings: eachLike(number(100), 2),
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
        glucose_readings: [100, 120],
        current_basal_rate: 10,
      });
      expect(response.status).toBe(200);
      expect(response.data).toEqual(expect.objectContaining({
        patient_id: 'patient-123',
        adjusted_basal_rate: expect.any(Number),
        adjustment_percentage: expect.any(Number),
        trend: expect.any(String),
        action: expect.any(String),
      }));
    });
  });
});