import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../../core/services/api.service';

@Component({
  selector: 'app-policy-management',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="policy-management-container">
      <h1>Policy Management</h1>

      <!-- Policy Form -->
      <div class="form-card">
        <h2>{{ isEditing ? 'Edit Policy' : 'Create New Policy' }}</h2>

        <form (ngSubmit)="submitForm()" #policyForm="ngForm">
          <div class="form-grid">
            <div class="form-group">
              <label for="name">Policy Name *</label>
              <input type="text" id="name" [(ngModel)]="form.name" name="name" required />
            </div>

            <div class="form-group">
              <label for="plan_type">Plan Type *</label>
              <select id="plan_type" [(ngModel)]="form.plan_type" name="plan_type" required>
                <option value="">Select Plan Type</option>
                <option value="basic">Basic</option>
                <option value="standard">Standard</option>
                <option value="premium">Premium</option>
                <option value="custom">Custom</option>
              </select>
            </div>

            <div class="form-group">
              <label for="monthly_premium_base">Monthly Premium Base *</label>
              <input type="number" id="monthly_premium_base" [(ngModel)]="form.monthly_premium_base"
                name="monthly_premium_base" step="0.01" min="0" required />
            </div>

            <div class="form-group">
              <label for="annual_deductible">Annual Deductible *</label>
              <input type="number" id="annual_deductible" [(ngModel)]="form.annual_deductible"
                name="annual_deductible" step="0.01" min="0" required />
            </div>

            <div class="form-group">
              <label for="max_coverage_limit">Max Coverage Limit *</label>
              <input type="number" id="max_coverage_limit" [(ngModel)]="form.max_coverage_limit"
                name="max_coverage_limit" step="0.01" min="0" required />
            </div>

            <div class="form-group">
              <label for="copay_percentage">Copay Percentage (%)</label>
              <input type="number" id="copay_percentage" [(ngModel)]="form.copay_percentage"
                name="copay_percentage" step="0.1" min="0" max="100" />
            </div>

            <div class="form-group">
              <label for="age_min">Minimum Age</label>
              <input type="number" id="age_min" [(ngModel)]="form.age_min"
                name="age_min" min="0" max="120" />
            </div>

            <div class="form-group">
              <label for="age_max">Maximum Age</label>
              <input type="number" id="age_max" [(ngModel)]="form.age_max"
                name="age_max" min="0" max="120" />
            </div>

            <div class="form-group">
              <label for="smoker_surcharge_pct">Smoker Surcharge (%)</label>
              <input type="number" id="smoker_surcharge_pct" [(ngModel)]="form.smoker_surcharge_pct"
                name="smoker_surcharge_pct" step="0.1" min="0" />
            </div>

            <div class="form-group">
              <label for="bmi_surcharge_pct">BMI Surcharge (%)</label>
              <input type="number" id="bmi_surcharge_pct" [(ngModel)]="form.bmi_surcharge_pct"
                name="bmi_surcharge_pct" step="0.1" min="0" />
            </div>

            <div class="form-group">
              <label for="pre_existing_waiting_months">Pre-existing Waiting (months)</label>
              <input type="number" id="pre_existing_waiting_months" [(ngModel)]="form.pre_existing_waiting_months"
                name="pre_existing_waiting_months" min="0" />
            </div>
          </div>

          <!-- Coverage Details -->
          <div class="list-builder">
            <label>Coverage Details</label>
            <div class="list-input-row">
              <input type="text" [(ngModel)]="newCoverage" name="newCoverage"
                placeholder="Enter coverage detail" (keyup.enter)="addCoverage()" />
              <button type="button" class="add-btn" (click)="addCoverage()" [disabled]="!newCoverage.trim()">
                Add
              </button>
            </div>
            <ul class="tag-list" *ngIf="form.coverage_details.length > 0">
              <li *ngFor="let item of form.coverage_details; let i = index" class="tag-item">
                <span>{{ item }}</span>
                <button type="button" class="remove-tag" (click)="removeCoverage(i)">&times;</button>
              </li>
            </ul>
          </div>

          <!-- Exclusions -->
          <div class="list-builder">
            <label>Exclusions</label>
            <div class="list-input-row">
              <input type="text" [(ngModel)]="newExclusion" name="newExclusion"
                placeholder="Enter exclusion" (keyup.enter)="addExclusion()" />
              <button type="button" class="add-btn" (click)="addExclusion()" [disabled]="!newExclusion.trim()">
                Add
              </button>
            </div>
            <ul class="tag-list" *ngIf="form.exclusions.length > 0">
              <li *ngFor="let item of form.exclusions; let i = index" class="tag-item">
                <span>{{ item }}</span>
                <button type="button" class="remove-tag" (click)="removeExclusion(i)">&times;</button>
              </li>
            </ul>
          </div>

          <div class="form-actions">
            <button type="submit" class="submit-btn" [disabled]="isSubmitting">
              {{ isSubmitting ? 'Saving...' : (isEditing ? 'Update Policy' : 'Create Policy') }}
            </button>
            <button type="button" class="cancel-btn" *ngIf="isEditing" (click)="resetForm()">
              Cancel
            </button>
          </div>

          <div class="form-message success-msg" *ngIf="formSuccess">{{ formSuccess }}</div>
          <div class="form-message error-msg" *ngIf="formError">{{ formError }}</div>
        </form>
      </div>

      <!-- Existing Policies Table -->
      <div class="table-card">
        <h2>Existing Policies</h2>

        <div class="table-wrapper">
          <table class="policies-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Type</th>
                <th>Premium</th>
                <th>Deductible</th>
                <th>Max Coverage</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let policy of policies">
                <td>{{ policy.name }}</td>
                <td>
                  <span class="type-badge" [ngClass]="'type-' + policy.plan_type">
                    {{ policy.plan_type }}
                  </span>
                </td>
                <td>{{ policy.monthly_premium_base | currency:'INR' }}/mo</td>
                <td>{{ policy.annual_deductible | currency:'INR' }}</td>
                <td>{{ policy.max_coverage_limit | currency:'INR' }}</td>
                <td class="action-cell">
                  <button class="edit-btn" (click)="editPolicy(policy)">Edit</button>
                  <button class="delete-btn" (click)="deletePolicy(policy)">Delete</button>
                </td>
              </tr>
              <tr *ngIf="policies.length === 0">
                <td colspan="6" class="empty-row">No policies found.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div class="loading" *ngIf="isLoading">Loading policies...</div>
  `,
  styles: [`
    .policy-management-container {
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

    .form-card, .table-card {
      background: #fff;
      border-radius: 12px;
      padding: 24px;
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
      margin-bottom: 24px;
    }

    .form-card h2, .table-card h2 {
      color: #333;
      font-size: 20px;
      margin: 0 0 20px 0;
      font-weight: 600;
    }

    .form-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;
      margin-bottom: 24px;
    }

    .form-group {
      display: flex;
      flex-direction: column;
    }

    .form-group label {
      font-size: 13px;
      color: #555;
      margin-bottom: 6px;
      font-weight: 500;
    }

    .form-group input,
    .form-group select {
      padding: 10px 12px;
      border: 1px solid #ddd;
      border-radius: 6px;
      font-size: 14px;
      transition: border-color 0.2s;
    }

    .form-group input:focus,
    .form-group select:focus {
      outline: none;
      border-color: #1565C0;
      box-shadow: 0 0 0 2px rgba(21, 101, 192, 0.1);
    }

    .list-builder {
      margin-bottom: 20px;
    }

    .list-builder > label {
      display: block;
      font-size: 14px;
      color: #555;
      margin-bottom: 8px;
      font-weight: 600;
    }

    .list-input-row {
      display: flex;
      gap: 8px;
      margin-bottom: 8px;
    }

    .list-input-row input {
      flex: 1;
      padding: 10px 12px;
      border: 1px solid #ddd;
      border-radius: 6px;
      font-size: 14px;
    }

    .list-input-row input:focus {
      outline: none;
      border-color: #1565C0;
    }

    .add-btn {
      padding: 10px 20px;
      background: #00897B;
      color: #fff;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      font-size: 14px;
      font-weight: 500;
      transition: background 0.2s;
    }

    .add-btn:hover:not(:disabled) { background: #00695c; }
    .add-btn:disabled { opacity: 0.5; cursor: not-allowed; }

    .tag-list {
      list-style: none;
      padding: 0;
      margin: 0;
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }

    .tag-item {
      display: flex;
      align-items: center;
      gap: 6px;
      background: #e3f2fd;
      color: #1565C0;
      padding: 6px 12px;
      border-radius: 20px;
      font-size: 13px;
      font-weight: 500;
    }

    .remove-tag {
      background: none;
      border: none;
      color: #1565C0;
      font-size: 18px;
      cursor: pointer;
      line-height: 1;
      padding: 0;
      opacity: 0.6;
    }

    .remove-tag:hover { opacity: 1; }

    .form-actions {
      display: flex;
      gap: 12px;
      margin-top: 8px;
    }

    .submit-btn {
      padding: 12px 32px;
      background: #1565C0;
      color: #fff;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      font-size: 15px;
      font-weight: 600;
      transition: background 0.2s;
    }

    .submit-btn:hover:not(:disabled) { background: #0d47a1; }
    .submit-btn:disabled { opacity: 0.5; cursor: not-allowed; }

    .cancel-btn {
      padding: 12px 24px;
      background: #f5f5f5;
      color: #666;
      border: 1px solid #ddd;
      border-radius: 6px;
      cursor: pointer;
      font-size: 15px;
      font-weight: 500;
      transition: background 0.2s;
    }

    .cancel-btn:hover { background: #eee; }

    .form-message {
      margin-top: 16px;
      padding: 12px 16px;
      border-radius: 6px;
      font-size: 14px;
      font-weight: 500;
    }

    .success-msg { background: #e8f5e9; color: #2e7d32; }
    .error-msg { background: #ffebee; color: #c62828; }

    .table-wrapper {
      overflow-x: auto;
    }

    .policies-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }

    .policies-table thead th {
      background: #f5f7fa;
      padding: 14px 12px;
      text-align: left;
      font-weight: 600;
      color: #555;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .policies-table tbody td {
      padding: 12px;
      border-bottom: 1px solid #f0f0f0;
      color: #333;
    }

    .policies-table tbody tr:hover {
      background: #fafbfc;
    }

    .empty-row {
      text-align: center;
      color: #888;
      padding: 40px 12px !important;
    }

    .type-badge {
      padding: 4px 10px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 600;
      text-transform: capitalize;
    }

    .type-basic { background: #e3f2fd; color: #1565C0; }
    .type-standard { background: #e8f5e9; color: #2e7d32; }
    .type-premium { background: #fff3e0; color: #ef6c00; }
    .type-custom { background: #f3e5f5; color: #7b1fa2; }

    .action-cell {
      white-space: nowrap;
    }

    .edit-btn {
      padding: 6px 14px;
      background: #1565C0;
      color: #fff;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      font-size: 13px;
      font-weight: 500;
      margin-right: 8px;
      transition: background 0.2s;
    }

    .edit-btn:hover { background: #0d47a1; }

    .delete-btn {
      padding: 6px 14px;
      background: #E53935;
      color: #fff;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      font-size: 13px;
      font-weight: 500;
      transition: background 0.2s;
    }

    .delete-btn:hover { background: #c62828; }

    .loading {
      text-align: center;
      padding: 60px;
      font-size: 16px;
      color: #888;
    }

    @media (max-width: 1024px) {
      .form-grid {
        grid-template-columns: repeat(2, 1fr);
      }
    }

    @media (max-width: 600px) {
      .form-grid {
        grid-template-columns: 1fr;
      }
    }
  `]
})
export class PolicyManagementComponent implements OnInit {
  policies: any[] = [];
  isLoading: boolean = false;
  isSubmitting: boolean = false;
  isEditing: boolean = false;
  editingId: number | null = null;
  formSuccess: string = '';
  formError: string = '';

  newCoverage: string = '';
  newExclusion: string = '';

  form: any = {
    name: '',
    plan_type: '',
    monthly_premium_base: null,
    annual_deductible: null,
    max_coverage_limit: null,
    copay_percentage: null,
    age_min: null,
    age_max: null,
    smoker_surcharge_pct: null,
    bmi_surcharge_pct: null,
    pre_existing_waiting_months: null,
    coverage_details: [] as string[],
    exclusions: [] as string[]
  };

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.loadPolicies();
  }

  loadPolicies(): void {
    this.isLoading = true;
    this.api.get('/policies').subscribe({
      next: (data: any) => {
        this.policies = Array.isArray(data) ? data : data.policies || [];
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Failed to load policies', err);
        this.isLoading = false;
      }
    });
  }

  addCoverage(): void {
    const value = this.newCoverage.trim();
    if (value) {
      this.form.coverage_details.push(value);
      this.newCoverage = '';
    }
  }

  removeCoverage(index: number): void {
    this.form.coverage_details.splice(index, 1);
  }

  addExclusion(): void {
    const value = this.newExclusion.trim();
    if (value) {
      this.form.exclusions.push(value);
      this.newExclusion = '';
    }
  }

  removeExclusion(index: number): void {
    this.form.exclusions.splice(index, 1);
  }

  submitForm(): void {
    this.isSubmitting = true;
    this.formSuccess = '';
    this.formError = '';

    const payload = { ...this.form };

    if (this.isEditing && this.editingId !== null) {
      this.api.put(`/policies/${this.editingId}`, payload).subscribe({
        next: () => {
          this.formSuccess = 'Policy updated successfully.';
          this.isSubmitting = false;
          this.resetForm();
          this.loadPolicies();
        },
        error: (err) => {
          this.formError = 'Failed to update policy. Please try again.';
          this.isSubmitting = false;
          console.error(err);
        }
      });
    } else {
      this.api.post('/policies', payload).subscribe({
        next: () => {
          this.formSuccess = 'Policy created successfully.';
          this.isSubmitting = false;
          this.resetForm();
          this.loadPolicies();
        },
        error: (err) => {
          this.formError = 'Failed to create policy. Please try again.';
          this.isSubmitting = false;
          console.error(err);
        }
      });
    }
  }

  editPolicy(policy: any): void {
    this.isEditing = true;
    this.editingId = policy.id;
    this.formSuccess = '';
    this.formError = '';

    this.form = {
      name: policy.name || '',
      plan_type: policy.plan_type || '',
      monthly_premium_base: policy.monthly_premium_base,
      annual_deductible: policy.annual_deductible,
      max_coverage_limit: policy.max_coverage_limit,
      copay_percentage: policy.copay_percentage,
      age_min: policy.age_min,
      age_max: policy.age_max,
      smoker_surcharge_pct: policy.smoker_surcharge_pct,
      bmi_surcharge_pct: policy.bmi_surcharge_pct,
      pre_existing_waiting_months: policy.pre_existing_waiting_months,
      coverage_details: Array.isArray(policy.coverage_details) ? [...policy.coverage_details] : [],
      exclusions: Array.isArray(policy.exclusions) ? [...policy.exclusions] : []
    };

    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  deletePolicy(policy: any): void {
    if (!confirm(`Are you sure you want to delete the policy "${policy.name}"? This action cannot be undone.`)) {
      return;
    }

    this.api.delete(`/policies/${policy.id}`).subscribe({
      next: () => {
        this.loadPolicies();
      },
      error: (err) => {
        console.error('Failed to delete policy', err);
        alert('Failed to delete policy. Please try again.');
      }
    });
  }

  resetForm(): void {
    this.isEditing = false;
    this.editingId = null;
    this.newCoverage = '';
    this.newExclusion = '';
    this.form = {
      name: '',
      plan_type: '',
      monthly_premium_base: null,
      annual_deductible: null,
      max_coverage_limit: null,
      copay_percentage: null,
      age_min: null,
      age_max: null,
      smoker_surcharge_pct: null,
      bmi_surcharge_pct: null,
      pre_existing_waiting_months: null,
      coverage_details: [],
      exclusions: []
    };
  }
}
