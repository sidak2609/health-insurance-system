import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { NgChartsModule } from 'ng2-charts';
import { Chart, ChartConfiguration, registerables } from 'chart.js';
import { ApiService } from '../../../core/services/api.service';

Chart.register(...registerables);

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule, NgChartsModule],
  template: `
    <div class="dashboard-container" *ngIf="dashboardData">
      <h1>Insurer Dashboard</h1>

      <!-- Stat Cards -->
      <div class="stat-cards">
        <div class="stat-card">
          <div class="stat-label">Total Claims</div>
          <div class="stat-value primary">{{ stats.total_claims }}</div>
          <div class="stat-sub">
            Amount Claimed: {{ stats.total_amount_claimed | currency:'INR' }}
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Approval Rate</div>
          <div class="stat-value success">{{ stats.approval_rate | number:'1.1-1' }}%</div>
          <div class="stat-sub">
            {{ stats.approved_count }} approved &middot; {{ stats.total_amount_approved | currency:'INR' }}
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Rejection Rate</div>
          <div class="stat-value danger">{{ stats.rejection_rate | number:'1.1-1' }}%</div>
          <div class="stat-sub">
            {{ stats.rejected_count }} rejected
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-label">High Risk Claims</div>
          <div class="stat-value accent">{{ stats.high_risk_count }}</div>
          <div class="stat-sub">
            {{ stats.pending_count }} pending review
          </div>
        </div>
      </div>

      <!-- Charts Row -->
      <div class="charts-row">
        <div class="chart-card">
          <h3>Claims by Status</h3>
          <canvas baseChart
            [data]="pieChartData"
            [options]="pieChartOptions"
            [type]="'pie'">
          </canvas>
        </div>
        <div class="chart-card">
          <h3>Claims by Policy</h3>
          <canvas baseChart
            [data]="barChartData"
            [options]="barChartOptions"
            [type]="'bar'">
          </canvas>
        </div>
      </div>

      <!-- Monthly Trends -->
      <div class="section-card">
        <h3>Monthly Trends</h3>
        <div class="trends-list">
          <div class="trend-header">
            <span>Month</span>
            <span>Count</span>
            <span>Amount</span>
          </div>
          <div class="trend-row" *ngFor="let trend of dashboardData.monthly_trends">
            <span>{{ trend.month }}</span>
            <span>{{ trend.count }}</span>
            <span>{{ trend.amount | currency:'INR' }}</span>
          </div>
        </div>
      </div>

      <!-- Bottom Row: Top Conditions + Top Claim Types -->
      <div class="bottom-row">
        <!-- Top Conditions -->
        <div class="section-card">
          <h3>Top Conditions</h3>
          <ul class="conditions-list" *ngIf="dashboardData.top_conditions?.length; else noConditions">
            <li *ngFor="let condition of dashboardData.top_conditions">
              <span class="condition-name">{{ condition.label }}</span>
              <span class="condition-count">{{ condition.count }}</span>
            </li>
          </ul>
          <ng-template #noConditions>
            <p class="empty-state">No condition data available.</p>
          </ng-template>
        </div>

        <!-- Top Claim Types -->
        <div class="section-card">
          <h3>Top Claim Types</h3>
          <ul class="conditions-list" *ngIf="dashboardData.top_claim_types?.length; else noClaimTypes">
            <li *ngFor="let claimType of dashboardData.top_claim_types">
              <span class="condition-name">{{ claimType.label | titlecase }}</span>
              <span class="condition-count">{{ claimType.count }}</span>
            </li>
          </ul>
          <ng-template #noClaimTypes>
            <p class="empty-state">No claim type data available.</p>
          </ng-template>
        </div>
      </div>

      <!-- Age Demographics -->
      <div class="section-card" *ngIf="dashboardData.age_demographics?.length">
        <h3>Age Demographics</h3>
        <div class="age-bars">
          <div class="age-bar-row" *ngFor="let age of dashboardData.age_demographics">
            <span class="age-label">{{ age.label }}</span>
            <div class="bar-track">
              <div class="bar-fill" [style.width]="getBarWidth(age.count, dashboardData.age_demographics) + '%'"></div>
            </div>
            <span class="age-count">{{ age.count }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="loading" *ngIf="!dashboardData && !error">Loading dashboard...</div>
    <div class="error" *ngIf="error">{{ error }}</div>
  `,
  styles: [`
    .dashboard-container {
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

    .stat-cards {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 20px;
      margin-bottom: 32px;
    }

    .stat-card {
      background: #fff;
      border-radius: 12px;
      padding: 24px;
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
      transition: transform 0.2s, box-shadow 0.2s;
    }

    .stat-card:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    }

    .stat-label {
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: #666;
      margin-bottom: 8px;
      font-weight: 500;
    }

    .stat-value {
      font-size: 36px;
      font-weight: 700;
      margin-bottom: 8px;
    }

    .stat-value.primary { color: #1565C0; }
    .stat-value.success { color: #43A047; }
    .stat-value.danger { color: #E53935; }
    .stat-value.accent { color: #00897B; }

    .stat-sub {
      font-size: 13px;
      color: #888;
    }

    .charts-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
      margin-bottom: 32px;
    }

    .chart-card {
      background: #fff;
      border-radius: 12px;
      padding: 24px;
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    }

    .chart-card h3 {
      color: #333;
      margin-bottom: 16px;
      font-size: 18px;
      font-weight: 600;
    }

    .section-card {
      background: #fff;
      border-radius: 12px;
      padding: 24px;
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
      margin-bottom: 24px;
    }

    .section-card h3 {
      color: #333;
      margin-bottom: 16px;
      font-size: 18px;
      font-weight: 600;
    }

    .trends-list {
      width: 100%;
    }

    .trend-header {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      padding: 12px 16px;
      background: #f5f7fa;
      border-radius: 8px;
      font-weight: 600;
      color: #555;
      font-size: 13px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 4px;
    }

    .trend-row {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      padding: 12px 16px;
      border-bottom: 1px solid #f0f0f0;
      font-size: 14px;
      color: #333;
    }

    .trend-row:last-child {
      border-bottom: none;
    }

    .conditions-list {
      list-style: none;
      padding: 0;
      margin: 0;
    }

    .conditions-list li {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 16px;
      border-bottom: 1px solid #f0f0f0;
    }

    .conditions-list li:last-child {
      border-bottom: none;
    }

    .condition-name {
      font-size: 14px;
      color: #333;
    }

    .condition-count {
      background: #e3f2fd;
      color: #1565C0;
      padding: 4px 12px;
      border-radius: 16px;
      font-size: 13px;
      font-weight: 600;
    }

    .bottom-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
      margin-bottom: 24px;
    }

    .bottom-row .section-card {
      margin-bottom: 0;
    }

    .empty-state {
      color: #aaa;
      font-size: 14px;
      padding: 16px 0;
      text-align: center;
    }

    .age-bars {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .age-bar-row {
      display: grid;
      grid-template-columns: 60px 1fr 40px;
      align-items: center;
      gap: 12px;
    }

    .age-label {
      font-size: 13px;
      color: #555;
      font-weight: 500;
    }

    .bar-track {
      background: #e3f2fd;
      border-radius: 4px;
      height: 20px;
      overflow: hidden;
    }

    .bar-fill {
      background: #1565C0;
      height: 100%;
      border-radius: 4px;
      transition: width 0.6s ease;
    }

    .age-count {
      font-size: 13px;
      color: #555;
      text-align: right;
      font-weight: 600;
    }

    @media (max-width: 768px) {
      .bottom-row {
        grid-template-columns: 1fr;
      }
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

    @media (max-width: 1024px) {
      .stat-cards {
        grid-template-columns: repeat(2, 1fr);
      }
      .charts-row {
        grid-template-columns: 1fr;
      }
    }

    @media (max-width: 600px) {
      .stat-cards {
        grid-template-columns: 1fr;
      }
    }
  `]
})
export class DashboardComponent implements OnInit {
  dashboardData: any = null;
  stats: any = {};
  error: string = '';

