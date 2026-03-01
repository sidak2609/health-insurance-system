import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Router } from '@angular/router';
import { AuthService } from '../../core/services/auth.service';
import { NotificationService } from '../../core/services/notification.service';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <nav class="navbar">
      <div class="navbar-left">
        <a class="brand" routerLink="/">HealthInsure</a>
        <ul class="nav-links">
          @if (authService.isPatient()) {
            <li><a routerLink="/patient/chat" routerLinkActive="active">Chat</a></li>
            <li><a routerLink="/patient/claims" routerLinkActive="active">Claims</a></li>
            <li><a routerLink="/patient/premium" routerLinkActive="active">Premium Estimator</a></li>
            <li><a routerLink="/patient/documents" routerLinkActive="active">Documents</a></li>
            <li><a routerLink="/policies" routerLinkActive="active">Policies</a></li>
          }
          @if (authService.isInsurer()) {
            <li><a routerLink="/dashboard/overview" routerLinkActive="active">Dashboard</a></li>
            <li><a routerLink="/dashboard/claims-review" routerLinkActive="active">Claims Review</a></li>
            <li><a routerLink="/dashboard/policies" routerLinkActive="active">Policy Management</a></li>
            <li><a routerLink="/dashboard/audit" routerLinkActive="active">Audit Log</a></li>
            <li><a routerLink="/policies" routerLinkActive="active">Policies</a></li>
          }
        </ul>
      </div>

      <div class="navbar-right">
        <a class="notification-bell" routerLink="/notifications">
          <span class="bell-icon">&#128276;</span>
          @if (notificationService.unreadCount() > 0) {
            <span class="badge">{{ notificationService.unreadCount() }}</span>
          }
        </a>
        <span class="user-name">{{ authService.currentUser()?.full_name }}</span>
        <button class="logout-btn" (click)="logout()">Logout</button>
      </div>
    </nav>
  `,
  styles: [`
    .navbar {
      position: fixed; top: 0; left: 0; right: 0; z-index: 1000;
      display: flex; align-items: center; justify-content: space-between;
      background-color: #1565C0; color: #fff;
      padding: 0 24px; height: 60px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .navbar-left { display: flex; align-items: center; gap: 32px; }
    .brand { font-size: 20px; font-weight: 700; color: #fff; text-decoration: none; }
    .brand:hover { opacity: 0.9; }
    .nav-links { display: flex; list-style: none; margin: 0; padding: 0; gap: 4px; }
    .nav-links li a {
      color: rgba(255,255,255,0.85); text-decoration: none;
      padding: 8px 14px; border-radius: 4px;
      font-size: 14px; font-weight: 500;
      transition: background 0.2s;
    }
    .nav-links li a:hover { background: rgba(255,255,255,0.15); color: #fff; }
    .nav-links li a.active { background: rgba(255,255,255,0.25); color: #fff; }
    .navbar-right { display: flex; align-items: center; gap: 18px; }
    .notification-bell {
      position: relative; color: #fff; text-decoration: none;
      cursor: pointer; font-size: 20px; line-height: 1;
    }
    .notification-bell:hover { opacity: 0.8; }
    .badge {
      position: absolute; top: -8px; right: -10px;
      background: #e53935; color: #fff;
      font-size: 11px; font-weight: 700;
      min-width: 18px; height: 18px; border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
      padding: 0 4px;
    }
    .user-name { font-size: 14px; font-weight: 500; color: rgba(255,255,255,0.9); }
    .logout-btn {
      background: rgba(255,255,255,0.15); color: #fff;
      border: 1px solid rgba(255,255,255,0.3);
      padding: 6px 16px; border-radius: 4px;
      font-size: 13px; font-weight: 500; cursor: pointer;
    }
    .logout-btn:hover { background: rgba(255,255,255,0.25); }
  `]
})
export class NavbarComponent {
  constructor(
    public authService: AuthService,
    public notificationService: NotificationService,
    private router: Router,
  ) {}

  logout(): void {
    this.authService.logout();
    this.notificationService.stopPolling();
    this.router.navigate(['/login']);
  }
}
