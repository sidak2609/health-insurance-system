import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule, Router } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  template: `
    <div class="login-wrapper">
      <div class="login-card">
        <h1 class="title">HealthInsure</h1>
        <p class="subtitle">Sign in to your account</p>

        <form (ngSubmit)="onSubmit()" #loginForm="ngForm">
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
              placeholder="Enter your password"
              required
              autocomplete="current-password"
            />
          </div>

          <div class="error-message" *ngIf="errorMessage">
            {{ errorMessage }}
          </div>

          <button type="submit" class="submit-btn" [disabled]="isLoading">
            {{ isLoading ? 'Signing in...' : 'Sign In' }}
          </button>
        </form>

        <p class="register-link">
          Don't have an account? <a routerLink="/register">Register here</a>
        </p>
      </div>
    </div>
  `,
  styles: [`
    .login-wrapper {
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      background-color: #f0f4f8;
      padding: 20px;
    }

    .login-card {
      background-color: #ffffff;
      border-radius: 8px;
      box-shadow: 0 4px 24px rgba(0, 0, 0, 0.1);
      padding: 40px;
      width: 100%;
      max-width: 420px;
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

    .form-group input {
      width: 100%;
      padding: 10px 12px;
      font-size: 14px;
      border: 1px solid #d0d5dd;
      border-radius: 6px;
      outline: none;
      transition: border-color 0.2s;
      box-sizing: border-box;
    }

    .form-group input:focus {
      border-color: #1565C0;
      box-shadow: 0 0 0 3px rgba(21, 101, 192, 0.12);
    }

    .form-group input::placeholder {
      color: #aaaaaa;
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

    .register-link {
      text-align: center;
      margin-top: 24px;
      font-size: 14px;
      color: #666666;
    }

    .register-link a {
      color: #1565C0;
      text-decoration: none;
      font-weight: 600;
    }

    .register-link a:hover {
      text-decoration: underline;
    }
  `]
})
export class LoginComponent {
  email: string = '';
  password: string = '';
  errorMessage: string = '';
  isLoading: boolean = false;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  onSubmit(): void {
    this.errorMessage = '';
    this.isLoading = true;

    this.authService.login(this.email, this.password).subscribe({
      next: (response) => {
        this.isLoading = false;
        const role = response.role;
        if (role === 'insurer') {
          this.router.navigate(['/dashboard']);
        } else {
          this.router.navigate(['/patient/chat']);
        }
      },
      error: (err) => {
        this.isLoading = false;
        this.errorMessage = err.error?.detail || err.error?.message || 'Login failed. Please check your credentials.';
      }
    });
  }
}
