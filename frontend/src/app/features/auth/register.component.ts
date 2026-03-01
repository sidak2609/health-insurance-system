import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, Router } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  template: `
    <div class="register-wrapper">
      <div class="register-card">
        <h1 class="title">HealthInsure</h1>
        <p class="subtitle">Create your account</p>

        <form (ngSubmit)="onSubmit()" #registerForm="ngForm">
          <div class="form-group">
            <label for="full_name">Full Name</label>
            <input
              id="full_name"
              type="text"
              [(ngModel)]="full_name"
              name="full_name"
              placeholder="Enter your full name"
              required
            />
          </div>

          <div class="form-group">
            <label for="email">Email</label>
            <input
              id="email"
              type="email"
              [(ngModel)]="email"
              name="email"
              placeholder="Enter your email"
              required
              autocomplete="email"
            />
          </div>

          <div class="form-group">
            <label for="password">Password</label>
            <input
              id="password"
              type="password"
              [(ngModel)]="password"
              name="password"
              placeholder="Create a password"
              required
              autocomplete="new-password"
            />
          </div>

          <div class="form-group">
            <label for="role">Role</label>
            <select
              id="role"
              [(ngModel)]="role"
              name="role"
              required
            >
              <option value="" disabled>Select a role</option>
              <option value="patient">Patient</option>
              <option value="insurer">Insurer</option>
            </select>
          </div>

          <!-- Patient-specific fields -->
          <ng-container *ngIf="role === 'patient'">
            <div class="form-row">
              <div class="form-group half">
                <label for="age">Age</label>
                <input
                  id="age"
                  type="number"
                  [(ngModel)]="age"
                  name="age"
                  placeholder="Age"
                  min="1"
                  max="150"
                />
              </div>

              <div class="form-group half">
                <label for="bmi">BMI</label>
                <input
                  id="bmi"
                  type="number"
                  [(ngModel)]="bmi"
                  name="bmi"
                  placeholder="BMI"
                  step="0.1"
                  min="1"
                />
              </div>
            </div>

            <div class="form-group checkbox-group">
              <label class="checkbox-label">
                <input
                  type="checkbox"
                  [(ngModel)]="is_smoker"
                  name="is_smoker"
                />
                <span>I am a smoker</span>
              </label>
            </div>

            <div class="form-group">
              <label for="pre_existing_conditions">Pre-existing Conditions</label>
              <input
                id="pre_existing_conditions"
                type="text"
                [(ngModel)]="pre_existing_conditions"
                name="pre_existing_conditions"
                placeholder="e.g. Diabetes, Hypertension (comma-separated)"
              />
            </div>
          </ng-container>

          <!-- Insurer-specific fields -->
          <ng-container *ngIf="role === 'insurer'">
            <div class="form-group">
              <label for="company_name">Company Name</label>
              <input
                id="company_name"
                type="text"
                [(ngModel)]="company_name"
                name="company_name"
                placeholder="Enter your company name"
                required
              />
            </div>
          </ng-container>

          <div class="error-message" *ngIf="errorMessage">
            {{ errorMessage }}
          </div>

          <button type="submit" class="submit-btn" [disabled]="isLoading">
            {{ isLoading ? 'Creating Account...' : 'Create Account' }}
          </button>
        </form>

        <p class="login-link">
          Already have an account? <a routerLink="/login">Sign in</a>
        </p>
      </div>
    </div>
  `,
  styles: [`
    .register-wrapper {
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      background-color: #f0f4f8;
      padding: 20px;
    }

    .register-card {
      background-color: #ffffff;
      border-radius: 8px;
      box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);
      padding: 40px;
      width: 100%;
      max-width: 480px;
    }

    .title {
      text-align: center;
      color: #1565C0;
      font-size: 28px;
      font-weight: 700;
      margin: 0 0 8px 0;
    }

    .subtitle {
      text-align: center;
      color: #666666;
      font-size: 15px;
      margin: 0 0 32px 0;
    }

    .form-group {
      margin-bottom: 20px;
    }

    .form-group label {
      display: block;
      font-size: 14px;
      font-weight: 600;
      color: #333333;
      margin-bottom: 6px;
    }

    .form-group input[type="text"],
    .form-group input[type="email"],
    .form-group input[type="password"],
    .form-group input[type="number"],
    .form-group select {
      width: 100%;
      padding: 10px 12px;
      font-size: 14px;
      border: 1px solid #d0d5dd;
      border-radius: 6px;
      outline: none;
      transition: border-color 0.2s;
      box-sizing: border-box;
      background-color: #ffffff;
    }

    .form-group input:focus,
    .form-group select:focus {
      border-color: #1565C0;
      box-shadow: 0 0 0 3px rgba(21, 101, 192, 0.12);
    }

    .form-group input::placeholder {
      color: #aaaaaa;
    }

    .form-row {
      display: flex;
      gap: 16px;
    }

    .form-group.half {
      flex: 1;
    }

    .checkbox-group {
      margin-bottom: 20px;
    }

    .checkbox-label {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 14px;
      font-weight: 500;
      color: #333333;
      cursor: pointer;
    }

    .checkbox-label input[type="checkbox"] {
      width: 16px;
      height: 16px;
      accent-color: #1565C0;
      cursor: pointer;
    }

    .error-message {
      background-color: #fef2f2;
      color: #dc2626;
      border: 1px solid #fecaca;
      border-radius: 6px;
      padding: 10px 14px;
      font-size: 13px;
      margin-bottom: 20px;
    }

    .submit-btn {
      width: 100%;
      padding: 12px;
      font-size: 15px;
      font-weight: 600;
      color: #ffffff;
      background-color: #1565C0;
      border: none;
      border-radius: 6px;
      cursor: pointer;
      transition: background-color 0.2s;
    }

    .submit-btn:hover:not(:disabled) {
      background-color: #0d47a1;
    }

    .submit-btn:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }

    .login-link {
      text-align: center;
      margin-top: 24px;
      font-size: 14px;
      color: #666666;
    }

    .login-link a {
      color: #1565C0;
      text-decoration: none;
      font-weight: 600;
    }

    .login-link a:hover {
      text-decoration: underline;
    }
  `]
})
export class RegisterComponent {
  full_name: string = '';
  email: string = '';
  password: string = '';
  role: string = '';
  age: number | null = null;
  bmi: number | null = null;
  is_smoker: boolean = false;
  pre_existing_conditions: string = '';
  company_name: string = '';
  errorMessage: string = '';
  isLoading: boolean = false;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  onSubmit(): void {
    this.errorMessage = '';
    this.isLoading = true;

    const payload: any = {
      full_name: this.full_name,
      email: this.email,
      password: this.password,
      role: this.role
    };

    if (this.role === 'patient') {
      payload.age = this.age;
      payload.bmi = this.bmi;
      payload.is_smoker = this.is_smoker;
      payload.pre_existing_conditions = this.pre_existing_conditions
        ? this.pre_existing_conditions.split(',').map((c: string) => c.trim()).filter((c: string) => c.length > 0)
        : [];
    }

    if (this.role === 'insurer') {
      payload.company_name = this.company_name;
    }

    this.authService.register(payload).subscribe({
      next: () => {
        this.isLoading = false;
        if (this.role === 'insurer') {
          this.router.navigate(['/dashboard']);
        } else {
          this.router.navigate(['/patient/chat']);
        }
      },
      error: (err) => {
        this.isLoading = false;
        this.errorMessage = err.error?.detail || err.error?.message || 'Registration failed. Please try again.';
      }
    });
  }
}
