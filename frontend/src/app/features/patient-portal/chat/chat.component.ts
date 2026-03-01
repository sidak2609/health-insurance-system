import { Component, OnInit, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../../core/services/api.service';
import { AuthService } from '../../../core/services/auth.service';

interface Citation {
  policy_name: string;
  section_title: string;
  excerpt: string;
}

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  follow_up_questions?: string[];
  showCitations?: boolean;
}

interface ChatSession {
  id: string;
  title: string;
  created_at: string;
}

interface ChatResponse {
  session_id: string;
  message: string;
  citations: Citation[];
  follow_up_questions: string[];
}

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="chat-container">
      <!-- Sidebar -->
      <aside class="chat-sidebar">
        <div class="sidebar-header">
          <h3>Chat Sessions</h3>
          <button class="btn-new-chat" (click)="startNewChat()">+ New Chat</button>
        </div>
        <ul class="session-list">
          <li
            *ngFor="let session of sessions"
            class="session-item"
            [class.active]="selectedSession?.id === session.id"
            (click)="selectSession(session)"
          >
            <span class="session-title">{{ session.title || 'Untitled Chat' }}</span>
            <span class="session-date">{{ session.created_at | date:'short' }}</span>
          </li>
        </ul>
      </aside>

      <!-- Main Chat Area -->
      <main class="chat-main">
        <div class="chat-header" *ngIf="selectedSession">
          <h3>{{ selectedSession.title || 'Eligibility Chat' }}</h3>
          <button class="btn-download" (click)="downloadReport()">
            Download Report
          </button>
        </div>

        <div class="chat-welcome" *ngIf="!selectedSession">
          <h2>Eligibility Chat</h2>
          <p>Select an existing session or start a new chat to ask about your insurance eligibility and coverage.</p>
        </div>

        <div class="messages-container" #messagesContainer>
          <div
            *ngFor="let msg of messages"
            class="message-wrapper"
            [class.user]="msg.role === 'user'"
            [class.assistant]="msg.role === 'assistant'"
          >
            <div class="message-bubble">
              <div class="message-content">{{ msg.content }}</div>

              <!-- Citations toggle -->
              <div *ngIf="msg.role === 'assistant' && msg.citations && msg.citations.length > 0" class="citations-section">
                <button class="btn-citations-toggle" (click)="msg.showCitations = !msg.showCitations">
                  {{ msg.showCitations ? 'Hide Sources' : 'Show Sources' }} ({{ msg.citations.length }})
                </button>
                <div class="citations-panel" *ngIf="msg.showCitations">
                  <div *ngFor="let citation of msg.citations" class="citation-card">
                    <div class="citation-policy">{{ citation.policy_name }}</div>
                    <div class="citation-section">{{ citation.section_title }}</div>
                    <div class="citation-excerpt">{{ citation.excerpt }}</div>
                  </div>
                </div>
              </div>

              <!-- Follow-up questions -->
              <div *ngIf="msg.role === 'assistant' && msg.follow_up_questions && msg.follow_up_questions.length > 0" class="follow-up-section">
                <div class="follow-up-chips">
                  <button
                    *ngFor="let question of msg.follow_up_questions"
                    class="chip"
                    (click)="sendFollowUp(question)"
                  >
                    {{ question }}
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div *ngIf="isLoading" class="message-wrapper assistant">
            <div class="message-bubble loading-bubble">
              <span class="dot"></span>
              <span class="dot"></span>
              <span class="dot"></span>
            </div>
          </div>
        </div>

        <!-- Input Bar -->
        <div class="input-bar" *ngIf="selectedSession || messages.length === 0">
          <input
            type="text"
            [(ngModel)]="userInput"
            placeholder="Ask about your insurance eligibility..."
            (keydown.enter)="sendMessage()"
            [disabled]="isLoading"
          />
          <button class="btn-send" (click)="sendMessage()" [disabled]="!userInput.trim() || isLoading">
            Send
          </button>
        </div>
      </main>
    </div>
  `,
  styles: [`
    .chat-container {
      display: flex;
      height: calc(100vh - 80px);
      background: #f5f7fa;
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    }

    /* Sidebar */
    .chat-sidebar {
      width: 280px;
      min-width: 280px;
      background: #1e293b;
      color: #e2e8f0;
      display: flex;
      flex-direction: column;
      border-right: 1px solid #334155;
    }

    .sidebar-header {
      padding: 16px;
      border-bottom: 1px solid #334155;

      h3 {
        margin: 0 0 12px 0;
        font-size: 16px;
        font-weight: 600;
        color: #f1f5f9;
      }
    }

    .btn-new-chat {
      width: 100%;
      padding: 10px 16px;
      background: #3b82f6;
      color: #fff;
      border: none;
      border-radius: 6px;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      transition: background 0.2s;

      &:hover {
        background: #2563eb;
      }
    }

    .session-list {
      list-style: none;
      margin: 0;
      padding: 8px;
      overflow-y: auto;
      flex: 1;
    }

    .session-item {
      padding: 12px;
      border-radius: 6px;
      cursor: pointer;
      margin-bottom: 4px;
      transition: background 0.15s;
      display: flex;
      flex-direction: column;
      gap: 4px;

      &:hover {
        background: #334155;
      }

      &.active {
        background: #3b82f6;
        color: #fff;

        .session-date {
          color: rgba(255, 255, 255, 0.7);
        }
      }
    }

    .session-title {
      font-size: 14px;
      font-weight: 500;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .session-date {
      font-size: 11px;
      color: #94a3b8;
    }

    /* Main Area */
    .chat-main {
      flex: 1;
      display: flex;
      flex-direction: column;
      background: #fff;
    }

    .chat-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16px 24px;
      border-bottom: 1px solid #e2e8f0;
      background: #fff;

      h3 {
        margin: 0;
        font-size: 18px;
        font-weight: 600;
        color: #1e293b;
      }
    }

    .btn-download {
      padding: 8px 16px;
      background: #10b981;
      color: #fff;
      border: none;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 500;
      cursor: pointer;
      transition: background 0.2s;

      &:hover {
        background: #059669;
      }
    }

    .chat-welcome {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      color: #64748b;

      h2 {
        margin: 0 0 8px 0;
        color: #1e293b;
      }

      p {
        font-size: 15px;
        max-width: 400px;
        text-align: center;
        line-height: 1.5;
      }
    }

    /* Messages */
    .messages-container {
      flex: 1;
      overflow-y: auto;
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .message-wrapper {
      display: flex;

      &.user {
        justify-content: flex-end;

        .message-bubble {
          background: #3b82f6;
          color: #fff;
          border-bottom-right-radius: 4px;
        }
      }

      &.assistant {
        justify-content: flex-start;

        .message-bubble {
          background: #f1f5f9;
          color: #1e293b;
          border-bottom-left-radius: 4px;
        }
      }
    }

    .message-bubble {
      max-width: 70%;
      padding: 12px 16px;
      border-radius: 16px;
      font-size: 14px;
      line-height: 1.6;
      word-wrap: break-word;
    }

    .message-content {
      white-space: pre-wrap;
    }

    /* Loading dots */
    .loading-bubble {
      display: flex;
      gap: 4px;
      padding: 16px 20px;

      .dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #94a3b8;
        animation: bounce 1.4s infinite ease-in-out both;

        &:nth-child(1) { animation-delay: -0.32s; }
        &:nth-child(2) { animation-delay: -0.16s; }
      }
    }

    @keyframes bounce {
      0%, 80%, 100% { transform: scale(0); }
      40% { transform: scale(1); }
    }

    /* Citations */
    .citations-section {
      margin-top: 10px;
      border-top: 1px solid #e2e8f0;
      padding-top: 8px;
    }

    .btn-citations-toggle {
      background: none;
      border: none;
      color: #3b82f6;
      font-size: 12px;
      font-weight: 500;
      cursor: pointer;
      padding: 4px 0;

      &:hover {
        text-decoration: underline;
      }
    }

    .citations-panel {
      margin-top: 8px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .citation-card {
      background: #fefce8;
      border: 1px solid #fde68a;
      border-radius: 8px;
      padding: 10px 12px;
    }

    .citation-policy {
      font-size: 13px;
      font-weight: 600;
      color: #92400e;
      margin-bottom: 2px;
    }

    .citation-section {
      font-size: 12px;
      font-weight: 500;
      color: #a16207;
      margin-bottom: 6px;
    }

    .citation-excerpt {
      font-size: 12px;
      color: #78716c;
      line-height: 1.5;
      font-style: italic;
    }

    /* Follow-up chips */
    .follow-up-section {
      margin-top: 10px;
    }

    .follow-up-chips {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }

    .chip {
      padding: 6px 14px;
      background: #e0e7ff;
      color: #3730a3;
      border: 1px solid #c7d2fe;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.15s;
      text-align: left;

      &:hover {
        background: #c7d2fe;
        border-color: #a5b4fc;
      }
    }

    /* Input Bar */
    .input-bar {
      display: flex;
      gap: 12px;
      padding: 16px 24px;
      border-top: 1px solid #e2e8f0;
      background: #fff;

      input {
        flex: 1;
        padding: 12px 16px;
        border: 1px solid #d1d5db;
        border-radius: 8px;
        font-size: 14px;
        outline: none;
        transition: border-color 0.2s;

        &:focus {
          border-color: #3b82f6;
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }

        &:disabled {
          background: #f9fafb;
        }
      }
    }

    .btn-send {
      padding: 12px 24px;
      background: #3b82f6;
      color: #fff;
      border: none;
      border-radius: 8px;
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
  `]
})
export class ChatComponent implements OnInit, AfterViewChecked {
  @ViewChild('messagesContainer') private messagesContainer!: ElementRef;

  sessions: ChatSession[] = [];
  selectedSession: ChatSession | null = null;
  messages: ChatMessage[] = [];
  userInput = '';
  isLoading = false;
  private shouldScrollToBottom = false;

  constructor(
    private apiService: ApiService,
    private authService: AuthService
  ) {}

  ngOnInit(): void {
    this.loadSessions();
  }

  ngAfterViewChecked(): void {
    if (this.shouldScrollToBottom) {
      this.scrollToBottom();
      this.shouldScrollToBottom = false;
    }
  }

  loadSessions(): void {
    this.apiService.get<ChatSession[]>('/chat/sessions').subscribe({
      next: (sessions) => {
        this.sessions = sessions;
      },
      error: (err) => {
        console.error('Failed to load chat sessions:', err);
      }
    });
  }

  selectSession(session: ChatSession): void {
    this.selectedSession = session;
    this.loadMessages(session.id);
  }

  loadMessages(sessionId: string): void {
    this.apiService.get<ChatMessage[]>(`/chat/sessions/${sessionId}/messages`).subscribe({
      next: (messages) => {
        this.messages = messages.map((msg) => ({ ...msg, showCitations: false }));
        this.shouldScrollToBottom = true;
      },
      error: (err) => {
        console.error('Failed to load messages:', err);
      }
    });
  }

  startNewChat(): void {
    this.selectedSession = null;
    this.messages = [];
    this.userInput = '';
  }

  sendMessage(): void {
    const text = this.userInput.trim();
    if (!text || this.isLoading) return;

    this.messages.push({ role: 'user', content: text });
    this.userInput = '';
    this.isLoading = true;
    this.shouldScrollToBottom = true;

    const payload: any = { message: text };
    if (this.selectedSession) {
      payload.session_id = this.selectedSession.id;
    }

    this.apiService.post<ChatResponse>('/chat', payload).subscribe({
      next: (response) => {
        if (!this.selectedSession) {
          this.selectedSession = {
            id: response.session_id,
            title: text.substring(0, 50),
            created_at: new Date().toISOString()
          };
          this.sessions.unshift(this.selectedSession);
        }

        this.messages.push({
          role: 'assistant',
          content: response.message,
          citations: response.citations,
          follow_up_questions: response.follow_up_questions,
          showCitations: false
        });
        this.isLoading = false;
        this.shouldScrollToBottom = true;
      },
      error: (err) => {
        console.error('Failed to send message:', err);
        this.isLoading = false;
      }
    });
  }

  sendFollowUp(question: string): void {
    this.userInput = question;
    this.sendMessage();
  }

  downloadReport(): void {
    if (!this.selectedSession) return;

    this.apiService.getBlob(`/chat/sessions/${this.selectedSession.id}/report`).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `chat-report-${this.selectedSession!.id}.pdf`;
        a.click();
        window.URL.revokeObjectURL(url);
      },
      error: (err) => {
        console.error('Failed to download report:', err);
      }
    });
  }

  private scrollToBottom(): void {
    try {
      const el = this.messagesContainer?.nativeElement;
      if (el) {
        el.scrollTop = el.scrollHeight;
      }
    } catch (err) {}
  }
}
