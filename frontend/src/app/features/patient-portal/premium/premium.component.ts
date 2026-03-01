import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../../core/services/api.service';
import { AuthService } from '../../../core/services/auth.service';

interface PremiumEstimate {
  plan_name: string;
  base_premium: number;
  age_adjustment: number;
  bmi_adjustment: number;
  smoker_adjustment: number;
  condition_adjustment: number;
  final_monthly_premium: number;
  deductible: number;
  max_coverage: number;
  copay_percentage: number;
}

interface EstimateForm {
  age: number | null;
  bmi: number | null;
  is_smoker: boolean;
  pre_existing_conditions: string;
}

@Component({
  selector: 'app-premium',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="premium-container">
      <!-- Estimator Form -->
      <section class="card form-section">
        <h2>Premium Estimator</h2>
        <p class="subtitle">Enter your details to compare insurance plan premiums tailored to your profile.</p>

        <form (ngSubmit)="estimatePremium()" class="estimate-form">
          <div class="form-row">
            <div class="form-group">
              <label for="age">Age</label>
              <input
                type="number"
                id="age"
                [(ngModel)]="form.age"
                name="age"
                min="1"
                max="120"
                placeholder="e.g. 35"
                required
              />
            </div>

            <div class="form-group">
              <label for="bmi">BMI</label>
              <input
                type="number"
                id="bmi"
                [(ngModel)]="form.bmi"
                name="bmi"
                min="10"
                max="60"
                step="0.1"
                placeholder="e.g. 24.5"
                required
              />
            </div>

            <div class="form-group checkbox-group">
              <label class="checkbox-label">
                <input
                  type="checkbox"
                  [(ngModel)]="form.is_smoker"
                  name="is_smoker"
                />
                <span>Smoker</span>
              </label>
            </div>
          </div>

          <div class="form-group">
            <label for="conditions">Pre-existing Conditions</label>
            <input
              type="text"
              id="conditions"
              [(ngModel)]="form.pre_existing_conditions"
              name="pre_existing_conditions"
              placeholder="e.g. diabetes, hypertension (comma-separated)"
            />
          </div>

          <div class="form-actions">
            <button
              type="submit"
              class="btn-estimate"
              [disabled]="isLoading || !form.age || !form.bmi"
            >
              {{ isLoading ? 'Estimating...' : 'Estimate Premium' }}
            </button>
          </div>

          <div *ngIf="errorMessage" class="alert alert-error">
            {{ errorMessage }}
          </div>
        </form>
      </section>

      <!-- Results Table -->
      <section class="card results-section" *ngIf="estimates.length > 0">
        <h2>Premium Comparison</h2>
        <p class="subtitle">
          Showing estimated monthly premiums for {{ estimates.length }} available plans.
          <span class="cheapest-note">The most affordable option is highlighted.</span>
        </p>

        <div class="table-wrapper">
          <table class="premium-table">
            <thead>
              <tr>
                <th>Plan Name</th>
                <th>Base Premium</th>
                <th>Age Adj.</th>
                <th>BMI Adj.</th>
                <th>Smoker Adj.</th>
                <th>Condition Adj.</th>
                <th>Final Monthly</th>
                <th>Deductible</th>
                <th>Max Coverage</th>
                <th>Copay %</th>
              </tr>
            </thead>
            <tbody>
              <tr
                *ngFor="let est of estimates; let i = index"
                [class.cheapest]="est.final_monthly_premium === cheapestPremium"
                [class.row-even]="i % 2 === 0"
                [class.row-odd]="i % 2 !== 0"
              >
                <td class="cell-plan">
                  {{ est.plan_name }}
                  <span *ngIf="est.final_monthly_premium === cheapestPremium" class="best-badge">Best Value</span>
                </td>
                <td>{{ est.base_premium | currency:'INR' }}</td>
                <td [class.adjustment-positive]="est.age_adjustment > 0" [class.adjustment-negative]="est.age_adjustment < 0">
                  {{ est.age_adjustment >= 0 ? '+' : '' }}{{ est.age_adjustment | currency:'INR' }}
                </td>
                <td [class.adjustment-positive]="est.bmi_adjustment > 0" [class.adjustment-negative]="est.bmi_adjustment < 0">
                  {{ est.bmi_adjustment >= 0 ? '+' : '' }}{{ est.bmi_adjustment | currency:'INR' }}
                </td>
                <td [class.adjustment-positive]="est.smoker_adjustment > 0" [class.adjustment-negative]="est.smoker_adjustment < 0">
                  {{ est.smoker_adjustment >= 0 ? '+' : '' }}{{ est.smoker_adjustment | currency:'INR' }}
                </td>
                <td [class.adjustment-positive]="est.condition_adjustment > 0" [class.adjustment-negative]="est.condition_adjustment < 0">
                  {{ est.condition_adjustment >= 0 ? '+' : '' }}{{ est.condition_adjustment | currency:'INR' }}
                </td>
                <td class="cell-final">{{ est.final_monthly_premium | currency:'INR' }}</td>
                <td>{{ est.deductible | currency:'INR' }}</td>
                <td>{{ est.max_coverage | currency:'INR':'symbol':'1.0-0' }}</td>
                <td>{{ est.copay_percentage }}%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  `,
  styles: [`
    .premium-container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 24px;
    }

    .card {
      background: #fff;
      border-radius: 10px;
      padding: 24px 28px;
      box-shadow: 0 1px 8px rgba(0, 0, 0, 0.07);
    }

    h2 {
      margin: 0 0 4px 0;
      font-size: 20px;
      font-weight: 600;
      color: #1e293b;
    }

    .subtitle {
      margin: 0 0 20px 0;
      font-size: 14px;
      color: #64748b;
      line-height: 1.5;
    }

    .cheapest-note {
      font-weight: 600;
      color: #059669;
    }

    /* Form */
    .estimate-form {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .form-row {
      display: flex;
      gap: 16px;
      align-items: flex-end;
      flex-wrap: wrap;
    }

    .form-group {
      display: flex;
      flex-direction: column;
      gap: 6px;
      flex: 1;
      min-width: 180px;

      label {
        font-size: 13px;
        font-weight: 600;
        color: #475569;
      }

      input[type="number"],
      input[type="text"] {
        padding: 10px 12px;
        border: 1px solid #d1d5db;
        border-radius: 6px;
        font-size: 14px;
        outline: none;
        transition: border-color 0.2s;

        &:focus {
          border-color: #3b82f6;
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
      }
    }

    .checkbox-group {
      justify-content: flex-end;
      min-width: 120px;
      flex: 0;
    }

    .checkbox-label {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      padding: 10px 0;

      input[type="checkbox"] {
        width: 18px;
        height: 18px;
        accent-color: #3b82f6;
        cursor: pointer;
      }

      span {
        font-size: 14px;
        font-weight: 500;
        color: #334155;
      }
    }

    .form-actions {
      display: flex;
      justify-content: flex-end;
    }

    .btn-estimate {
      padding: 10px 28px;
      background: #3b82f6;
      color: #fff;
      border: none;
      border-radius: 6px;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      transition: background 0.2s;

      &:hover:not(:disabled) {
        background: #2563eb;
      }

      &:disabled {
        background: #93c5fd;
        cursor: not-allowed;
      }
    }

    .alert-error {
      padding: 12px 16px;
      border-radius: 6px;
      font-size: 14px;
      font-weight: 500;
      background: #fef2f2;
      color: #991b1b;
      border: 1px solid #fecaca;
    }

    /* Table */
    .table-wrapper {
      overflow-x: auto;
    }

    .premium-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;

      th {
        text-align: left;
        padding: 12px 14px;
        background: #f8fafc;
        color: #475569;
        font-weight: 600;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        border-bottom: 2px solid #e2e8f0;
        white-space: nowrap;
      }

      td {
        padding: 12px 14px;
        border-bottom: 1px solid #f1f5f9;
        color: #334155;
        white-space: nowrap;
      }

      tbody tr:hover {
        background: #f0f9ff !important;
      }
    }

    .row-even {
      background: #fff;
    }

    .row-odd {
      background: #f8fafc;
    }

    .cheapest {
      background: #ecfdf5 !important;
      border-left: 3px solid #10b981;

      td {
        color: #065f46;
        font-weight: 500;
      }
    }

    .cell-plan {
      font-weight: 600;
      color: #1e293b;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .best-badge {
      display: inline-block;
      padding: 2px 8px;
      background: #10b981;
      color: #fff;
      border-radius: 10px;
      font-size: 10px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }

    .cell-final {
      font-weight: 700;
      font-size: 14px;
      color: #1e293b;
    }

    .adjustment-positive {
      color: #dc2626;
    }

    .adjustment-negative {
      color: #059669;
    }
  `]
})
export class PremiumComponent {
  form: EstimateForm = {
    age: null,
    bmi: null,
    is_smoker: false,
    pre_existing_conditions: ''
  };

  estimates: PremiumEstimate[] = [];
  cheapestPremium: number | null = null;
  isLoading = false;
  errorMessage = '';

  constructor(
    private apiService: ApiService,
    private authService: AuthService
  ) {}

  estimatePremium(): void {
    if (this.isLoading || !this.form.age || !this.form.bmi) return;

    this.isLoading = true;
    this.errorMessage = '';
    this.estimates = [];
    this.cheapestPremium = null;

    const payload = {
      age: this.form.age,
      bmi: this.form.bmi,
      is_smoker: this.form.is_smoker,
      pre_existing_conditions: this.form.pre_existing_conditions
        ? this.form.pre_existing_conditions.split(',').map((c) => c.trim()).filter((c) => c)
        : []
    };

    this.apiService.post<PremiumEstimate[]>('/premium/estimate', payload).subscribe({
      next: (estimates) => {
        this.estimates = estimates;
        if (estimates.length > 0) {
          this.cheapestPremium = Math.min(...estimates.map((e) => e.final_monthly_premium));
        }
        this.isLoading = false;
      },
      error: (err) => {
        this.errorMessage = err?.error?.detail || 'Failed to estimate premiums. Please try again.';
        this.isLoading = false;
        console.error('Premium estimation failed:', err);
      }
    });
  }
}
