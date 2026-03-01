import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { NavbarComponent } from './shared/navbar/navbar.component';
import { AuthService } from './core/services/auth.service';
import { NotificationService } from './core/services/notification.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, NavbarComponent],
  template: `
    @if (authService.isAuthenticated()) {
      <app-navbar />
    }
    <main [class.with-navbar]="authService.isAuthenticated()">
      <router-outlet />
    </main>
  `,
  styles: [`
    main.with-navbar { padding-top: 60px; }
  `]
})
export class AppComponent implements OnInit, OnDestroy {
  constructor(
    public authService: AuthService,
    private notificationService: NotificationService,
  ) {}

  ngOnInit() {
    if (this.authService.isAuthenticated()) {
      this.notificationService.startPolling();
    }
  }

  ngOnDestroy() {
    this.notificationService.stopPolling();
  }
}
