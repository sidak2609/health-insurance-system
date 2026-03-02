import { Component, OnInit, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DomSanitizer, SafeHtml } from '@angular/platform-browser';
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
  timestamp?: Date;
}

interface ChatSession {
  id: string;
  title: string;
  created_at: string;
  message_count?: number;
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
    <!-- Floating Action Button -->
    <button class="fab" (click)="toggleChat()" [class.open]="isOpen" title="Insurance Assistant">
      <svg *ngIf="!isOpen" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
      </svg>
      <svg *ngIf="isOpen" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <line x1="18" y1="6" x2="6" y2="18"></line>
        <line x1="6" y1="6" x2="18" y2="18"></line>
      </svg>
      <span class="fab-label" *ngIf="!isOpen">Ask AI</span>
    </button>

    <!-- Chat Popup Panel -->
    <div class="chat-popup" [class.visible]="isOpen">

      <!-- Panel Header -->
      <div class="popup-header">
        <div class="header-left">
          <div class="header-avatar">AI</div>
          <div>
            <div class="header-title">Insurance Assistant</div>
            <div class="header-sub" *ngIf="currentUser">Hi {{ firstName }}! Ready to help.</div>
          </div>
        </div>
        <div class="header-actions">
          <button class="btn-icon" (click)="showSessions = !showSessions" title="Chat history" [class.active]="showSessions">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 20h9"></path><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
            </svg>
          </button>
          <button class="btn-icon" *ngIf="selectedSession" (click)="downloadReport()" title="Download report">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="7 10 12 15 17 10"></polyline>
              <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
          </button>
          <button class="btn-icon" (click)="toggleChat()" title="Close">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
      </div>

      <!-- Sessions Drawer -->
      <div class="sessions-drawer" [class.open]="showSessions">
        <div class="drawer-header">
          <span>Chat History</span>
          <button class="btn-new-chat" (click)="startNewChat()">+ New</button>
        </div>
        <ul class="session-list">
          <li
            *ngFor="let session of sessions"
            class="session-item"
            [class.active]="selectedSession?.id === session.id"
            (click)="selectSession(session); showSessions = false"
          >
            <span class="session-title">{{ session.title || 'Chat' }}</span>
            <span class="session-date">{{ session.created_at | date:'MMM d' }}</span>
          </li>
          <li *ngIf="sessions.length === 0" class="no-sessions">No previous chats</li>
        </ul>
      </div>

      <!-- Welcome screen -->
      <div class="welcome-screen" *ngIf="!selectedSession && messages.length === 0 && !showSessions">
        <div class="welcome-avatar">{{ initials || '🏥' }}</div>
        <h3>Hi {{ firstName || 'there' }}!</h3>
        <p>I know your health profile and can answer questions about your coverage, premiums, and claims.</p>

        <div class="profile-pills" *ngIf="currentUser">
          <span class="pill" *ngIf="currentUser.age">Age {{ currentUser.age }}</span>
          <span class="pill" *ngIf="currentUser.bmi">BMI {{ currentUser.bmi?.toFixed(1) }}</span>
          <span class="pill warn" *ngIf="currentUser.is_smoker">Smoker</span>
          <span class="pill green" *ngIf="patientConditions.length > 0">{{ patientConditions.length }} condition(s)</span>
        </div>

        <div class="suggestions">
          <button
            *ngFor="let q of suggestedQuestions"
            class="suggestion-btn"
            (click)="sendFollowUp(q)"
          >{{ q }}</button>
        </div>
      </div>

      <!-- Messages -->
      <div class="messages-area" #messagesContainer [class.hidden]="showSessions">
        <div
          *ngFor="let msg of messages"
          class="msg-row"
          [class.user]="msg.role === 'user'"
          [class.assistant]="msg.role === 'assistant'"
        >
          <div class="msg-avatar-sm" *ngIf="msg.role === 'assistant'">AI</div>

          <div class="bubble">
            <div *ngIf="msg.role === 'user'" class="bubble-text">{{ msg.content }}</div>
            <div
              *ngIf="msg.role === 'assistant'"
              class="bubble-text md"
              [innerHTML]="renderMarkdown(msg.content)"
            ></div>

            <div class="bubble-time">{{ msg.timestamp | date:'h:mm a' }}</div>

