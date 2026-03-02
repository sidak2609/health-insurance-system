import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  {
    path: 'login',
    loadComponent: () => import('./features/auth/login.component').then(m => m.LoginComponent),
  },
  {
    path: 'register',
    loadComponent: () => import('./features/auth/register.component').then(m => m.RegisterComponent),
  },
  {
    path: 'patient',
    canActivate: [authGuard],
    children: [
      { path: '', redirectTo: 'claims', pathMatch: 'full' },
      {
        path: 'chat',
        loadComponent: () => import('./features/patient-portal/chat/chat.component').then(m => m.ChatComponent),
      },
      {
        path: 'claims',
        loadComponent: () => import('./features/patient-portal/claims/claims.component').then(m => m.ClaimsComponent),
      },
      {
        path: 'premium',
        loadComponent: () => import('./features/patient-portal/premium/premium.component').then(m => m.PremiumComponent),
      },
      {
        path: 'documents',
        loadComponent: () => import('./features/patient-portal/documents/documents.component').then(m => m.DocumentsComponent),
      },
    ],
  },
  {
    path: 'dashboard',
    canActivate: [authGuard],
    children: [
      { path: '', redirectTo: 'overview', pathMatch: 'full' },
      {
        path: 'overview',
        loadComponent: () => import('./features/insurer-dashboard/dashboard/dashboard.component').then(m => m.DashboardComponent),
      },
      {
        path: 'claims-review',
        loadComponent: () => import('./features/insurer-dashboard/claims-review/claims-review.component').then(m => m.ClaimsReviewComponent),
      },
      {
        path: 'policies',
        loadComponent: () => import('./features/insurer-dashboard/policy-management/policy-management.component').then(m => m.PolicyManagementComponent),
      },
      {
        path: 'audit',
        loadComponent: () => import('./features/insurer-dashboard/audit/audit.component').then(m => m.AuditComponent),
      },
    ],
  },
  {
    path: 'policies',
    canActivate: [authGuard],
    children: [
      { path: '', loadComponent: () => import('./features/policy-details/policy-list.component').then(m => m.PolicyListComponent) },
      { path: 'compare', loadComponent: () => import('./features/policy-details/policy-comparison.component').then(m => m.PolicyComparisonComponent) },
    ],
  },
  {
    path: 'notifications',
    canActivate: [authGuard],
    loadComponent: () => import('./features/notifications/notification-center.component').then(m => m.NotificationCenterComponent),
  },
  { path: '**', redirectTo: '/login' },
];
