#!/usr/bin/env python3
"""
Smart Task Suggestions Module
AI-powered recommendations for task management optimization.
"""

from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics
import re
import random
from dataclasses import dataclass
import json

@dataclass
class TaskSuggestion:
    """Data class for task suggestions."""
    title: str
    description: str
    priority: str
    tags: List[str]
    confidence: float
    reasoning: str
    suggestion_type: str
    estimated_duration: Optional[str] = None
    due_date: Optional[str] = None

@dataclass
class BehaviorPattern:
    """Data class for user behavior patterns."""
    pattern_type: str
    description: str
    confidence: float
    data_points: int
    recommendations: List[str]

class SmartSuggestions:
    def __init__(self, vector_memory):
        """Initialize the smart suggestions module."""
        self.memory = vector_memory
        self.suggestion_templates = self._load_suggestion_templates()
        self.behavior_patterns = []
        
    def _load_suggestion_templates(self) -> Dict:
        """Load suggestion templates for different scenarios."""
        return {
            'productivity_boost': [
                "Complete {count} quick tasks to build momentum",
                "Focus on {priority} priority tasks first",
                "Break down complex tasks into smaller subtasks",
                "Schedule focused work sessions for {duration} minutes"
            ],
            'time_management': [
                "Set time blocks for {task_type} tasks",
                "Use the Pomodoro technique for {task_type}",
                "Batch similar tasks together",
                "Schedule breaks between intensive tasks"
            ],
            'priority_optimization': [
                "Review and reprioritize {count} tasks",
                "Consider deadline proximity for priority setting",
                "Balance urgent vs important tasks",
                "Delegate low-priority tasks if possible"
            ],
            'workflow_improvement': [
                "Create templates for recurring {task_type} tasks",
                "Standardize your task naming convention",
                "Use consistent tagging for better organization",
                "Implement a daily review routine"
            ]
        }
    
    def get_smart_suggestions(self, limit: int = 5) -> List[TaskSuggestion]:
        """Get AI-powered task suggestions based on user behavior and patterns."""
        tasks = self.memory.get_all_tasks()
        
        if not tasks:
            return self._get_onboarding_suggestions()
        
        suggestions = []
        
        # Analyze user behavior patterns
        patterns = self._analyze_behavior_patterns(tasks)
        self.behavior_patterns = patterns
        
        # Generate contextual suggestions
        suggestions.extend(self._generate_contextual_suggestions(tasks, patterns))
        
        # Generate task completion suggestions
        suggestions.extend(self._generate_completion_suggestions(tasks))
        
        # Generate optimization suggestions
        suggestions.extend(self._generate_optimization_suggestions(tasks, patterns))
        
        # Generate proactive suggestions
        suggestions.extend(self._generate_proactive_suggestions(tasks))
        
        # Sort by confidence and return top suggestions
        suggestions.sort(key=lambda x: x.confidence, reverse=True)
        return suggestions[:limit]
    
    def _get_onboarding_suggestions(self) -> List[TaskSuggestion]:
        """Get suggestions for new users."""
        return [
            TaskSuggestion(
                title="Create your first task",
                description="Start by adding a simple task to get familiar with the system",
                priority="medium",
                tags=["getting-started"],
                confidence=0.95,
                reasoning="New user detected - need to create first task",
                suggestion_type="onboarding"
            ),
            TaskSuggestion(
                title="Set up your workspace",
                description="Organize your tasks with tags like 'work', 'personal', 'urgent'",
                priority="medium",
                tags=["organization", "setup"],
                confidence=0.90,
                reasoning="Help user establish good organizational habits",
                suggestion_type="onboarding"
            ),
            TaskSuggestion(
                title="Add a high-priority task",
                description="Practice setting priorities to manage your workload effectively",
                priority="high",
                tags=["priority", "practice"],
                confidence=0.85,
                reasoning="Teach priority management early",
                suggestion_type="onboarding"
            )
        ]
    
    def _analyze_behavior_patterns(self, tasks: List[Dict]) -> List[BehaviorPattern]:
        """Analyze user behavior patterns from task data."""
        patterns = []
        
        if not tasks:
            return patterns
        
        # Pattern 1: Task creation frequency
        creation_pattern = self._analyze_creation_pattern(tasks)
        if creation_pattern:
            patterns.append(creation_pattern)
        
        # Pattern 2: Priority distribution
        priority_pattern = self._analyze_priority_pattern(tasks)
        if priority_pattern:
            patterns.append(priority_pattern)
        
        # Pattern 3: Completion patterns
        completion_pattern = self._analyze_completion_pattern(tasks)
        if completion_pattern:
            patterns.append(completion_pattern)
        
        # Pattern 4: Tag usage patterns
        tag_pattern = self._analyze_tag_pattern(tasks)
        if tag_pattern:
            patterns.append(tag_pattern)
        
        # Pattern 5: Time-based patterns
        time_pattern = self._analyze_time_pattern(tasks)
        if time_pattern:
            patterns.append(time_pattern)
        
        return patterns
    
    def _analyze_creation_pattern(self, tasks: List[Dict]) -> Optional[BehaviorPattern]:
        """Analyze task creation patterns."""
        if len(tasks) < 3:
            return None
        
        # Group tasks by creation date
        daily_creation = defaultdict(int)
        for task in tasks:
            try:
                created = datetime.fromisoformat(task['created_at']).date()
                daily_creation[created] += 1
            except:
                continue
        
        if not daily_creation:
            return None
        
        avg_daily = statistics.mean(daily_creation.values())
        max_daily = max(daily_creation.values())
        
        if max_daily > avg_daily * 2:
            return BehaviorPattern(
                pattern_type="burst_creation",
                description=f"You tend to create tasks in bursts (up to {max_daily} per day)",
                confidence=0.8,
                data_points=len(daily_creation),
                recommendations=[
                    "Consider spreading task creation throughout the day",
                    "Use task templates for common activities",
                    "Batch planning sessions for better organization"
                ]
            )
        
        return None
    
    def _analyze_priority_pattern(self, tasks: List[Dict]) -> Optional[BehaviorPattern]:
        """Analyze priority distribution patterns."""
        priority_counts = Counter(task['priority'] for task in tasks)
        total = len(tasks)
        
        if total < 5:
            return None
        
        high_ratio = priority_counts.get('high', 0) / total
        low_ratio = priority_counts.get('low', 0) / total
        
        if high_ratio > 0.6:
            return BehaviorPattern(
                pattern_type="high_priority_heavy",
                description=f"You mark {high_ratio:.1%} of tasks as high priority",
                confidence=0.85,
                data_points=total,
                recommendations=[
                    "Consider if all tasks truly need high priority",
                    "Use medium priority for important but not urgent tasks",
                    "Review priority criteria to avoid priority inflation"
                ]
            )
        elif low_ratio > 0.7:
            return BehaviorPattern(
                pattern_type="low_priority_heavy",
                description=f"You mark {low_ratio:.1%} of tasks as low priority",
                confidence=0.85,
                data_points=total,
                recommendations=[
                    "Review if some tasks could be higher priority",
                    "Consider delegating or removing very low priority tasks",
                    "Focus on medium priority tasks for better balance"
                ]
            )
        
        return None
    
    def _analyze_completion_pattern(self, tasks: List[Dict]) -> Optional[BehaviorPattern]:
        """Analyze task completion patterns."""
        completed_tasks = [t for t in tasks if t.get('completed', False)]
        pending_tasks = [t for t in tasks if not t.get('completed', False)]
        
        if not completed_tasks or not pending_tasks:
            return None
        
        completion_rate = len(completed_tasks) / len(tasks)
        
        # Analyze completion time patterns
        completion_times = []
        for task in completed_tasks:
            try:
                created = datetime.fromisoformat(task['created_at'])
                updated = datetime.fromisoformat(task.get('updated_at', task['created_at']))
                completion_time = (updated - created).total_seconds() / 3600  # hours
                completion_times.append(completion_time)
            except:
                continue
        
        if completion_times:
            avg_completion_time = statistics.mean(completion_times)
            
            if completion_rate < 0.3:
                return BehaviorPattern(
                    pattern_type="low_completion_rate",
                    description=f"Your task completion rate is {completion_rate:.1%}",
                    confidence=0.9,
                    data_points=len(tasks),
                    recommendations=[
                        "Break down large tasks into smaller subtasks",
                        "Set realistic deadlines for better motivation",
                        "Focus on completing 1-3 tasks per day",
                        "Review and remove tasks that are no longer relevant"
                    ]
                )
            elif avg_completion_time > 72:  # More than 3 days
                return BehaviorPattern(
                    pattern_type="slow_completion",
                    description=f"Tasks take an average of {avg_completion_time:.1f} hours to complete",
                    confidence=0.8,
                    data_points=len(completion_times),
                    recommendations=[
                        "Set shorter time blocks for task completion",
                        "Use time tracking to identify bottlenecks",
                        "Consider if tasks are too complex",
                        "Implement the 2-minute rule for quick tasks"
                    ]
                )
        
        return None
    
    def _analyze_tag_pattern(self, tasks: List[Dict]) -> Optional[BehaviorPattern]:
        """Analyze tag usage patterns."""
        tagged_tasks = [t for t in tasks if t.get('tags')]
        
        if len(tagged_tasks) < 3:
            return None
        
        tag_usage_rate = len(tagged_tasks) / len(tasks)
        
        if tag_usage_rate < 0.3:
            return BehaviorPattern(
                pattern_type="low_tag_usage",
                description=f"Only {tag_usage_rate:.1%} of tasks have tags",
                confidence=0.75,
                data_points=len(tasks),
                recommendations=[
                    "Use tags to categorize tasks by project or context",
                    "Create consistent tag naming conventions",
                    "Tag tasks to improve search and filtering",
                    "Use tags for better task organization"
                ]
            )
        
        # Analyze tag diversity
        all_tags = []
        for task in tagged_tasks:
            all_tags.extend(task['tags'])
        
        unique_tags = len(set(all_tags))
        if unique_tags > 20:
            return BehaviorPattern(
                pattern_type="high_tag_diversity",
                description=f"You use {unique_tags} different tags",
                confidence=0.7,
                data_points=len(tagged_tasks),
                recommendations=[
                    "Consider consolidating similar tags",
                    "Create a tag hierarchy for better organization",
                    "Review and remove unused tags",
                    "Standardize tag naming conventions"
                ]
            )
        
        return None
    
    def _analyze_time_pattern(self, tasks: List[Dict]) -> Optional[BehaviorPattern]:
        """Analyze time-based patterns."""
        # Analyze due date patterns
        tasks_with_due_dates = [t for t in tasks if t.get('due_date')]
        
        if len(tasks_with_due_dates) < 3:
            return None
        
        overdue_tasks = []
        for task in tasks_with_due_dates:
            try:
                due_date = datetime.strptime(task['due_date'], '%Y-%m-%d').date()
                if due_date < datetime.now().date() and not task.get('completed', False):
                    overdue_tasks.append(task)
            except:
                continue
        
        overdue_rate = len(overdue_tasks) / len(tasks_with_due_dates)
        
        if overdue_rate > 0.3:
            return BehaviorPattern(
                pattern_type="frequent_overdue",
                description=f"{overdue_rate:.1%} of tasks with due dates are overdue",
                confidence=0.85,
                data_points=len(tasks_with_due_dates),
                recommendations=[
                    "Set more realistic due dates",
                    "Add buffer time to your estimates",
                    "Review and adjust deadlines regularly",
                    "Consider using time estimates instead of just due dates"
                ]
            )
        
        return None
    
    def _generate_contextual_suggestions(self, tasks: List[Dict], patterns: List[BehaviorPattern]) -> List[TaskSuggestion]:
        """Generate contextual suggestions based on behavior patterns."""
        suggestions = []
        
        for pattern in patterns:
            if pattern.pattern_type == "low_completion_rate":
                suggestions.append(TaskSuggestion(
                    title="Create a daily focus list",
                    description="Select 3 most important tasks for today and focus on completing them",
                    priority="high",
                    tags=["productivity", "focus"],
                    confidence=0.9,
                    reasoning="Low completion rate detected - need to improve focus",
                    suggestion_type="productivity_boost"
                ))
            
            elif pattern.pattern_type == "high_priority_heavy":
                suggestions.append(TaskSuggestion(
                    title="Review and reprioritize tasks",
                    description="Go through your high-priority tasks and identify which can be medium priority",
                    priority="medium",
                    tags=["organization", "priority"],
                    confidence=0.85,
                    reasoning="Too many high-priority tasks detected",
                    suggestion_type="priority_optimization"
                ))
            
            elif pattern.pattern_type == "frequent_overdue":
                suggestions.append(TaskSuggestion(
                    title="Set up a weekly planning session",
                    description="Dedicate 30 minutes each week to review and adjust task deadlines",
                    priority="medium",
                    tags=["planning", "time-management"],
                    confidence=0.8,
                    reasoning="Frequent overdue tasks detected",
                    suggestion_type="time_management"
                ))
        
        return suggestions
    
    def _generate_completion_suggestions(self, tasks: List[Dict]) -> List[TaskSuggestion]:
        """Generate suggestions for task completion."""
        suggestions = []
        
        # Find quick wins (low priority, simple tasks)
        quick_wins = [t for t in tasks if not t.get('completed', False) and 
                     t.get('priority') == 'low' and 
                     len(t.get('description', '')) < 50]
        
        if quick_wins:
            suggestions.append(TaskSuggestion(
                title=f"Complete {min(3, len(quick_wins))} quick tasks",
                description="Focus on simple, low-priority tasks to build momentum",
                priority="low",
                tags=["momentum", "quick-wins"],
                confidence=0.8,
                reasoning=f"Found {len(quick_wins)} potential quick wins",
                suggestion_type="productivity_boost"
            ))
        
        # Find overdue tasks
        overdue_tasks = []
        for task in tasks:
            if not task.get('completed', False) and task.get('due_date'):
                try:
                    due_date = datetime.strptime(task['due_date'], '%Y-%m-%d').date()
                    if due_date < datetime.now().date():
                        overdue_tasks.append(task)
                except:
                    continue
        
        if overdue_tasks:
            suggestions.append(TaskSuggestion(
                title=f"Address {len(overdue_tasks)} overdue tasks",
                description="Review and either complete, reschedule, or remove overdue tasks",
                priority="high",
                tags=["overdue", "cleanup"],
                confidence=0.9,
                reasoning=f"Found {len(overdue_tasks)} overdue tasks",
                suggestion_type="priority_optimization"
            ))
        
        return suggestions
    
    def _generate_optimization_suggestions(self, tasks: List[Dict], patterns: List[BehaviorPattern]) -> List[TaskSuggestion]:
        """Generate workflow optimization suggestions."""
        suggestions = []
        
        # Analyze task complexity
        complex_tasks = [t for t in tasks if len(t.get('description', '')) > 100]
        if complex_tasks:
            suggestions.append(TaskSuggestion(
                title="Break down complex tasks",
                description="Split large tasks into smaller, manageable subtasks",
                priority="medium",
                tags=["optimization", "complexity"],
                confidence=0.75,
                reasoning=f"Found {len(complex_tasks)} complex tasks that could be simplified",
                suggestion_type="workflow_improvement"
            ))
        
        # Analyze tag consistency
        all_tags = []
        for task in tasks:
            if task.get('tags'):
                all_tags.extend(task['tags'])
        
        if all_tags:
            tag_counts = Counter(all_tags)
            most_common = tag_counts.most_common(1)[0]
            
            suggestions.append(TaskSuggestion(
                title=f"Focus on {most_common[0]} tasks",
                description=f"You have {most_common[1]} tasks tagged with '{most_common[0]}' - consider batching them",
                priority="medium",
                tags=["batching", "focus"],
                confidence=0.7,
                reasoning=f"Most common tag: {most_common[0]} with {most_common[1]} tasks",
                suggestion_type="productivity_boost"
            ))
        
        return suggestions
    
    def _generate_proactive_suggestions(self, tasks: List[Dict]) -> List[TaskSuggestion]:
        """Generate proactive suggestions based on task patterns."""
        suggestions = []
        
        # Suggest recurring task templates
        task_titles = [t['title'].lower() for t in tasks]
        common_words = []
        for title in task_titles:
            words = re.findall(r'\b\w+\b', title)
            common_words.extend(words)
        
        word_counts = Counter(common_words)
        common_activities = [word for word, count in word_counts.most_common(10) 
                           if count > 2 and len(word) > 3]
        
        if common_activities:
            activity = common_activities[0]
            suggestions.append(TaskSuggestion(
                title=f"Create template for {activity} tasks",
                description=f"Since you frequently create tasks involving '{activity}', consider creating a template",
                priority="low",
                tags=["template", "efficiency"],
                confidence=0.6,
                reasoning=f"'{activity}' appears in {word_counts[activity]} task titles",
                suggestion_type="workflow_improvement"
            ))
        
        # Suggest time blocking
        high_priority_pending = [t for t in tasks if not t.get('completed', False) and t.get('priority') == 'high']
        if len(high_priority_pending) > 3:
            suggestions.append(TaskSuggestion(
                title="Schedule focused time blocks",
                description="Block 2-3 hours for your high-priority tasks to ensure completion",
                priority="high",
                tags=["time-blocking", "focus"],
                confidence=0.8,
                reasoning=f"You have {len(high_priority_pending)} high-priority pending tasks",
                suggestion_type="time_management"
            ))
        
        return suggestions
    
    def get_behavior_insights(self) -> List[Dict]:
        """Get insights about user behavior patterns."""
        insights = []
        
        for pattern in self.behavior_patterns:
            insights.append({
                'type': pattern.pattern_type,
                'description': pattern.description,
                'confidence': pattern.confidence,
                'recommendations': pattern.recommendations,
                'data_points': pattern.data_points
            })
        
        return insights
    
    def get_productivity_score(self) -> Dict:
        """Calculate a productivity score based on various metrics."""
        tasks = self.memory.get_all_tasks()
        
        if not tasks:
            return {'score': 0, 'level': 'Beginner', 'message': 'No tasks to analyze'}
        
        # Calculate various metrics
        completion_rate = len([t for t in tasks if t.get('completed', False)]) / len(tasks)
        
        # Priority balance score
        priority_counts = Counter(t['priority'] for t in tasks)
        total = len(tasks)
        priority_balance = 1 - abs(priority_counts.get('high', 0) / total - 0.3)  # Ideal: 30% high priority
        
        # Tag usage score
        tagged_tasks = len([t for t in tasks if t.get('tags')])
        tag_score = tagged_tasks / len(tasks)
        
        # Due date adherence score
        tasks_with_due_dates = [t for t in tasks if t.get('due_date')]
        if tasks_with_due_dates:
            overdue_count = 0
            for task in tasks_with_due_dates:
                try:
                    due_date = datetime.strptime(task['due_date'], '%Y-%m-%d').date()
                    if due_date < datetime.now().date() and not task.get('completed', False):
                        overdue_count += 1
                except:
                    continue
            due_date_score = 1 - (overdue_count / len(tasks_with_due_dates))
        else:
            due_date_score = 0.5  # Neutral score if no due dates
        
        # Calculate overall score
        overall_score = (completion_rate * 0.4 + 
                        priority_balance * 0.2 + 
                        tag_score * 0.2 + 
                        due_date_score * 0.2) * 100
        
        # Determine level
        if overall_score >= 80:
            level = "Expert"
        elif overall_score >= 60:
            level = "Advanced"
        elif overall_score >= 40:
            level = "Intermediate"
        else:
            level = "Beginner"
        
        return {
            'score': round(overall_score, 1),
            'level': level,
            'completion_rate': round(completion_rate * 100, 1),
            'priority_balance': round(priority_balance * 100, 1),
            'tag_usage': round(tag_score * 100, 1),
            'due_date_adherence': round(due_date_score * 100, 1),
            'message': f"You're at {level} level with {overall_score:.1f}% productivity score"
        }
    
    def get_next_actions(self, limit: int = 3) -> List[Dict]:
        """Get recommended next actions based on current task state."""
        tasks = self.memory.get_all_tasks()
        
        if not tasks:
            return [{'action': 'Create your first task', 'priority': 'high', 'reasoning': 'Get started with task management'}]
        
        actions = []
        
        # Check for overdue tasks
        overdue_tasks = []
        for task in tasks:
            if not task.get('completed', False) and task.get('due_date'):
                try:
                    due_date = datetime.strptime(task['due_date'], '%Y-%m-%d').date()
                    if due_date < datetime.now().date():
                        overdue_tasks.append(task)
                except:
                    continue
        
        if overdue_tasks:
            actions.append({
                'action': f'Address {len(overdue_tasks)} overdue task(s)',
                'priority': 'high',
                'reasoning': 'Overdue tasks can create stress and reduce productivity'
            })
        
        # Check for high priority pending tasks
        high_priority_pending = [t for t in tasks if not t.get('completed', False) and t.get('priority') == 'high']
        if high_priority_pending:
            actions.append({
                'action': f'Focus on {len(high_priority_pending)} high-priority task(s)',
                'priority': 'high',
                'reasoning': 'High-priority tasks should be completed first'
            })
        
        # Suggest quick wins
        quick_wins = [t for t in tasks if not t.get('completed', False) and 
                     t.get('priority') == 'low' and 
                     len(t.get('description', '')) < 50]
        if quick_wins:
            actions.append({
                'action': f'Complete {min(3, len(quick_wins))} quick task(s)',
                'priority': 'medium',
                'reasoning': 'Quick wins build momentum and motivation'
            })
        
        # Suggest planning
        if len([t for t in tasks if not t.get('completed', False)]) > 10:
            actions.append({
                'action': 'Review and prioritize your task list',
                'priority': 'medium',
                'reasoning': 'Large number of pending tasks - need organization'
            })
        
        return actions[:limit] 