            <!-- Citations -->
            <div *ngIf="msg.role === 'assistant' && msg.citations && msg.citations.length > 0" class="citations-row">
              <button class="btn-cite" (click)="msg.showCitations = !msg.showCitations">
                {{ msg.showCitations ? '▲ Hide' : '▼ Sources' }} ({{ msg.citations.length }})
              </button>
              <div class="citations-list" *ngIf="msg.showCitations">
                <div *ngFor="let c of msg.citations" class="cite-card">
                  <strong>{{ c.policy_name }}</strong> — {{ c.section_title }}
                  <p>{{ c.excerpt }}</p>
                </div>
              </div>
            </div>

            <!-- Follow-ups -->
            <div *ngIf="msg.role === 'assistant' && msg.follow_up_questions && msg.follow_up_questions.length > 0" class="followups">
              <button
                *ngFor="let q of msg.follow_up_questions"
                class="followup-chip"
                (click)="sendFollowUp(q)"
              >{{ q }}</button>
            </div>
          </div>

          <div class="msg-avatar-sm user-av" *ngIf="msg.role === 'user'">{{ initials }}</div>
        </div>

        <!-- Typing indicator -->
        <div *ngIf="isLoading" class="msg-row assistant">
          <div class="msg-avatar-sm">AI</div>
          <div class="bubble loading-bubble">
            <span class="dot"></span><span class="dot"></span><span class="dot"></span>
          </div>
        </div>
      </div>

      <!-- Input bar -->
      <div class="input-bar" [class.hidden]="showSessions">
        <input
          type="text"
          [(ngModel)]="userInput"
          placeholder="Ask about your coverage..."
          (keydown.enter)="sendMessage()"
          [disabled]="isLoading"
        />
        <button class="send-btn" (click)="sendMessage()" [disabled]="!userInput.trim() || isLoading">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </div>

    </div>
  `,
  styles: [`
    /* ===== FAB ===== */
    .fab {
      position: fixed;
      bottom: 28px;
      right: 28px;
      z-index: 1100;
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 0 20px 0 16px;
      height: 52px;
      background: linear-gradient(135deg, #2563eb, #4f46e5);
      color: #fff;
      border: none;
      border-radius: 26px;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      box-shadow: 0 4px 20px rgba(37, 99, 235, 0.45);
      transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);

      &:hover { transform: scale(1.06); box-shadow: 0 6px 24px rgba(37, 99, 235, 0.55); }
      &.open { padding: 0; width: 52px; border-radius: 50%; }
      &.open .fab-label { display: none; }
    }

    .fab-label { white-space: nowrap; }

    /* ===== POPUP PANEL ===== */
    .chat-popup {
      position: fixed;
      bottom: 92px;
      right: 28px;
      z-index: 1099;
      width: 390px;
      height: 580px;
      background: #fff;
      border-radius: 16px;
      box-shadow: 0 12px 48px rgba(0, 0, 0, 0.18), 0 2px 8px rgba(0, 0, 0, 0.10);
      display: flex;
      flex-direction: column;
      overflow: hidden;
      transform: scale(0.85) translateY(20px);
      transform-origin: bottom right;
      opacity: 0;
      pointer-events: none;
      transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
    }

    .chat-popup.visible {
      transform: scale(1) translateY(0);
      opacity: 1;
      pointer-events: all;
    }

    /* ===== HEADER ===== */
    .popup-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px 14px;
      background: linear-gradient(135deg, #1e3a5f, #1a2d4a);
      color: #fff;
      flex-shrink: 0;
    }

    .header-left { display: flex; align-items: center; gap: 10px; }

