import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../../core/services/api.service';
import { AuthService } from '../../../core/services/auth.service';

interface Document {
  id: string;
  filename: string;
  document_type: string;
  uploaded_at: string;
}

@Component({
  selector: 'app-documents',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="documents-container">
      <!-- Upload Section -->
      <section class="card upload-section">
        <h2>Upload Document</h2>
        <p class="subtitle">Upload medical records, prescriptions, lab results, and other insurance-related documents.</p>

        <form (ngSubmit)="uploadDocument()" class="upload-form">
          <div class="form-row">
            <div class="form-group">
              <label for="documentType">Document Type</label>
              <select id="documentType" [(ngModel)]="documentType" name="document_type" required>
                <option value="" disabled>Select document type</option>
                <option value="medical_record">Medical Record</option>
                <option value="prescription">Prescription</option>
                <option value="lab_result">Lab Result</option>
                <option value="insurance_card">Insurance Card</option>
                <option value="claim_receipt">Claim Receipt</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div class="form-group file-group">
              <label for="fileInput">File</label>
              <div class="file-input-wrapper">
                <input
                  type="file"
                  id="fileInput"
                  (change)="onFileSelected($event)"
                  #fileInput
                  class="file-input-hidden"
                />
                <button type="button" class="btn-choose-file" (click)="fileInput.click()">
                  Choose File
                </button>
                <span class="file-name">{{ selectedFile ? selectedFile.name : 'No file selected' }}</span>
              </div>
            </div>
          </div>

          <div class="form-actions">
            <button
              type="submit"
              class="btn-upload"
              [disabled]="isUploading || !selectedFile || !documentType"
            >
              {{ isUploading ? 'Uploading...' : 'Upload' }}
            </button>
          </div>

          <div *ngIf="uploadSuccess" class="alert alert-success">
            Document uploaded successfully!
          </div>
          <div *ngIf="uploadError" class="alert alert-error">
            {{ uploadError }}
          </div>
        </form>
      </section>

      <!-- Documents List -->
      <section class="card documents-list-section">
        <h2>Your Documents</h2>

        <div *ngIf="isLoadingDocuments" class="loading-state">Loading documents...</div>

        <div *ngIf="!isLoadingDocuments && documents.length === 0" class="empty-state">
          No documents uploaded yet. Upload your first document above.
        </div>

        <div class="table-wrapper" *ngIf="documents.length > 0">
          <table class="documents-table">
            <thead>
              <tr>
                <th>Filename</th>
                <th>Type</th>
                <th>Uploaded Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let doc of documents">
                <td class="cell-filename">
                  <span class="file-icon">{{ getFileIcon(doc.filename) }}</span>
                  {{ doc.filename }}
                </td>
                <td>
                  <span class="type-badge">{{ formatDocumentType(doc.document_type) }}</span>
                </td>
                <td class="cell-date">{{ doc.uploaded_at | date:'medium' }}</td>
                <td>
                  <button class="btn-download" (click)="downloadDocument(doc)">
                    Download
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  `,
  styles: [`
    .documents-container {
      max-width: 1000px;
      margin: 0 auto;
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 24px;
    }

    .card {
      background: #fff;
      border-radius: 10px;
      padding: 24px 28px;
      box-shadow: 0 1px 8px rgba(0, 0, 0, 0.07);
    }

    h2 {
      margin: 0 0 4px 0;
      font-size: 20px;
      font-weight: 600;
      color: #1e293b;
    }

    .subtitle {
      margin: 0 0 20px 0;
      font-size: 14px;
      color: #64748b;
      line-height: 1.5;
    }

    /* Upload Form */
    .upload-form {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .form-row {
      display: flex;
      gap: 16px;
      align-items: flex-end;
      flex-wrap: wrap;
    }

    .form-group {
      display: flex;
      flex-direction: column;
      gap: 6px;
      flex: 1;
      min-width: 200px;

      label {
        font-size: 13px;
        font-weight: 600;
        color: #475569;
      }

      select {
        padding: 10px 12px;
        border: 1px solid #d1d5db;
        border-radius: 6px;
        font-size: 14px;
        outline: none;
        transition: border-color 0.2s;
        background: #fff;

        &:focus {
          border-color: #3b82f6;
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
      }
    }

    .file-group {
      flex: 1.5;
    }

    .file-input-wrapper {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .file-input-hidden {
      display: none;
    }

    .btn-choose-file {
      padding: 10px 16px;
      background: #f1f5f9;
      color: #334155;
      border: 1px solid #d1d5db;
      border-radius: 6px;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.15s;

      &:hover {
        background: #e2e8f0;
        border-color: #94a3b8;
      }
    }

    .file-name {
      font-size: 13px;
      color: #64748b;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      max-width: 250px;
    }

    .form-actions {
      display: flex;
      justify-content: flex-end;
    }

    .btn-upload {
      padding: 10px 28px;
      background: #3b82f6;
      color: #fff;
      border: none;
      border-radius: 6px;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      transition: background 0.2s;

      &:hover:not(:disabled) {
        background: #2563eb;
      }

      &:disabled {
        background: #93c5fd;
        cursor: not-allowed;
      }
    }

    /* Alerts */
    .alert {
      padding: 12px 16px;
      border-radius: 6px;
      font-size: 14px;
      font-weight: 500;
    }

    .alert-success {
      background: #dcfce7;
      color: #166534;
      border: 1px solid #bbf7d0;
    }

    .alert-error {
      background: #fef2f2;
      color: #991b1b;
      border: 1px solid #fecaca;
    }

    /* Table */
    .loading-state,
    .empty-state {
      text-align: center;
      padding: 32px;
      color: #64748b;
      font-size: 14px;
    }

    .table-wrapper {
      overflow-x: auto;
    }

    .documents-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;

      th {
        text-align: left;
        padding: 12px 16px;
        background: #f8fafc;
        color: #475569;
        font-weight: 600;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        border-bottom: 2px solid #e2e8f0;
      }

      td {
        padding: 12px 16px;
        border-bottom: 1px solid #f1f5f9;
        color: #334155;
      }

      tbody tr:hover {
        background: #f8fafc;
      }
    }

    .cell-filename {
      font-weight: 500;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .file-icon {
      font-size: 16px;
      width: 20px;
      text-align: center;
    }

    .cell-date {
      color: #64748b;
      white-space: nowrap;
    }

    .type-badge {
      display: inline-block;
      padding: 4px 10px;
      background: #e0e7ff;
      color: #3730a3;
      border-radius: 12px;
      font-size: 12px;
      font-weight: 600;
      text-transform: capitalize;
    }

    .btn-download {
      padding: 6px 14px;
      background: #fff;
      color: #3b82f6;
      border: 1px solid #3b82f6;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.15s;

      &:hover {
        background: #3b82f6;
        color: #fff;
      }
    }
  `]
})
export class DocumentsComponent implements OnInit {
  documents: Document[] = [];
  selectedFile: File | null = null;
  documentType = '';
  isUploading = false;
  isLoadingDocuments = false;
  uploadSuccess = false;
  uploadError = '';

  constructor(
    private apiService: ApiService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.loadDocuments();
  }

  loadDocuments(): void {
    this.isLoadingDocuments = true;
    this.apiService.get<Document[]>('/documents').subscribe({
      next: (documents) => {
        this.documents = documents;
        this.isLoadingDocuments = false;
      },
      error: (err) => {
        console.error('Failed to load documents:', err);
        this.isLoadingDocuments = false;
      }
    });
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.selectedFile = input.files[0];
    }
  }

  uploadDocument(): void {
    if (this.isUploading || !this.selectedFile || !this.documentType) return;

    this.isUploading = true;
    this.uploadSuccess = false;
    this.uploadError = '';

    const formData = new FormData();
    formData.append('file', this.selectedFile);
    formData.append('document_type', this.documentType);

    this.apiService.post('/documents/upload', formData).subscribe({
      next: () => {
        this.isUploading = false;
        this.uploadSuccess = true;
        this.selectedFile = null;
        this.documentType = '';

        // Reset the file input
        const fileInput = document.getElementById('fileInput') as HTMLInputElement;
        if (fileInput) {
          fileInput.value = '';
        }

        this.loadDocuments();

        setTimeout(() => {
          this.uploadSuccess = false;
        }, 4000);
      },
      error: (err) => {
        this.isUploading = false;
        this.uploadError = err?.error?.detail || 'Failed to upload document. Please try again.';
        console.error('Document upload failed:', err);
      }
    });
  }

  downloadDocument(doc: Document): void {
    this.apiService.getBlob(`/documents/${doc.id}/download`).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = doc.filename;
        a.click();
        window.URL.revokeObjectURL(url);
      },
      error: (err) => {
        console.error('Failed to download document:', err);
      }
    });
  }

  formatDocumentType(type: string): string {
    return type.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
  }

  getFileIcon(filename: string): string {
    const ext = filename.split('.').pop()?.toLowerCase();
    switch (ext) {
      case 'pdf': return 'PDF';
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'gif': return 'IMG';
      case 'doc':
      case 'docx': return 'DOC';
      case 'xls':
      case 'xlsx': return 'XLS';
      default: return 'FILE';
    }
  }
}
