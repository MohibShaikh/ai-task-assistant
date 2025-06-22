from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import statistics
from collections import defaultdict, Counter
import math

class TaskAnalytics:
    def __init__(self, vector_memory):
        """Initialize the analytics module with access to task data."""
        self.memory = vector_memory
    
    def get_comprehensive_stats(self) -> Dict:
        """Get comprehensive task statistics and insights."""
        tasks = self.memory.get_all_tasks()
        
        if not tasks:
            return self._empty_stats()
        
        stats = {
            'basic_stats': self._get_basic_stats(tasks),
            'priority_analysis': self._analyze_priorities(tasks),
            'status_analysis': self._analyze_statuses(tasks),
            'tag_analysis': self._analyze_tags(tasks),
            'productivity_metrics': self._calculate_productivity_metrics(tasks),
            'trends': self._analyze_trends(tasks),
            'insights': self._generate_insights(tasks),
            'recommendations': self._generate_recommendations(tasks)
        }
        
        return stats
    
    def _empty_stats(self) -> Dict:
        """Return empty statistics structure."""
        return {
            'basic_stats': {'total_tasks': 0, 'message': 'No tasks found'},
            'priority_analysis': {},
            'status_analysis': {},
            'tag_analysis': {},
            'productivity_metrics': {},
            'trends': {},
            'insights': ['No tasks available for analysis'],
            'recommendations': ['Add some tasks to get started!']
        }
    
    def _get_basic_stats(self, tasks: List[Dict]) -> Dict:
        """Calculate basic task statistics."""
        total_tasks = len(tasks)
        
        # Calculate average task length
        title_lengths = [len(task['title']) for task in tasks]
        desc_lengths = [len(task.get('description', '')) for task in tasks]
        
        # Calculate creation dates
        creation_dates = []
        for task in tasks:
            try:
                created = datetime.fromisoformat(task['created_at'])
                creation_dates.append(created)
            except:
                pass
        
        stats = {
            'total_tasks': total_tasks,
            'avg_title_length': statistics.mean(title_lengths) if title_lengths else 0,
            'avg_description_length': statistics.mean(desc_lengths) if desc_lengths else 0,
            'tasks_with_descriptions': len([t for t in tasks if t.get('description')]),
            'tasks_with_tags': len([t for t in tasks if t.get('tags')]),
            'oldest_task_days': self._days_since_oldest(creation_dates),
            'newest_task_days': self._days_since_newest(creation_dates)
        }
        
        return stats
    
    def _analyze_priorities(self, tasks: List[Dict]) -> Dict:
        """Analyze task priorities."""
        priority_counts = Counter(task['priority'] for task in tasks)
        total = len(tasks)
        
        analysis = {
            'distribution': dict(priority_counts),
            'percentages': {priority: (count/total)*100 for priority, count in priority_counts.items()},
            'high_priority_ratio': priority_counts.get('high', 0) / total if total > 0 else 0,
            'priority_balance': self._calculate_priority_balance(priority_counts),
            'urgent_tasks': priority_counts.get('high', 0)
        }
        
        return analysis
    
    def _analyze_statuses(self, tasks: List[Dict]) -> Dict:
        """Analyze task statuses."""
        # Determine status from completed field if status is missing
        status_counts = Counter()
        for task in tasks:
            if task.get('completed', False):
                status = 'completed'
            else:
                status = task.get('status', 'pending')
            status_counts[status] += 1
            
        total = len(tasks)
        
        # Calculate completion rate
        completed = status_counts.get('completed', 0)
        completion_rate = (completed / total) * 100 if total > 0 else 0
        
        analysis = {
            'distribution': dict(status_counts),
            'percentages': {status: (count/total)*100 for status, count in status_counts.items()},
            'completion_rate': completion_rate,
            'pending_tasks': status_counts.get('pending', 0),
            'in_progress_tasks': status_counts.get('in_progress', 0),
            'completed_tasks': completed
        }
        
        return analysis
    
    def _analyze_tags(self, tasks: List[Dict]) -> Dict:
        """Analyze task tags."""
        all_tags = []
        for task in tasks:
            if task.get('tags'):
                all_tags.extend(task['tags'])
        
        tag_counts = Counter(all_tags)
        
        # Find most common tag combinations
        tag_combinations = []
        for task in tasks:
            if task.get('tags') and len(task['tags']) > 1:
                tag_combinations.append(tuple(sorted(task['tags'])))
        
        combination_counts = Counter(tag_combinations)
        
        analysis = {
            'total_unique_tags': len(tag_counts),
            'most_common_tags': tag_counts.most_common(5),
            'tag_usage_percentage': (len([t for t in tasks if t.get('tags')]) / len(tasks)) * 100 if tasks else 0,
            'most_common_combinations': combination_counts.most_common(3),
            'tag_diversity': len(tag_counts) / len(tasks) if tasks else 0
        }
        
        return analysis
    
    def _calculate_productivity_metrics(self, tasks: List[Dict]) -> Dict:
        """Calculate productivity-related metrics."""
        # Group tasks by creation date
        daily_tasks = defaultdict(list)
        for task in tasks:
            try:
                created = datetime.fromisoformat(task['created_at']).date()
                daily_tasks[created].append(task)
            except:
                pass
        
        # Calculate daily task creation rates
        if daily_tasks:
            daily_counts = [len(tasks) for tasks in daily_tasks.values()]
            avg_daily_tasks = statistics.mean(daily_counts)
            max_daily_tasks = max(daily_counts)
            min_daily_tasks = min(daily_counts)
        else:
            avg_daily_tasks = max_daily_tasks = min_daily_tasks = 0
        
        # Calculate task complexity (based on description length and tags)
        complexity_scores = []
        for task in tasks:
            score = 0
            if task.get('description'):
                score += len(task['description']) / 100  # Normalize description length
            if task.get('tags'):
                score += len(task['tags']) * 0.5  # Add points for tags
            if task['priority'] == 'high':
                score += 1
            complexity_scores.append(score)
        
        avg_complexity = statistics.mean(complexity_scores) if complexity_scores else 0
        
        metrics = {
            'avg_daily_tasks': avg_daily_tasks,
            'max_daily_tasks': max_daily_tasks,
            'min_daily_tasks': min_daily_tasks,
            'avg_task_complexity': avg_complexity,
            'total_days_active': len(daily_tasks),
            'productivity_score': self._calculate_productivity_score(tasks)
        }
        
        return metrics
    
    def _analyze_trends(self, tasks: List[Dict]) -> Dict:
        """Analyze trends over time."""
        # Group tasks by week
        weekly_tasks = defaultdict(list)
        for task in tasks:
            try:
                created = datetime.fromisoformat(task['created_at'])
                week_start = created - timedelta(days=created.weekday())
                week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
                weekly_tasks[week_start].append(task)
            except:
                pass
        
        # Calculate weekly trends
        weekly_counts = []
        weekly_priorities = defaultdict(list)
        
        for week_start, week_tasks in sorted(weekly_tasks.items()):
            weekly_counts.append(len(week_tasks))
            for task in week_tasks:
                weekly_priorities[week_start].append(task['priority'])
        
        # Calculate trend direction
        if len(weekly_counts) > 1:
            trend_direction = 'increasing' if weekly_counts[-1] > weekly_counts[0] else 'decreasing'
            trend_strength = abs(weekly_counts[-1] - weekly_counts[0]) / max(weekly_counts)
        else:
            trend_direction = 'stable'
            trend_strength = 0
        
        trends = {
            'weekly_task_counts': weekly_counts,
            'trend_direction': trend_direction,
            'trend_strength': trend_strength,
            'most_productive_week': max(weekly_counts) if weekly_counts else 0,
            'least_productive_week': min(weekly_counts) if weekly_counts else 0,
            'weekly_priority_trends': dict(weekly_priorities)
        }
        
        return trends
    
    def _generate_insights(self, tasks: List[Dict]) -> List[str]:
        """Generate actionable insights from task data."""
        insights = []
        
        # Priority insights
        priority_analysis = self._analyze_priorities(tasks)
        high_priority_ratio = priority_analysis['high_priority_ratio']
        
        if high_priority_ratio > 0.3:
            insights.append(f"⚠️  {high_priority_ratio*100:.1f}% of your tasks are high priority - consider delegating or breaking them down")
        elif high_priority_ratio < 0.1:
            insights.append("✅ Your priority distribution looks balanced")
        
        # Status insights
        status_analysis = self._analyze_statuses(tasks)
        completion_rate = status_analysis['completion_rate']
        
        if completion_rate < 20:
            insights.append("📈 Low completion rate - try focusing on smaller, achievable tasks")
        elif completion_rate > 80:
            insights.append("🎉 Excellent completion rate! Keep up the great work")
        
        # Tag insights
        tag_analysis = self._analyze_tags(tasks)
        if tag_analysis['tag_usage_percentage'] < 50:
            insights.append("🏷️  Consider using more tags to better organize your tasks")
        
        # Productivity insights
        productivity_metrics = self._calculate_productivity_metrics(tasks)
        if productivity_metrics['avg_daily_tasks'] > 10:
            insights.append("⚡ High daily task volume - consider batching similar tasks")
        
        # Trend insights
        trends = self._analyze_trends(tasks)
        if trends['trend_direction'] == 'increasing':
            insights.append("📊 Task volume is increasing - monitor your workload")
        elif trends['trend_direction'] == 'decreasing':
            insights.append("📉 Task volume is decreasing - good progress on clearing your backlog")
        
        return insights
    
    def _generate_recommendations(self, tasks: List[Dict]) -> List[str]:
        """Generate specific recommendations for improvement."""
        recommendations = []
        
        # Priority recommendations
        priority_analysis = self._analyze_priorities(tasks)
        high_priority_count = priority_analysis['urgent_tasks']
        
        if high_priority_count > 5:
            recommendations.append("🔴 You have many high-priority tasks. Try the Eisenhower Matrix to prioritize effectively")
        
        # Status recommendations
        status_analysis = self._analyze_statuses(tasks)
        pending_count = status_analysis['pending_tasks']
        
        if pending_count > 10:
            recommendations.append("⏳ Many pending tasks - consider time-blocking to tackle them systematically")
        
        # Tag recommendations
        tag_analysis = self._analyze_tags(tasks)
        if tag_analysis['total_unique_tags'] < 5:
            recommendations.append("🏷️  Create a tagging system (e.g., work, personal, urgent, learning) for better organization")
        
        # Productivity recommendations
        productivity_metrics = self._calculate_productivity_metrics(tasks)
        if productivity_metrics['avg_task_complexity'] > 2:
            recommendations.append("🔧 Complex tasks detected - break them into smaller, manageable subtasks")
        
        return recommendations
    
    def _calculate_priority_balance(self, priority_counts: Counter) -> str:
        """Calculate how balanced the priority distribution is."""
        total = sum(priority_counts.values())
        if total == 0:
            return "balanced"
        
        # Calculate entropy-like measure
        proportions = [count/total for count in priority_counts.values()]
        entropy = -sum(p * math.log2(p) for p in proportions if p > 0)
        max_entropy = math.log2(len(priority_counts))
        
        balance_ratio = entropy / max_entropy if max_entropy > 0 else 0
        
        if balance_ratio > 0.8:
            return "well_balanced"
        elif balance_ratio > 0.5:
            return "moderately_balanced"
        else:
            return "unbalanced"
    
    def _calculate_productivity_score(self, tasks: List[Dict]) -> float:
        """Calculate overall productivity score (0-100)."""
        if not tasks:
            return 0
        
        # Factors: completion rate, priority balance, task organization
        status_analysis = self._analyze_statuses(tasks)
        priority_analysis = self._analyze_priorities(tasks)
        tag_analysis = self._analyze_tags(tasks)
        
        completion_score = status_analysis['completion_rate']
        priority_score = 100 * (1 - priority_analysis['high_priority_ratio'])  # Lower high-priority ratio is better
        organization_score = tag_analysis['tag_usage_percentage']
        
        # Weighted average
        productivity_score = (completion_score * 0.5 + priority_score * 0.3 + organization_score * 0.2)
        
        return min(100, max(0, productivity_score))
    
    def _days_since_oldest(self, dates: List[datetime]) -> int:
        """Calculate days since the oldest task."""
        if not dates:
            return 0
        oldest = min(dates)
        return (datetime.now() - oldest).days
    
    def _days_since_newest(self, dates: List[datetime]) -> int:
        """Calculate days since the newest task."""
        if not dates:
            return 0
        newest = max(dates)
        return (datetime.now() - newest).days
    
    def get_weekly_report(self) -> Dict:
        """Generate a weekly productivity report."""
        tasks = self.memory.get_all_tasks()
        
        # Get tasks from the last 7 days
        week_ago = datetime.now() - timedelta(days=7)
        recent_tasks = [
            task for task in tasks
            if datetime.fromisoformat(task['created_at']) >= week_ago
        ]
        
        report = {
            'period': 'Last 7 days',
            'tasks_created': len(recent_tasks),
            'tasks_completed': len([t for t in recent_tasks if t['status'] == 'completed']),
            'completion_rate': (len([t for t in recent_tasks if t['status'] == 'completed']) / len(recent_tasks)) * 100 if recent_tasks else 0,
            'most_productive_day': self._find_most_productive_day(recent_tasks),
            'priority_distribution': Counter(t['priority'] for t in recent_tasks),
            'top_tags': Counter(tag for t in recent_tasks if t.get('tags') for tag in t['tags']).most_common(3)
        }
        
        return report
    
    def _find_most_productive_day(self, tasks: List[Dict]) -> str:
        """Find the day with the most tasks created."""
        if not tasks:
            return "No tasks"
        
        daily_counts = defaultdict(int)
        for task in tasks:
            try:
                day = datetime.fromisoformat(task['created_at']).strftime('%A')
                daily_counts[day] += 1
            except:
                pass
        
        if daily_counts:
            return max(daily_counts, key=daily_counts.get)
        return "Unknown" 