    .header-avatar {
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background: linear-gradient(135deg, #3b82f6, #6366f1);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
      font-weight: 700;
      flex-shrink: 0;
    }

    .header-title { font-size: 14px; font-weight: 600; color: #f1f5f9; }
    .header-sub { font-size: 11px; color: #94a3b8; margin-top: 1px; }

    .header-actions { display: flex; align-items: center; gap: 6px; }

    .btn-icon {
      width: 30px;
      height: 30px;
      border-radius: 6px;
      border: none;
      background: rgba(255,255,255,0.08);
      color: #cbd5e1;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: background 0.15s;

      &:hover { background: rgba(255,255,255,0.18); color: #fff; }
      &.active { background: rgba(59, 130, 246, 0.4); color: #93c5fd; }
    }

    /* ===== SESSIONS DRAWER ===== */
    .sessions-drawer {
      background: #1a2332;
      overflow: hidden;
      max-height: 0;
      transition: max-height 0.3s ease;
      flex-shrink: 0;
    }

    .sessions-drawer.open { max-height: 220px; overflow-y: auto; }

    .drawer-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 10px 14px;
      border-bottom: 1px solid #243044;
      font-size: 12px;
      font-weight: 600;
      color: #94a3b8;
      text-transform: uppercase;
      letter-spacing: 0.6px;
    }

    .btn-new-chat {
      font-size: 12px;
      padding: 4px 10px;
      background: #3b82f6;
      color: #fff;
      border: none;
      border-radius: 5px;
      cursor: pointer;
      font-weight: 500;

      &:hover { background: #2563eb; }
    }

    .session-list {
      list-style: none;
      margin: 0;
      padding: 6px;
    }

    .session-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 10px;
      border-radius: 6px;
      cursor: pointer;
      transition: background 0.15s;
      gap: 8px;

      &:hover { background: #243044; }
      &.active { background: #2563eb; }
    }

    .session-title {
      font-size: 12px;
      color: #e2e8f0;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      flex: 1;
    }

    .session-date { font-size: 11px; color: #64748b; flex-shrink: 0; }
    .session-item.active .session-date { color: rgba(255,255,255,0.65); }

    .no-sessions {
      font-size: 12px;
      color: #64748b;
      text-align: center;
      padding: 12px;
    }

    /* ===== WELCOME ===== */
    .welcome-screen {
      flex: 1;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 20px 16px;
      text-align: center;
      overflow-y: auto;
      background: #f8fafc;
    }

    .welcome-avatar {
      width: 56px;
      height: 56px;
      border-radius: 50%;
      background: linear-gradient(135deg, #3b82f6, #6366f1);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 18px;
      font-weight: 700;
      color: #fff;
      margin: 0 auto 12px;
      box-shadow: 0 6px 18px rgba(59, 130, 246, 0.3);
    }

    .welcome-screen h3 {
      margin: 0 0 6px;
      font-size: 18px;
      font-weight: 700;
      color: #1e293b;
    }

    .welcome-screen p {
      font-size: 13px;
      color: #64748b;
      line-height: 1.5;
      margin: 0 0 14px;
      max-width: 280px;
    }

    .profile-pills {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      justify-content: center;
      margin-bottom: 16px;
    }

    .pill {
      font-size: 11px;
      padding: 3px 10px;
      background: #e0e7ff;
      color: #3730a3;
      border-radius: 12px;
      font-weight: 500;
    }

    .pill.warn { background: #fee2e2; color: #991b1b; }
    .pill.green { background: #d1fae5; color: #065f46; }

    .suggestions {
      display: flex;
      flex-direction: column;
      gap: 7px;
      width: 100%;
      max-width: 320px;
    }

    .suggestion-btn {
      padding: 9px 14px;
      background: #fff;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      font-size: 12px;
      color: #1e293b;
      text-align: left;
      cursor: pointer;
      transition: all 0.15s;
      line-height: 1.4;

      &:hover {
        background: #eff6ff;
        border-color: #bfdbfe;
        color: #1d4ed8;
        transform: translateX(2px);
      }
    }

    /* ===== MESSAGES ===== */
    .messages-area {
      flex: 1;
      overflow-y: auto;
      padding: 14px 12px;
      display: flex;
      flex-direction: column;
      gap: 14px;
      background: #f8fafc;
    }

    .messages-area.hidden { display: none; }

    .msg-row {
      display: flex;
      align-items: flex-end;
      gap: 7px;

      &.user { justify-content: flex-end; }
    }

    .msg-avatar-sm {
      width: 28px;
      height: 28px;
      border-radius: 50%;
      background: linear-gradient(135deg, #3b82f6, #6366f1);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 10px;
      font-weight: 700;
      color: #fff;
      flex-shrink: 0;
    }

    .user-av { background: linear-gradient(135deg, #10b981, #059669); }

    .bubble {
      max-width: 78%;
      padding: 10px 13px;
      border-radius: 14px;
      font-size: 13px;
      line-height: 1.55;
      word-wrap: break-word;
    }

    .msg-row.user .bubble {
      background: linear-gradient(135deg, #3b82f6, #2563eb);
      color: #fff;
      border-bottom-right-radius: 4px;
    }

    .msg-row.assistant .bubble {
      background: #fff;
      color: #1e293b;
      border-bottom-left-radius: 4px;
      box-shadow: 0 1px 4px rgba(0, 0, 0, 0.07);
      border: 1px solid #e8edf3;
    }

    .bubble-text { white-space: pre-wrap; }
    .md { white-space: normal; }

    .bubble-time {
      font-size: 9px;
      color: #94a3b8;
      margin-top: 4px;
      text-align: right;
    }

    .msg-row.user .bubble-time { color: rgba(255,255,255,0.55); }

    /* Loading */
    .loading-bubble {
      display: flex;
      gap: 4px;
      padding: 12px 14px;
      align-items: center;
    }

    .dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: #94a3b8;
      animation: bounce 1.4s infinite ease-in-out both;
    }

    .dot:nth-child(1) { animation-delay: -0.32s; }
    .dot:nth-child(2) { animation-delay: -0.16s; }

    @keyframes bounce {
      0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
      40% { transform: scale(1); opacity: 1; }
    }

    /* Citations */
    .citations-row { margin-top: 8px; border-top: 1px solid #e8edf3; padding-top: 6px; }

    .btn-cite {
      background: none;
      border: none;
      color: #3b82f6;
      font-size: 11px;
      cursor: pointer;
      padding: 0;
      font-weight: 500;
      &:hover { text-decoration: underline; }
    }

    .citations-list { margin-top: 7px; display: flex; flex-direction: column; gap: 6px; }

    .cite-card {
      background: #fffbeb;
      border: 1px solid #fde68a;
      border-radius: 6px;
      padding: 7px 9px;
      font-size: 11px;
      color: #78716c;

      strong { color: #92400e; display: block; margin-bottom: 3px; }
      p { margin: 4px 0 0; font-style: italic; line-height: 1.45; }
    }

    /* Follow-ups */
    .followups {
      margin-top: 8px;
      display: flex;
      flex-wrap: wrap;
      gap: 5px;
    }

    .followup-chip {
      padding: 4px 10px;
      background: #eff6ff;
      color: #1d4ed8;
      border: 1px solid #bfdbfe;
      border-radius: 12px;
      font-size: 11px;
      cursor: pointer;
      transition: all 0.15s;
      font-weight: 500;
      text-align: left;

      &:hover { background: #dbeafe; }
    }

    /* ===== INPUT BAR ===== */
    .input-bar {
      display: flex;
      gap: 8px;
      padding: 10px 12px;
      border-top: 1px solid #e8edf3;
      background: #fff;
      align-items: center;
      flex-shrink: 0;
    }

    .input-bar.hidden { display: none; }

    .input-bar input {
      flex: 1;
      padding: 9px 13px;
      border: 1.5px solid #e2e8f0;
      border-radius: 8px;
      font-size: 13px;
      outline: none;
      background: #f8fafc;
      transition: border-color 0.2s, box-shadow 0.2s;

      &:focus {
        border-color: #3b82f6;
        background: #fff;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.08);
      }

      &:disabled { opacity: 0.6; }
    }

    .send-btn {
      width: 38px;
      height: 38px;
      border-radius: 8px;
      border: none;
      background: #3b82f6;
      color: #fff;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      transition: background 0.2s, transform 0.1s;

      &:hover:not(:disabled) { background: #2563eb; transform: scale(1.08); }
      &:disabled { background: #93c5fd; cursor: not-allowed; }
    }
  `]
})
export class ChatComponent implements OnInit, AfterViewChecked {
  @ViewChild('messagesContainer') private messagesContainer!: ElementRef;

  isOpen = false;
  showSessions = false;

  sessions: ChatSession[] = [];
  selectedSession: ChatSession | null = null;
  messages: ChatMessage[] = [];
  userInput = '';
  isLoading = false;
  private shouldScrollToBottom = false;

  constructor(
    private apiService: ApiService,
    private authService: AuthService,
    private sanitizer: DomSanitizer
  ) {}

  get currentUser(): any {
    return this.authService.currentUser();
  }

  get initials(): string {
    const name = this.currentUser?.full_name || '';
    return name.split(' ').map((n: string) => n[0]).join('').substring(0, 2).toUpperCase();
  }

  get firstName(): string {
    return (this.currentUser?.full_name || '').split(' ')[0];
  }

  get patientConditions(): string[] {
    const raw = this.currentUser?.pre_existing_conditions;
    if (!raw) return [];
    if (Array.isArray(raw)) return raw;
    try { return JSON.parse(raw); } catch { return []; }
  }

  get suggestedQuestions(): string[] {
    const questions: string[] = [];
    const conditions = this.patientConditions;

    if (conditions.length > 0) {
      questions.push(`Am I covered for ${conditions[0]}?`);
      if (conditions.length > 1) {
        questions.push(`Waiting period for ${conditions[1]}?`);
      }
    }

    if (this.currentUser?.is_smoker) {
      questions.push('How does smoking affect my premium?');
    }

    questions.push('What is my monthly premium?');
    questions.push('What services are covered?');

    return questions.slice(0, 5);
  }

  ngOnInit(): void {
    this.loadSessions();
    this.authService.loadUser();
  }

  ngAfterViewChecked(): void {
    if (this.shouldScrollToBottom) {
      this.scrollToBottom();
      this.shouldScrollToBottom = false;
    }
  }

  toggleChat(): void {
    this.isOpen = !this.isOpen;
    if (this.isOpen) {
      this.showSessions = false;
      setTimeout(() => this.scrollToBottom(), 50);
    }
  }

  renderMarkdown(text: string): SafeHtml {
    let html = text
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*([^*\n]+)\*/g, '<em>$1</em>')
      .replace(/^- (.+)$/gm, '<li>$1</li>')
      .replace(/(<li>[\s\S]*?<\/li>\n?)+/g, (m) => `<ul style="margin:5px 0 5px 16px;padding:0;">${m}</ul>`)
      .replace(/\n\n/g, '<br><br>')
      .replace(/\n/g, '<br>');

    return this.sanitizer.bypassSecurityTrustHtml(html);
  }

  loadSessions(): void {
    this.apiService.get<ChatSession[]>('/chat/sessions').subscribe({
      next: (sessions) => { this.sessions = sessions; },
      error: () => {}
    });
  }

  selectSession(session: ChatSession): void {
    this.selectedSession = session;
    this.apiService.get<ChatMessage[]>(`/chat/sessions/${session.id}/messages`).subscribe({
      next: (messages) => {
        this.messages = messages.map((msg) => ({ ...msg, showCitations: false, timestamp: new Date() }));
        this.shouldScrollToBottom = true;
      },
      error: () => {}
    });
  }

  startNewChat(): void {
    this.selectedSession = null;
    this.messages = [];
    this.userInput = '';
    this.showSessions = false;
  }

  sendMessage(): void {
    const text = this.userInput.trim();
    if (!text || this.isLoading) return;

    this.messages.push({ role: 'user', content: text, timestamp: new Date() });
    this.userInput = '';
    this.isLoading = true;
    this.shouldScrollToBottom = true;

    const payload: any = { message: text };
    if (this.selectedSession) payload.session_id = this.selectedSession.id;

    this.apiService.post<ChatResponse>('/chat', payload).subscribe({
      next: (response) => {
        if (!this.selectedSession) {
          this.selectedSession = {
            id: response.session_id,
            title: text.substring(0, 40),
            created_at: new Date().toISOString(),
          };
          this.sessions.unshift(this.selectedSession);
        }

        this.messages.push({
          role: 'assistant',
          content: response.message,
          citations: response.citations,
          follow_up_questions: response.follow_up_questions,
          showCitations: false,
          timestamp: new Date(),
        });
        this.isLoading = false;
        this.shouldScrollToBottom = true;
      },
      error: () => {
        this.messages.push({ role: 'assistant', content: 'Sorry, something went wrong. Please try again.', timestamp: new Date() });
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
        a.download = `report-${this.selectedSession!.id}.pdf`;
        a.click();
        window.URL.revokeObjectURL(url);
      },
      error: () => {}
    });
  }

  private scrollToBottom(): void {
    try {
      const el = this.messagesContainer?.nativeElement;
      if (el) el.scrollTop = el.scrollHeight;
    } catch {}
  }
}
