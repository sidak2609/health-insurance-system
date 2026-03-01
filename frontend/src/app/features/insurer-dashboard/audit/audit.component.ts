import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../../core/services/api.service';

@Component({
  selector: 'app-audit',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="audit-container">
      <h1>Audit Log</h1>

      <div class="table-card">
        <div class="table-wrapper">
          <table class="audit-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>User</th>
                <th>Action</th>
                <th>Entity Type</th>
                <th>Entity ID</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let log of auditLogs; let odd = odd" [class.zebra]="odd">
                <td class="timestamp-cell">{{ log.timestamp | date:'medium' }}</td>
                <td>{{ log.user || log.username || 'System' }}</td>
                <td>
                  <span class="action-badge" [ngClass]="getActionClass(log.action)">
                    {{ log.action }}
                  </span>
                </td>
                <td>{{ log.entity_type }}</td>
                <td class="entity-id-cell">{{ log.entity_id }}</td>
                <td class="details-cell">
                  <pre class="details-text" *ngIf="log.details">{{ formatDetails(log.details) }}</pre>
                  <span class="no-details" *ngIf="!log.details">--</span>
                </td>
              </tr>
              <tr *ngIf="auditLogs.length === 0 && !isLoading">
                <td colspan="6" class="empty-row">No audit logs found.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <div class="loading" *ngIf="isLoading">Loading audit logs...</div>
    <div class="error" *ngIf="error">{{ error }}</div>
  `,
  styles: [`
    .audit-container {
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

    .table-card {
      background: #fff;
      border-radius: 12px;
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
      overflow: hidden;
    }

    .table-wrapper {
      overflow-x: auto;
    }

    .audit-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }

    .audit-table thead th {
      background: #f5f7fa;
      padding: 14px 12px;
      text-align: left;
      font-weight: 600;
      color: #555;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      white-space: nowrap;
      position: sticky;
      top: 0;
    }

    .audit-table tbody td {
      padding: 12px;
      border-bottom: 1px solid #f0f0f0;
      color: #333;
      vertical-align: top;
    }

    .audit-table tbody tr:hover {
      background: #fafbfc;
    }

    .audit-table tbody tr.zebra {
      background: #f9fafb;
    }

    .audit-table tbody tr.zebra:hover {
      background: #f0f4f8;
    }

    .timestamp-cell {
      white-space: nowrap;
      font-size: 13px;
      color: #666;
    }

    .entity-id-cell {
      font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
      font-size: 13px;
      color: #555;
    }

    .action-badge {
      padding: 4px 10px;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.3px;
      white-space: nowrap;
    }

    .action-create { background: #e8f5e9; color: #2e7d32; }
    .action-update { background: #e3f2fd; color: #1565C0; }
    .action-delete { background: #ffebee; color: #c62828; }
    .action-review { background: #fff3e0; color: #ef6c00; }
    .action-login { background: #f3e5f5; color: #7b1fa2; }
    .action-default { background: #f5f5f5; color: #616161; }

    .details-cell {
      max-width: 400px;
    }

    .details-text {
      margin: 0;
      padding: 8px 12px;
      background: #f5f7fa;
      border-radius: 6px;
      font-size: 12px;
      font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
      white-space: pre-wrap;
      word-break: break-word;
      max-height: 120px;
      overflow-y: auto;
      color: #444;
      line-height: 1.5;
    }

    .no-details {
      color: #bbb;
      font-size: 13px;
    }

    .empty-row {
      text-align: center;
      color: #888;
      padding: 40px 12px !important;
    }

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
  `]
})
export class AuditComponent implements OnInit {
  auditLogs: any[] = [];
  isLoading: boolean = false;
  error: string = '';

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.isLoading = true;
    this.api.get('/dashboard/audit').subscribe({
      next: (data: any) => {
        this.auditLogs = Array.isArray(data) ? data : data.logs || data.audit_logs || [];
        this.isLoading = false;
      },
      error: (err) => {
        this.error = 'Failed to load audit logs.';
        this.isLoading = false;
        console.error(err);
      }
    });
  }

  formatDetails(details: any): string {
    if (!details) return '';
    if (typeof details === 'string') {
      try {
        return JSON.stringify(JSON.parse(details), null, 2);
      } catch {
        return details;
      }
    }
    return JSON.stringify(details, null, 2);
  }

  getActionClass(action: string): string {
    if (!action) return 'action-default';
    const normalized = action.toLowerCase();
    if (normalized.includes('create') || normalized.includes('add')) return 'action-create';
    if (normalized.includes('update') || normalized.includes('edit') || normalized.includes('modify')) return 'action-update';
    if (normalized.includes('delete') || normalized.includes('remove')) return 'action-delete';
    if (normalized.includes('review') || normalized.includes('approve') || normalized.includes('reject')) return 'action-review';
    if (normalized.includes('login') || normalized.includes('logout') || normalized.includes('auth')) return 'action-login';
    return 'action-default';
  }
}
