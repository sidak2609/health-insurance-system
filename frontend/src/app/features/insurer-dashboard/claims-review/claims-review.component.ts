import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../../core/services/api.service';

@Component({
  selector: 'app-claims-review',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="claims-review-container">
      <h1>Claims Review</h1>

      <!-- Global feedback banners -->
      <div class="banner success-banner" *ngIf="globalSuccess">
        {{ globalSuccess }}
        <button class="close-banner" (click)="globalSuccess=''">×</button>
      </div>
      <div class="banner error-banner" *ngIf="globalError">
        {{ globalError }}
        <button class="close-banner" (click)="globalError=''">×</button>
      </div>

      <!-- Filter Buttons -->
      <div class="filter-bar">
        <button
          *ngFor="let f of filters"
          class="filter-btn"
          [class.active]="activeFilter === f.value"
          (click)="filterClaims(f.value)">
          {{ f.label }}
        </button>
      </div>

      <!-- Claims Table -->
      <div class="table-wrapper">
        <table class="claims-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Patient Name</th>
              <th>Policy</th>
              <th>Type</th>
              <th>Amount Claimed</th>
              <th>Risk Score</th>
              <th>Risk Level</th>
              <th>Status</th>
              <th>Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr *ngFor="let claim of claims" [class.selected]="selectedClaim?.id === claim.id">
              <td>{{ claim.id }}</td>
              <td>{{ claim.patient_name }}</td>
              <td>{{ claim.policy_name || claim.policy }}</td>
              <td>{{ claim.claim_type || claim.type }}</td>
              <td>{{ claim.amount_claimed | currency:'INR' }}</td>
              <td>
                <div class="risk-bar-container">
                  <div
                    class="risk-bar"
                    [style.width.%]="(claim.risk_score || 0) * 100"
                    [class.risk-low]="(claim.risk_score || 0) < 0.3"
                    [class.risk-medium]="(claim.risk_score || 0) >= 0.3 && (claim.risk_score || 0) <= 0.6"
                    [class.risk-high]="(claim.risk_score || 0) > 0.6">
                  </div>
                  <span class="risk-score-text">{{ (claim.risk_score || 0) | number:'1.2-2' }}</span>
                </div>
              </td>
              <td>
                <span class="risk-badge"
                  [class.risk-level-low]="claim.risk_level === 'low'"
                  [class.risk-level-medium]="claim.risk_level === 'medium'"
                  [class.risk-level-high]="claim.risk_level === 'high'">
                  {{ claim.risk_level || 'N/A' }}
                </span>
              </td>
              <td>
                <span class="status-badge" [ngClass]="'status-' + (claim.status || '').toLowerCase().replace(' ', '-')">
                  {{ claim.status }}
                </span>
              </td>
              <td>{{ claim.created_at | date:'mediumDate' }}</td>
              <td>
                <button class="review-btn" (click)="openReview(claim)"
                  [disabled]="claim.status === 'approved' || claim.status === 'rejected'">
                  Review
                </button>
              </td>
            </tr>
            <tr *ngIf="claims.length === 0">
              <td colspan="10" class="empty-row">No claims found.</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Review Panel -->
      <div class="review-panel" *ngIf="selectedClaim">
        <div class="review-panel-header">
          <h2>Review Claim #{{ selectedClaim.id }}</h2>
          <button class="close-btn" (click)="closeReview()">&times;</button>
        </div>

        <div class="review-details">
          <div class="detail-grid">
            <div class="detail-item">
              <span class="detail-label">Patient</span>
              <span class="detail-value">{{ selectedClaim.patient_name }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Policy</span>
              <span class="detail-value">{{ selectedClaim.policy_name || selectedClaim.policy }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Claim Type</span>
              <span class="detail-value">{{ selectedClaim.claim_type || selectedClaim.type }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Amount Claimed</span>
              <span class="detail-value">{{ selectedClaim.amount_claimed | currency:'INR' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Risk Score</span>
              <span class="detail-value">{{ (selectedClaim.risk_score || 0) | number:'1.2-2' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Risk Level</span>
              <span class="detail-value">{{ selectedClaim.risk_level || 'N/A' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Status</span>
              <span class="detail-value">{{ selectedClaim.status }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Date Submitted</span>
              <span class="detail-value">{{ selectedClaim.created_at | date:'medium' }}</span>
            </div>
          </div>

          <div class="detail-item full-width" *ngIf="selectedClaim.description">
            <span class="detail-label">Description</span>
            <span class="detail-value">{{ selectedClaim.description }}</span>
          </div>

          <div class="detail-item full-width" *ngIf="selectedClaim.rejection_reason">
            <span class="detail-label">Previous Rejection Reason</span>
            <span class="detail-value">{{ selectedClaim.rejection_reason }}</span>
          </div>
        </div>

        <div class="review-actions">
          <!-- Approve Section -->
          <div class="action-section approve-section">
            <h4>Approve Claim</h4>
            <div class="form-group">
              <label for="amountApproved">Amount Approved</label>
              <input
                type="number"
                id="amountApproved"
                [(ngModel)]="amountApproved"
                [placeholder]="selectedClaim.amount_claimed"
                step="0.01"
                min="0" />
            </div>
            <button class="action-btn approve-btn" (click)="approveClaim()" [disabled]="isSubmitting">
              {{ isSubmitting ? 'Processing...' : 'Approve' }}
            </button>
          </div>

          <!-- Reject Section -->
          <div class="action-section reject-section">
            <h4>Reject Claim</h4>
            <div class="form-group">
              <label for="rejectionReason">Rejection Reason</label>
              <textarea
                id="rejectionReason"
                [(ngModel)]="rejectionReason"
                rows="3"
                placeholder="Enter reason for rejection...">
              </textarea>
            </div>
            <button class="action-btn reject-btn" (click)="rejectClaim()" [disabled]="isSubmitting || !rejectionReason.trim()">
              {{ isSubmitting ? 'Processing...' : 'Reject' }}
            </button>
          </div>
        </div>

        <div class="review-message success-msg" *ngIf="reviewSuccess">{{ reviewSuccess }}</div>
        <div class="review-message error-msg" *ngIf="reviewError">{{ reviewError }}</div>
      </div>
    </div>

    <div class="loading" *ngIf="isLoading">Loading claims...</div>
    <div class="error" *ngIf="loadError">{{ loadError }}</div>
  `,
  styles: [`
    .claims-review-container {
      padding: 24px;
      max-width: 1400px;
      margin: 0 auto;
    }

    h1 {
      color: #1565C0;
      margin-bottom: 24px;
      font-size: 28px;
      font-weight: 600;
    }

    .filter-bar {
      display: flex;
      gap: 8px;
      margin-bottom: 24px;
      flex-wrap: wrap;
    }

    .filter-btn {
      padding: 8px 20px;
      border: 2px solid #1565C0;
      background: #fff;
      color: #1565C0;
      border-radius: 24px;
      cursor: pointer;
      font-size: 14px;
      font-weight: 500;
      transition: all 0.2s;
    }

    .filter-btn:hover {
      background: #e3f2fd;
    }

    .filter-btn.active {
      background: #1565C0;
      color: #fff;
    }

    .table-wrapper {
      overflow-x: auto;
      background: #fff;
      border-radius: 12px;
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    }

    .claims-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }

    .claims-table thead th {
      background: #f5f7fa;
      padding: 14px 12px;
      text-align: left;
      font-weight: 600;
      color: #555;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      white-space: nowrap;
    }

    .claims-table tbody td {
      padding: 12px;
      border-bottom: 1px solid #f0f0f0;
      color: #333;
    }

    .claims-table tbody tr:hover {
      background: #fafbfc;
    }

    .claims-table tbody tr.selected {
      background: #e3f2fd;
    }

    .empty-row {
      text-align: center;
      color: #888;
      padding: 40px 12px !important;
    }

    .risk-bar-container {
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .risk-bar {
      height: 8px;
      border-radius: 4px;
      min-width: 4px;
      max-width: 80px;
    }

    .risk-bar.risk-low { background: #43A047; }
    .risk-bar.risk-medium { background: #FFA726; }
    .risk-bar.risk-high { background: #E53935; }

    .risk-score-text {
      font-size: 12px;
      color: #666;
      font-weight: 500;
    }

    .risk-badge {
      padding: 4px 10px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 600;
      text-transform: capitalize;
    }

    .risk-level-low { background: #e8f5e9; color: #2e7d32; }
    .risk-level-medium { background: #fff3e0; color: #ef6c00; }
    .risk-level-high { background: #ffebee; color: #c62828; }

    .status-badge {
      padding: 4px 10px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 600;
      text-transform: capitalize;
    }

    .status-pending { background: #fff3e0; color: #ef6c00; }
    .status-under-review { background: #e3f2fd; color: #1565C0; }
    .status-approved { background: #e8f5e9; color: #2e7d32; }
    .status-rejected { background: #ffebee; color: #c62828; }

    .review-btn {
      padding: 6px 16px;
      background: #1565C0;
      color: #fff;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      font-size: 13px;
      font-weight: 500;
      transition: background 0.2s;
    }

    .review-btn:hover:not(:disabled) { background: #0d47a1; }
    .review-btn:disabled { opacity: 0.5; cursor: not-allowed; }

    .review-panel {
      margin-top: 24px;
      background: #fff;
      border-radius: 12px;
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
      border: 2px solid #1565C0;
      padding: 24px;
    }

    .review-panel-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
    }

    .review-panel-header h2 {
      color: #1565C0;
      font-size: 22px;
      margin: 0;
    }

    .close-btn {
      background: none;
      border: none;
      font-size: 28px;
      color: #999;
      cursor: pointer;
      line-height: 1;
      padding: 0 4px;
    }

    .close-btn:hover { color: #333; }

    .review-details {
      margin-bottom: 24px;
    }

    .detail-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
      margin-bottom: 16px;
    }

    .detail-item {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .detail-item.full-width {
      margin-bottom: 12px;
    }

    .detail-label {
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: #888;
      font-weight: 500;
    }

    .detail-value {
      font-size: 15px;
      color: #333;
      font-weight: 500;
    }

    .review-actions {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
    }

    .action-section {
      padding: 20px;
      border-radius: 8px;
    }

    .approve-section {
      background: #f1f8e9;
      border: 1px solid #c5e1a5;
    }

    .reject-section {
      background: #fce4ec;
      border: 1px solid #ef9a9a;
    }

    .action-section h4 {
      margin: 0 0 12px 0;
      font-size: 16px;
    }

    .approve-section h4 { color: #2e7d32; }
    .reject-section h4 { color: #c62828; }

    .form-group {
      margin-bottom: 12px;
    }

    .form-group label {
      display: block;
      font-size: 13px;
      color: #555;
      margin-bottom: 6px;
      font-weight: 500;
    }

    .form-group input,
    .form-group textarea {
      width: 100%;
      padding: 10px 12px;
      border: 1px solid #ccc;
      border-radius: 6px;
      font-size: 14px;
      box-sizing: border-box;
      transition: border-color 0.2s;
    }

    .form-group input:focus,
    .form-group textarea:focus {
      outline: none;
      border-color: #1565C0;
    }

    .action-btn {
      padding: 10px 24px;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      font-size: 14px;
      font-weight: 600;
      color: #fff;
      transition: opacity 0.2s;
    }

    .action-btn:disabled { opacity: 0.5; cursor: not-allowed; }
    .approve-btn { background: #43A047; }
    .approve-btn:hover:not(:disabled) { background: #2e7d32; }
    .reject-btn { background: #E53935; }
    .reject-btn:hover:not(:disabled) { background: #c62828; }

    .review-message {
      margin-top: 16px;
      padding: 12px 16px;
      border-radius: 6px;
      font-size: 14px;
      font-weight: 500;
    }

    .success-msg { background: #e8f5e9; color: #2e7d32; }
    .error-msg { background: #ffebee; color: #c62828; }

    .banner {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 16px;
      border-radius: 8px;
      font-size: 14px;
      font-weight: 500;
      margin-bottom: 16px;
    }

    .success-banner { background: #e8f5e9; color: #2e7d32; border: 1px solid #a5d6a7; }
    .error-banner { background: #ffebee; color: #c62828; border: 1px solid #ef9a9a; }

    .close-banner {
      background: none;
      border: none;
      font-size: 20px;
      cursor: pointer;
      color: inherit;
      line-height: 1;
      padding: 0 4px;
      opacity: 0.7;
    }

    .close-banner:hover { opacity: 1; }

    .loading {
      text-align: center;
      padding: 60px;
      font-size: 16px;
      color: #888;
    }

    .error {
      text-align: center;
      padding: 60px;
      font-size: 16px;
      color: #E53935;
    }

    @media (max-width: 900px) {
      .detail-grid {
        grid-template-columns: repeat(2, 1fr);
      }
      .review-actions {
        grid-template-columns: 1fr;
      }
    }
  `]
})
export class ClaimsReviewComponent implements OnInit {
  claims: any[] = [];
  selectedClaim: any = null;
  activeFilter: string = '';
  isLoading: boolean = false;
  loadError: string = '';
  isSubmitting: boolean = false;
  reviewSuccess: string = '';
  reviewError: string = '';
  globalSuccess: string = '';
  globalError: string = '';

  amountApproved: number = 0;
  rejectionReason: string = '';

  filters = [
    { label: 'All', value: '' },
    { label: 'Pending', value: 'pending' },
    { label: 'Under Review', value: 'under_review' },
    { label: 'Approved', value: 'approved' },
    { label: 'Rejected', value: 'rejected' }
  ];

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.loadClaims();
  }

  loadClaims(): void {
    this.isLoading = true;
    this.loadError = '';

    let url = '/claims';
    if (this.activeFilter) {
      url += `?status=${this.activeFilter}`;
    }

    this.api.get(url).subscribe({
      next: (data: any) => {
        this.claims = Array.isArray(data) ? data : data.claims || [];
        this.isLoading = false;
      },
      error: (err) => {
        this.loadError = 'Failed to load claims.';
        this.isLoading = false;
        console.error(err);
      }
    });
  }

  filterClaims(status: string): void {
    this.activeFilter = status;
    this.closeReview();
    this.loadClaims();
  }

  openReview(claim: any): void {
    this.selectedClaim = claim;
    this.amountApproved = claim.amount_claimed;
    this.rejectionReason = '';
    this.reviewSuccess = '';
    this.reviewError = '';
  }

  closeReview(): void {
    this.selectedClaim = null;
    this.reviewSuccess = '';
    this.reviewError = '';
  }

  approveClaim(): void {
    if (!this.selectedClaim) return;

    this.isSubmitting = true;
    this.reviewSuccess = '';
    this.reviewError = '';

    const payload = {
      status: 'approved',
      amount_approved: this.amountApproved || this.selectedClaim.amount_claimed
    };

    this.api.put(`/claims/${this.selectedClaim.id}/review`, payload).subscribe({
      next: () => {
        this.isSubmitting = false;
        this.globalSuccess = 'Claim approved successfully.';
        this.loadClaims();
        this.closeReview();
      },
      error: (err) => {
        this.reviewError = `Failed to approve claim. ${err?.error?.detail || err?.status || 'Please try again.'}`;
        this.isSubmitting = false;
        console.error(err);
      }
    });
  }

  rejectClaim(): void {
    if (!this.selectedClaim) return;

    this.isSubmitting = true;
    this.reviewSuccess = '';
    this.reviewError = '';

    const payload = {
      status: 'rejected',
      rejection_reason: this.rejectionReason
    };

    this.api.put(`/claims/${this.selectedClaim.id}/review`, payload).subscribe({
      next: () => {
        this.isSubmitting = false;
        this.globalSuccess = 'Claim rejected successfully.';
        this.loadClaims();
        this.closeReview();
      },
      error: (err) => {
        this.reviewError = `Failed to reject claim. ${err?.error?.detail || err?.status || 'Please try again.'}`;
        this.isSubmitting = false;
        console.error(err);
      }
    });
  }
}
