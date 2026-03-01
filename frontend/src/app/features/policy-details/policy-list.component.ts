import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { ApiService } from '../../core/services/api.service';

@Component({
  selector: 'app-policy-list',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  template: `
    <div class="policy-list-page">
      <div class="page-header">
        <h2>Available Health Plans</h2>
        <div class="search-bar">
          <input type="text" [(ngModel)]="searchTerm" placeholder="Search policies..." (input)="filterPolicies()" />
        </div>
        <a routerLink="/policies/compare" class="btn btn-accent">Compare Plans</a>
      </div>

      <div class="policies-grid">
        @for (policy of filteredPolicies(); track policy.id) {
          <div class="policy-card" [class.basic]="policy.plan_type === 'basic'" [class.standard]="policy.plan_type === 'standard'" [class.premium]="policy.plan_type === 'premium'">
            <div class="card-header">
              <span class="plan-badge">{{ policy.plan_type | uppercase }}</span>
              <h3>{{ policy.name }}</h3>
            </div>
            <div class="card-body">
              <div class="price">₹{{ policy.monthly_premium_base | number }}<span>/mo</span></div>
              <ul class="key-stats">
                <li>Deductible: ₹{{ policy.annual_deductible | number }}</li>
                <li>Max Coverage: ₹{{ policy.max_coverage_limit | number }}</li>
                <li>Copay: {{ policy.copay_percentage }}%</li>
                <li>Age: {{ policy.age_min }}-{{ policy.age_max }}</li>
                <li>Waiting: {{ policy.pre_existing_waiting_months }} months</li>
              </ul>

              <div class="coverage-section">
                <h4 (click)="toggleSection(policy.id, 'coverage')">
                  Covered Services {{ expandedSections[policy.id + '-coverage'] ? '▾' : '▸' }}
                </h4>
                @if (expandedSections[policy.id + '-coverage']) {
                  <ul>
                    @for (item of policy.coverage_details; track item) {
                      <li>{{ item }}</li>
                    }
                  </ul>
                }
              </div>

              <div class="exclusion-section">
                <h4 (click)="toggleSection(policy.id, 'exclusions')">
                  Exclusions {{ expandedSections[policy.id + '-exclusions'] ? '▾' : '▸' }}
                </h4>
                @if (expandedSections[policy.id + '-exclusions']) {
                  <ul>
                    @for (item of policy.exclusions; track item) {
                      <li>{{ item }}</li>
                    }
                  </ul>
                }
              </div>
            </div>
          </div>
        }
      </div>
    </div>
  `,
  styles: [`
    .policy-list-page { padding: 24px; max-width: 1200px; margin: 0 auto; }
    .page-header { display: flex; align-items: center; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }
    .page-header h2 { flex: 1; margin: 0; color: #1565C0; }
    .search-bar input { padding: 8px 16px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; width: 250px; }
    .btn-accent { background: #00897B; color: #fff; padding: 8px 20px; border-radius: 6px; text-decoration: none; font-weight: 500; }
    .btn-accent:hover { background: #00796B; }
    .policies-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 24px; }
    .policy-card { background: #fff; border-radius: 12px; box-shadow: 0 2px 12px rgba(0,0,0,0.08); overflow: hidden; transition: transform 0.2s; }
    .policy-card:hover { transform: translateY(-4px); box-shadow: 0 4px 20px rgba(0,0,0,0.12); }
    .card-header { padding: 20px; color: #fff; }
    .policy-card.basic .card-header { background: #1565C0; }
    .policy-card.standard .card-header { background: #00897B; }
    .policy-card.premium .card-header { background: #6A1B9A; }
    .plan-badge { background: rgba(255,255,255,0.2); padding: 2px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; }
    .card-header h3 { margin: 8px 0 0; }
    .card-body { padding: 20px; }
    .price { font-size: 32px; font-weight: 700; color: #1565C0; margin-bottom: 16px; }
    .price span { font-size: 14px; font-weight: 400; color: #666; }
    .key-stats { list-style: none; padding: 0; margin: 0 0 16px; }
    .key-stats li { padding: 4px 0; color: #555; font-size: 14px; border-bottom: 1px solid #f0f0f0; }
    .coverage-section, .exclusion-section { margin-top: 12px; }
    .coverage-section h4, .exclusion-section h4 { cursor: pointer; color: #1565C0; font-size: 14px; margin: 0 0 8px; }
    .coverage-section ul, .exclusion-section ul { list-style: disc; padding-left: 20px; margin: 0; }
    .coverage-section li, .exclusion-section li { font-size: 13px; color: #555; padding: 2px 0; }
  `]
})
export class PolicyListComponent implements OnInit {
  policies = signal<any[]>([]);
  filteredPolicies = signal<any[]>([]);
  searchTerm = '';
  expandedSections: Record<string, boolean> = {};

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.api.get<any[]>('/policies').subscribe(data => {
      this.policies.set(data);
      this.filteredPolicies.set(data);
    });
  }

  filterPolicies() {
    const term = this.searchTerm.toLowerCase();
    this.filteredPolicies.set(
      this.policies().filter(p =>
        p.name.toLowerCase().includes(term) ||
        p.plan_type.toLowerCase().includes(term)
      )
    );
  }

  toggleSection(policyId: number, section: string) {
    const key = policyId + '-' + section;
    this.expandedSections[key] = !this.expandedSections[key];
  }
}
