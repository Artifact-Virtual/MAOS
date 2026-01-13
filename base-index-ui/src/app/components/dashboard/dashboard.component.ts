import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';

interface IndexStats {
  totalFiles: number;
  totalSize: number;
  totalLOC: number;
  fileTypes: { [key: string]: number };
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  Object = Object; // Expose Object to template
  
  stats: IndexStats = {
    totalFiles: 1247,
    totalSize: 45230000,
    totalLOC: 128456,
    fileTypes: {
      'Python': 423,
      'TypeScript': 312,
      'JavaScript': 245,
      'HTML': 134,
      'CSS': 89,
      'JSON': 44
    }
  };

  viewMode = 'grid';
  complexityData = [
    { path: 'src/core/engine.py', complexity: 85, loc: 1250, color: 'high' },
    { path: 'src/api/routes.py', complexity: 72, loc: 980, color: 'high' },
    { path: 'src/ui/dashboard.ts', complexity: 58, loc: 756, color: 'medium' },
    { path: 'src/utils/helpers.py', complexity: 35, loc: 420, color: 'low' },
    { path: 'src/models/base.py', complexity: 42, loc: 512, color: 'medium' }
  ];

  ngOnInit(): void {
    console.log('Dashboard initialized');
  }

  getFileTypeKeys(): string[] {
    return Object.keys(this.stats.fileTypes);
  }

  getSizeInMB(): string {
    return (this.stats.totalSize / (1024 * 1024)).toFixed(2);
  }

  getFileTypeColor(type: string): string {
    const colors: {[key: string]: string} = {
      'Python': '#3776ab',
      'TypeScript': '#3178c6',
      'JavaScript': '#f7df1e',
      'HTML': '#e34c26',
      'CSS': '#1572b6',
      'JSON': '#292929'
    };
    return colors[type] || '#718096';
  }

  getComplexityClass(complexity: number): string {
    if (complexity >= 70) return 'high';
    if (complexity >= 40) return 'medium';
    return 'low';
  }

  changeView(mode: string): void {
    this.viewMode = mode;
  }
}
