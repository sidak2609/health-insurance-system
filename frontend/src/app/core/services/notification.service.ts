import { Injectable, signal, computed, OnDestroy } from '@angular/core';
import { ApiService } from './api.service';

export interface Notification {
  id: number;
  title: string;
  message: string;
  notification_type: string;
  is_read: boolean;
  related_entity_type: string;
  related_entity_id: number;
  created_at: string;
}

@Injectable({
  providedIn: 'root'
})
export class NotificationService implements OnDestroy {
  notifications = signal<Notification[]>([]);
  unreadCount = computed(() => this.notifications().filter(n => !n.is_read).length);

  private pollingInterval: ReturnType<typeof setInterval> | null = null;

  constructor(private api: ApiService) {}

  loadNotifications(): void {
    this.api.get<Notification[]>('/notifications').subscribe({
      next: (notifications) => {
        this.notifications.set(notifications);
      },
      error: () => {
        // Notification fetch failed; keep existing data
      }
    });
  }

  markRead(id: number): void {
    this.api.put<Notification>(`/notifications/${id}/read`, {}).subscribe({
      next: () => {
        this.notifications.update(notifications =>
          notifications.map(n => n.id === id ? { ...n, is_read: true } : n)
        );
      }
    });
  }

  markAllRead(): void {
    this.api.put<any>('/notifications/read-all', {}).subscribe({
      next: () => {
        this.notifications.update(notifications =>
          notifications.map(n => ({ ...n, is_read: true }))
        );
      }
    });
  }

  startPolling(): void {
    this.stopPolling();
    this.loadNotifications();
    this.pollingInterval = setInterval(() => {
      this.loadNotifications();
    }, 30000);
  }

  stopPolling(): void {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = null;
    }
  }

  ngOnDestroy(): void {
    this.stopPolling();
  }
}
