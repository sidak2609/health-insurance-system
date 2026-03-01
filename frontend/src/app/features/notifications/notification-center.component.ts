import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { NotificationService } from '../../core/services/notification.service';

@Component({
  selector: 'app-notification-center',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="notifications-page">
      <div class="page-header">
        <h2>Notifications</h2>
        <button class="btn btn-secondary" (click)="markAllRead()" [disabled]="notificationService.unreadCount() === 0">
          Mark All Read
        </button>
      </div>

      <div class="notification-list">
        @for (notif of notificationService.notifications(); track notif.id) {
          <div class="notification-item" [class.unread]="!notif.is_read" (click)="markRead(notif)">
            <div class="notif-icon" [class]="notif.notification_type">
              @switch (notif.notification_type) {
                @case ('claim_submitted') { &#128203; }
                @case ('claim_approved') { &#9989; }
                @case ('claim_rejected') { &#10060; }
                @default { &#128276; }
              }
            </div>
            <div class="notif-content">
              <div class="notif-title">{{ notif.title }}</div>
              <div class="notif-message">{{ notif.message }}</div>
              <div class="notif-time">{{ notif.created_at | date:'medium' }}</div>
            </div>
            @if (!notif.is_read) {
              <div class="unread-dot"></div>
            }
          </div>
        } @empty {
          <div class="empty-state">No notifications yet.</div>
        }
      </div>
    </div>
  `,
  styles: [`
    .notifications-page { padding: 24px; max-width: 700px; margin: 0 auto; }
    .page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
    .page-header h2 { margin: 0; color: #1565C0; }
    .btn-secondary { background: #e0e0e0; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 13px; }
    .btn-secondary:hover:not(:disabled) { background: #bdbdbd; }
    .btn-secondary:disabled { opacity: 0.5; cursor: default; }
    .notification-list { display: flex; flex-direction: column; gap: 8px; }
    .notification-item { display: flex; align-items: flex-start; gap: 12px; padding: 16px; background: #fff; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.06); cursor: pointer; transition: background 0.2s; }
    .notification-item:hover { background: #f5f5f5; }
    .notification-item.unread { background: #E3F2FD; border-left: 3px solid #1565C0; }
    .notif-icon { font-size: 24px; width: 36px; text-align: center; flex-shrink: 0; }
    .notif-content { flex: 1; }
    .notif-title { font-weight: 600; font-size: 14px; color: #333; }
    .notif-message { font-size: 13px; color: #666; margin-top: 4px; }
    .notif-time { font-size: 11px; color: #999; margin-top: 6px; }
    .unread-dot { width: 10px; height: 10px; background: #1565C0; border-radius: 50%; flex-shrink: 0; margin-top: 6px; }
    .empty-state { text-align: center; padding: 40px; color: #999; }
  `]
})
export class NotificationCenterComponent implements OnInit {
  constructor(public notificationService: NotificationService) {}

  ngOnInit() {
    this.notificationService.loadNotifications();
  }

  markRead(notif: any) {
    if (!notif.is_read) {
      this.notificationService.markRead(notif.id);
    }
  }

  markAllRead() {
    this.notificationService.markAllRead();
  }
}
