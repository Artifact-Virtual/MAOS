import { Component } from '@angular/core';
import { DashboardComponent } from './components/dashboard/dashboard.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [DashboardComponent],
  template: `
    <div class="app-container">
      <header class="app-header">
        <div class="header-content">
          <div class="logo">
            <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
              <rect width="40" height="40" rx="8" fill="url(#gradient)" />
              <path d="M12 20L18 26L28 14" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
              <defs>
                <linearGradient id="gradient" x1="0" y1="0" x2="40" y2="40">
                  <stop offset="0%" stop-color="#667eea" />
                  <stop offset="100%" stop-color="#764ba2" />
                </linearGradient>
              </defs>
            </svg>
            <h1>Base Index</h1>
          </div>
          <nav class="nav-menu">
            <a href="#" class="nav-link active">Dashboard</a>
            <a href="#" class="nav-link">Explorer</a>
            <a href="#" class="nav-link">Analytics</a>
            <a href="#" class="nav-link">Settings</a>
          </nav>
        </div>
      </header>

      <main class="app-main">
        <app-dashboard></app-dashboard>
      </main>

      <footer class="app-footer">
        <p>Base Index v2.0 - Production-Grade Code Intelligence Platform</p>
      </footer>
    </div>
  `,
  styleUrls: ['./app.scss']
})
export class AppComponent {
  title = 'Base Index - Code Intelligence Platform';
}
