import { Injectable, signal, computed } from '@angular/core';
import { ApiService } from './api.service';
import { Observable, tap } from 'rxjs';

interface TokenResponse {
  access_token: string;
  token_type: string;
  role: string;
  user_id: number;
  full_name: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private tokenSignal = signal<string | null>(this.getToken());
  currentUser = signal<any>(this.getStoredUser());

  isAuthenticated = computed(() => !!this.tokenSignal());
  isPatient = computed(() => this.currentUser()?.role === 'patient');
  isInsurer = computed(() => this.currentUser()?.role === 'insurer');

  constructor(private api: ApiService) {}

  login(email: string, password: string): Observable<TokenResponse> {
    return this.api.post<TokenResponse>('/auth/login', { email, password }).pipe(
      tap((response) => {
        this.storeToken(response.access_token);
        this.storeUser({
          user_id: response.user_id,
          full_name: response.full_name,
          role: response.role
        });
        this.loadUser();
      })
    );
  }

  register(data: any): Observable<TokenResponse> {
    return this.api.post<TokenResponse>('/auth/register', data).pipe(
      tap((response) => {
        this.storeToken(response.access_token);
        this.storeUser({
          user_id: response.user_id,
          full_name: response.full_name,
          role: response.role
        });
        this.loadUser();
      })
    );
  }

  logout(): void {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    this.tokenSignal.set(null);
    this.currentUser.set(null);
  }

  getToken(): string | null {
    return localStorage.getItem('token');
  }

  loadUser(): void {
    this.api.get<any>('/auth/profile').subscribe({
      next: (profile) => {
        this.storeUser(profile);
      },
      error: () => {
        // Profile fetch failed; keep existing user data
      }
    });
  }

  private storeToken(token: string): void {
    localStorage.setItem('token', token);
    this.tokenSignal.set(token);
  }

  private storeUser(user: any): void {
    localStorage.setItem('user', JSON.stringify(user));
    this.currentUser.set(user);
  }

  private getStoredUser(): any {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  }
}
