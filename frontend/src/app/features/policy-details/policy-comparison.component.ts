import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../core/services/api.service';

@Component({
  selector: 'app-policy-comparison',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="comparison-page">
      <h2>Compare Health Plans</h2>

      <div class="selector">
        <p>Select plans to compare (2-3):</p>
        <div class="plan-checkboxes">
          @for (policy of allPolicies(); track policy.id) {
            <label>
              <input type="checkbox" [checked]="isSelected(policy.id)" (change)="togglePolicy(policy.id)" [disabled]="!isSelected(policy.id) && selectedIds().length >= 3" />
              {{ policy.name }}
            </label>
          }
        </div>
      </div>

      @if (selectedPolicies().length >= 2) {
        <div class="comparison-table-wrapper">
          <table class="comparison-table">
            <thead>
              <tr>
                <th>Feature</th>
                @for (p of selectedPolicies(); track p.id) {
                  <th [class]="p.plan_type">{{ p.name }}</th>
                }
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Monthly Premium</td>
                @for (p of selectedPolicies(); track p.id) { <td>₹{{ p.monthly_premium_base | number }}</td> }
              </tr>
              <tr>
                <td>Annual Deductible</td>
                @for (p of selectedPolicies(); track p.id) { <td>₹{{ p.annual_deductible | number }}</td> }
              </tr>
              <tr>
                <td>Max Coverage</td>
                @for (p of selectedPolicies(); track p.id) { <td>₹{{ p.max_coverage_limit | number }}</td> }
              </tr>
              <tr>
                <td>Copay</td>
                @for (p of selectedPolicies(); track p.id) { <td>{{ p.copay_percentage }}%</td> }
              </tr>
              <tr>
                <td>Age Range</td>
                @for (p of selectedPolicies(); track p.id) { <td>{{ p.age_min }}-{{ p.age_max }}</td> }
              </tr>
              <tr>
                <td>Smoker Surcharge</td>
                @for (p of selectedPolicies(); track p.id) { <td>{{ p.smoker_surcharge_pct }}%</td> }
              </tr>
              <tr>
                <td>BMI Surcharge</td>
                @for (p of selectedPolicies(); track p.id) { <td>{{ p.bmi_surcharge_pct }}%</td> }
              </tr>
              <tr>
                <td>Pre-existing Wait</td>
                @for (p of selectedPolicies(); track p.id) { <td>{{ p.pre_existing_waiting_months }} months</td> }
              </tr>
              <tr>
                <td>Covered Services</td>
                @for (p of selectedPolicies(); track p.id) {
                  <td>
                    <ul>
                      @for (item of p.coverage_details; track item) { <li>{{ item }}</li> }
                    </ul>
                  </td>
                }
              </tr>
              <tr>
                <td>Exclusions</td>
                @for (p of selectedPolicies(); track p.id) {
                  <td>
                    <ul class="exclusions">
                      @for (item of p.exclusions; track item) { <li>{{ item }}</li> }
                    </ul>
                  </td>
                }
              </tr>
            </tbody>
          </table>
        </div>
      } @else {
        <p class="hint">Please select at least 2 plans to compare.</p>
      }
    </div>
  `,
  styles: [`
    .comparison-page { padding: 24px; max-width: 1100px; margin: 0 auto; }
    h2 { color: #1565C0; margin-bottom: 20px; }
    .selector { margin-bottom: 24px; }
    .plan-checkboxes { display: flex; gap: 20px; flex-wrap: wrap; }
    .plan-checkboxes label { display: flex; align-items: center; gap: 6px; cursor: pointer; padding: 8px 16px; background: #f5f5f5; border-radius: 8px; }
    .comparison-table-wrapper { overflow-x: auto; }
    .comparison-table { width: 100%; border-collapse: collapse; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
    .comparison-table th, .comparison-table td { padding: 12px 16px; text-align: left; border-bottom: 1px solid #eee; font-size: 14px; vertical-align: top; }
    .comparison-table th { background: #f5f5f5; font-weight: 600; }
    th.basic { background: #1565C0; color: #fff; }
    th.standard { background: #00897B; color: #fff; }
    th.premium { background: #6A1B9A; color: #fff; }
    .comparison-table td:first-child { font-weight: 500; background: #fafafa; min-width: 160px; }
    ul { list-style: disc; padding-left: 16px; margin: 0; }
    ul li { font-size: 13px; padding: 2px 0; }
    ul.exclusions li { color: #E53935; }
    .hint { color: #999; font-style: italic; }
  `]
})
export class PolicyComparisonComponent implements OnInit {
  allPolicies = signal<any[]>([]);
  selectedIds = signal<number[]>([]);
  selectedPolicies = signal<any[]>([]);

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.api.get<any[]>('/policies').subscribe(data => {
      this.allPolicies.set(data);
      if (data.length >= 2) {
        this.selectedIds.set(data.slice(0, 2).map((p: any) => p.id));
        this.updateSelected();
      }
    });
  }

  isSelected(id: number): boolean {
    return this.selectedIds().includes(id);
  }

  togglePolicy(id: number) {
    const current = this.selectedIds();
    if (current.includes(id)) {
      this.selectedIds.set(current.filter(i => i !== id));
    } else if (current.length < 3) {
      this.selectedIds.set([...current, id]);
    }
    this.updateSelected();
  }

  updateSelected() {
    const ids = this.selectedIds();
    this.selectedPolicies.set(this.allPolicies().filter(p => ids.includes(p.id)));
  }
}