  pieChartData: ChartConfiguration<'pie'>['data'] = {
    labels: [],
    datasets: [{ data: [], backgroundColor: [] }]
  };

  pieChartOptions: ChartConfiguration<'pie'>['options'] = {
    responsive: true,
    plugins: {
      legend: { position: 'bottom' }
    }
  };

  barChartData: ChartConfiguration<'bar'>['data'] = {
    labels: [],
    datasets: [{ data: [], label: 'Claims', backgroundColor: '#1565C0' }]
  };

  barChartOptions: ChartConfiguration<'bar'>['options'] = {
    responsive: true,
    plugins: {
      legend: { display: false }
    },
    scales: {
      y: { beginAtZero: true }
    }
  };

  constructor(private api: ApiService) {}

  ngOnInit(): void {
    this.api.get('/dashboard').subscribe({
      next: (data: any) => {
        this.dashboardData = data;
        this.stats = data.stats || {};
        this.buildPieChart(data.claims_by_status || []);
        this.buildBarChart(data.claims_by_policy || []);
      },
      error: (err) => {
        this.error = 'Failed to load dashboard data.';
        console.error(err);
      }
    });
  }

  private buildPieChart(claimsByStatus: any[]): void {
    const statusColors: Record<string, string> = {
      'approved': '#43A047',
      'rejected': '#E53935',
      'pending review': '#FFA726',
    };

    this.pieChartData = {
      labels: claimsByStatus.map(s => s.label),
      datasets: [{
        data: claimsByStatus.map(s => s.count),
        backgroundColor: claimsByStatus.map(s =>
          statusColors[(s.label || '').toLowerCase()] || '#90A4AE'
        )
      }]
    };
  }

  private buildBarChart(claimsByPolicy: any[]): void {
    this.barChartData = {
      labels: claimsByPolicy.map(p => p.label || p.policy || p.name),
      datasets: [{
        data: claimsByPolicy.map(p => p.count),
        label: 'Claims',
        backgroundColor: '#1565C0'
      }]
    };
  }

  getBarWidth(count: number, items: any[]): number {
    const max = Math.max(...items.map(i => i.count), 1);
    return Math.round((count / max) * 100);
  }
}
