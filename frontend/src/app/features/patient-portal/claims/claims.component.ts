import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../../core/services/api.service';
import { AuthService } from '../../../core/services/auth.service';

interface Policy {
  id: string;
  name: string;
}

interface Claim {
  id: string;
  claim_type: string;
  amount_claimed: number;
  status: 'pending' | 'approved' | 'rejected' | 'under_review';
  risk_level: 'low' | 'medium' | 'high';
  created_at: string;
}

interface ClaimForm {
  policy_id: string;
  claim_type: string;
  amount_claimed: number | null;
  description: string;
}

@Component({
  selector: 'app-claims',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="claims-container">
      <!-- Submit Claim Form -->
      <section class="card submit-section">
        <h2>Submit a Claim</h2>
        <form (ngSubmit)="submitClaim()" class="claim-form">
          <div class="form-row">
            <div class="form-group">
              <label for="policy">Policy</label>
              <select id="policy" [(ngModel)]="claimForm.policy_id" name="policy_id" required>
                <option value="" disabled>Select a policy</option>
                <option *ngFor="let policy of policies" [value]="policy.id">
                  {{ policy.name }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label for="claimType">Claim Type</label>
              <select id="claimType" [(ngModel)]="claimForm.claim_type" name="claim_type" required>
                <option value="" disabled>Select type</option>
                <option value="hospitalization">Hospitalization</option>
                <option value="outpatient">Outpatient</option>
                <option value="prescription">Prescription</option>
                <option value="dental">Dental</option>
                <option value="vision">Vision</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div class="form-group">
              <label for="amount">Amount Claimed (₹)</label>
              <input
                type="number"
                id="amount"
                [(ngModel)]="claimForm.amount_claimed"
                name="amount_claimed"
                min="0"
                step="0.01"
                placeholder="0.00"
                required
              />
            </div>
          </div>

          <div class="form-group">
            <label for="description">Description</label>
            <textarea
              id="description"
              [(ngModel)]="claimForm.description"
              name="description"
              rows="3"
              placeholder="Describe the claim details..."
              required
            ></textarea>
          </div>

          <div class="form-actions">
            <button
              type="submit"
              class="btn-submit"
              [disabled]="isSubmitting || !claimForm.policy_id || !claimForm.claim_type || !claimForm.amount_claimed || !claimForm.description"
            >
              {{ isSubmitting ? 'Submitting...' : 'Submit Claim' }}
            </button>
          </div>

          <div *ngIf="submitSuccess" class="alert alert-success">
            Claim submitted successfully!
          </div>
          <div *ngIf="submitError" class="alert alert-error">
            {{ submitError }}
          </div>
        </form>
      </section>

      <!-- Claims List -->
      <section class="card claims-list-section">
        <h2>Your Claims</h2>

        <div *ngIf="isLoadingClaims" class="loading-state">Loading claims...</div>

        <div *ngIf="!isLoadingClaims && claims.length === 0" class="empty-state">
          No claims found. Submit your first claim above.
        </div>

        <div class="table-wrapper" *ngIf="claims.length > 0">
          <table class="claims-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Type</th>
                <th>Amount</th>
                <th>Status</th>
                <th>Risk Level</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let claim of claims">
                <td class="cell-id">{{ claim.id }}</td>
                <td class="cell-type">{{ formatClaimType(claim.claim_type) }}</td>
                <td class="cell-amount">{{ claim.amount_claimed | currency:'INR' }}</td>
                <td>
                  <span class="badge" [ngClass]="getStatusClass(claim.status)">
                    {{ formatStatus(claim.status) }}
                  </span>
                </td>
                <td>
                  <span class="badge" [ngClass]="getRiskClass(claim.risk_level)">
                    {{ claim.risk_level | titlecase }}
                  </span>
                </td>
                <td class="cell-date">{{ claim.created_at | date:'mediumDate' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  `,
  styles: [`
    .claims-container {
      max-width: 1100px;
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
      margin: 0 0 20px 0;
      font-size: 20px;
      font-weight: 600;
      color: #1e293b;
    }

    /* Form */
    .claim-form {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .form-row {
      display: flex;
      gap: 16px;
      flex-wrap: wrap;
    }

    .form-group {
      display: flex;
      flex-direction: column;
      gap: 6px;
      flex: 1;
      min-width: 200px;

      label {
        font-size: 13px;
        font-weight: 600;
        color: #475569;
      }

      select,
      input,
      textarea {
        padding: 10px 12px;
        border: 1px solid #d1d5db;
        border-radius: 6px;
        font-size: 14px;
        outline: none;
        transition: border-color 0.2s;
        font-family: inherit;

        &:focus {
          border-color: #3b82f6;
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
      }

      textarea {
        resize: vertical;
      }
    }

    .form-actions {
      display: flex;
      justify-content: flex-end;
    }

    .btn-submit {
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

    /* Alerts */
    .alert {
      padding: 12px 16px;
      border-radius: 6px;
      font-size: 14px;
      font-weight: 500;
    }

    .alert-success {
      background: #dcfce7;
      color: #166534;
      border: 1px solid #bbf7d0;
    }

    .alert-error {
      background: #fef2f2;
      color: #991b1b;
      border: 1px solid #fecaca;
    }

    /* Table */
    .loading-state,
    .empty-state {
      text-align: center;
      padding: 32px;
      color: #64748b;
      font-size: 14px;
    }

    .table-wrapper {
      overflow-x: auto;
    }

    .claims-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;

      th {
        text-align: left;
        padding: 12px 16px;
        background: #f8fafc;
        color: #475569;
        font-weight: 600;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        border-bottom: 2px solid #e2e8f0;
      }

      td {
        padding: 12px 16px;
        border-bottom: 1px solid #f1f5f9;
        color: #334155;
      }

      tbody tr:hover {
        background: #f8fafc;
      }
    }

    .cell-id {
      font-family: 'SF Mono', 'Fira Code', monospace;
      font-size: 12px;
      color: #64748b;
      max-width: 120px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .cell-type {
      font-weight: 500;
    }

    .cell-amount {
      font-weight: 600;
      color: #1e293b;
    }

    .cell-date {
      color: #64748b;
      white-space: nowrap;
    }

    /* Badges */
    .badge {
      display: inline-block;
      padding: 4px 10px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 600;
      text-transform: capitalize;
    }

    .status-pending {
      background: #fef9c3;
      color: #a16207;
    }

    .status-approved {
      background: #dcfce7;
      color: #166534;
    }

    .status-rejected {
      background: #fef2f2;
      color: #991b1b;
    }

    .status-under_review {
      background: #dbeafe;
      color: #1e40af;
    }

    .risk-low {
      background: #dcfce7;
      color: #166534;
    }

    .risk-medium {
      background: #fff7ed;
      color: #c2410c;
    }

    .risk-high {
      background: #fef2f2;
      color: #991b1b;
    }
  `]
})
export class ClaimsComponent implements OnInit {
  policies: Policy[] = [];
  claims: Claim[] = [];
  isLoadingClaims = false;
  isSubmitting = false;
  submitSuccess = false;
  submitError = '';

  claimForm: ClaimForm = {
    policy_id: '',
    claim_type: '',
    amount_claimed: null,
    description: ''
  };

  constructor(
    private apiService: ApiService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.loadPolicies();
    this.loadClaims();
  }

  loadPolicies(): void {
    this.apiService.get<Policy[]>('/policies').subscribe({
      next: (policies) => {
        this.policies = policies;
      },
      error: (err) => {
        console.error('Failed to load policies:', err);
      }
    });
  }

  loadClaims(): void {
    this.isLoadingClaims = true;
    this.apiService.get<Claim[]>('/claims').subscribe({
      next: (claims) => {
        this.claims = claims;
        this.isLoadingClaims = false;
      },
      error: (err) => {
        console.error('Failed to load claims:', err);
        this.isLoadingClaims = false;
      }
    });
  }

  submitClaim(): void {
    if (this.isSubmitting) return;

    this.isSubmitting = true;
    this.submitSuccess = false;
    this.submitError = '';

    this.apiService.post('/claims', this.claimForm).subscribe({
      next: () => {
        this.isSubmitting = false;
        this.submitSuccess = true;
        this.claimForm = {
          policy_id: '',
          claim_type: '',
          amount_claimed: null,
          description: ''
        };
        this.loadClaims();

        setTimeout(() => {
          this.submitSuccess = false;
        }, 4000);
      },
      error: (err) => {
        this.isSubmitting = false;
        this.submitError = err?.error?.detail || 'Failed to submit claim. Please try again.';
        console.error('Failed to submit claim:', err);
      }
    });
  }

  formatClaimType(type: string): string {
    return type.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
  }

  formatStatus(status: string): string {
    return status.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
  }

  getStatusClass(status: string): string {
    return `status-${status}`;
  }

  getRiskClass(riskLevel: string): string {
    return `risk-${riskLevel}`;
  }
}
