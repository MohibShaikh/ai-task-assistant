#!/usr/bin/env python3
"""
AI Task Assistant with Vector Memory
A smart task management system using semantic search and vector embeddings.
"""

import os
from typing import List, Dict, Optional
from datetime import datetime
import uuid
import re
from colorama import Fore, Style
from dotenv import load_dotenv
load_dotenv()

# Import the appropriate memory system
try:
    from pinecone_memory import PineconeMemory
    USE_PINECONE = True
    print("🌐 Using Pinecone for vector storage")
except ImportError:
    USE_PINECONE = False
    print("💾 Using local FAISS for vector storage")

# Import other modules
from nlp_processor import NLPProcessor
from task_analytics import TaskAnalytics
from smart_suggestions import SmartSuggestions
from user_manager import UserManager

# Import vector memory (will be used by UserManager)
if not USE_PINECONE:
    from vector_memory import VectorMemory

class TaskAssistant:
    def __init__(self, user_id: str = "default"):
        """Initialize the AI Task Assistant with vector memory, NLP, analytics, and smart suggestions."""
        self.user_id = user_id
        self.user_manager = UserManager()
        self.memory = self.user_manager.get_user_vector_memory(user_id)
        
        # Initialize NLP processor with error handling
        try:
            self.nlp_processor = NLPProcessor()
        except Exception as e:
            print(f"⚠️ Failed to initialize NLP processor: {e}")
            self.nlp_processor = None
        
        self.analytics = TaskAnalytics(self.memory)
        self.suggestions = SmartSuggestions(self.memory)
        
        self.commands = {
            'add': self._add_task,
            'search': self._search_tasks,
            'list': self._list_tasks,
            'update': self._update_task,
            'delete': self._delete_task,
            'complete': self._complete_task,
            'stats': self._show_statistics,
            'analytics': self._show_analytics,
            'insights': self._show_insights,
            'weekly': self._show_weekly_report,
            'due': self._show_due_stats,
            'suggest': self._show_suggestions,
            'recommendations': self._show_suggestions,
            'help': self._show_help,
            'quit': lambda x: "Goodbye! Your tasks have been saved.",
            'exit': lambda x: "Goodbye! Your tasks have been saved."
        }
    
    def get_user_stats(self) -> Dict:
        """Get user-specific statistics."""
        return self.user_manager.get_user_stats(int(self.user_id))
    
    def switch_user(self, user_id: str):
        """Switch to a different user's data."""
        self.user_id = user_id
        self.memory = self.user_manager.get_user_vector_memory(user_id)
        self.analytics = TaskAnalytics(self.memory)
        self.suggestions = SmartSuggestions(self.memory)
    
    def process_command(self, user_input: str) -> str:
        """
        Process user input and return appropriate response.
        Now supports both traditional commands and natural language.
        
        Args:
            user_input: User's command input
            
        Returns:
            Response string
        """
        user_input = user_input.strip()
        if not user_input:
            return "Please enter a command. Type 'help' for available commands."
        
        # First, try to parse as natural language
        parsed_command = self.nlp_processor.parse_command(user_input)
        
        if parsed_command['command_type'] != 'unknown':
            return self._execute_nlp_command(parsed_command)
        
        # If NLP parsing fails, fall back to traditional command parsing
        return self._process_traditional_command(user_input)
    
    def _find_task_by_display_position(self, position: int) -> Optional[Dict]:
        """Find a task by its display position (1-indexed)."""
        tasks = self.memory.get_all_tasks()
        if 1 <= position <= len(tasks):
            return tasks[position - 1]  # Convert to 0-indexed
        return None
    
    def _execute_nlp_command(self, parsed_command: Dict) -> str:
        """Execute a command parsed by the NLP processor."""
        command_type = parsed_command['command_type']
        confidence = parsed_command.get('confidence', 0)
        
        # Debug output to see what's being parsed
        debug_info = f"DEBUG: Command type: {command_type}, Confidence: {confidence}\n"
        debug_info += f"DEBUG: Parsed data: {parsed_command}\n"
        
        # Show confidence level for debugging
        if confidence < 0.7:
            response = f"I think you want to {command_type.replace('_', ' ')}, but I'm not completely sure.\n\n"
        else:
            response = f"Understood! I'll {command_type.replace('_', ' ')} for you.\n\n"
        
        # Execute the command
        if command_type == 'add_task':
            title = parsed_command.get('title', '')
            description = parsed_command.get('description', '')
            priority = parsed_command.get('priority', 'medium')
            tags = parsed_command.get('tags', [])
            due_date = parsed_command.get('due_date', None)
            
            if title:
                task_id = self.memory.add_task(title, description, priority, "pending", tags, due_date)
                response += f"✅ Task added successfully! ID: {task_id}\nTitle: {title}\nPriority: {priority}"
                if tags:
                    response += f"\nTags: {', '.join(tags)}"
            else:
                response += "❌ I couldn't understand the task title. Please try again."
        
        elif command_type == 'search_tasks':
            query = parsed_command.get('query', '')
            if query:
                results = self.memory.search_tasks(query, k=10)
                response += self._format_search_results(results, query)
            else:
                response += "❌ I couldn't understand what you want to search for. Please try again."
        
        elif command_type == 'list_tasks':
            tasks = self.memory.get_all_tasks()
            response += self._format_task_list(tasks)
        
        elif command_type == 'update_task':
            task_id = parsed_command.get('task_id')
            field = parsed_command.get('field', 'status')
            value = parsed_command.get('value', 'completed')
            
            # Add debug info for updates
            response += debug_info
            
            if task_id is not None:
                # First try to find by database ID
                existing_task = self.memory.get_task_by_id(task_id)
                
                # If not found, try to find by display position
                if not existing_task:
                    display_task = self._find_task_by_display_position(task_id)
                    if display_task:
                        task_id = display_task['id']  # Use the actual database ID
                        existing_task = display_task
                        response += f"ℹ️  Found task at position {parsed_command.get('task_id')} (Database ID: {task_id})\n"
                
                if existing_task:
                    # Create the update dictionary
                    update_data = {field: value}
                    response += f"DEBUG: Updating task {task_id} with {update_data}\n"
                    
                    success = self.memory.update_task(task_id, **update_data)
                    if success:
                        response += f"✅ Task {task_id} updated successfully!\n"
                        response += f"   Changed {field} to: {value}\n"
                        response += f"   Task: {existing_task['title']}"
                    else:
                        response += f"❌ Failed to update task {task_id}."
                else:
                    response += f"❌ Task {task_id} not found. Available task IDs: "
                    all_tasks = self.memory.get_all_tasks()
                    if all_tasks:
                        task_ids = [str(task['id']) for task in all_tasks[:10]]  # Show first 10
                        response += ", ".join(task_ids)
                        if len(all_tasks) > 10:
                            response += f" ... and {len(all_tasks) - 10} more"
                    else:
                        response += "No tasks available"
            else:
                response += "❌ I couldn't understand which task to update. Please specify the task ID."
        
        elif command_type == 'delete_task':
            task_id = parsed_command.get('task_id')
            if task_id is not None:
                # First try to find by database ID
                existing_task = self.memory.get_task_by_id(task_id)
                
                # If not found, try to find by display position
                if not existing_task:
                    display_task = self._find_task_by_display_position(task_id)
                    if display_task:
                        task_id = display_task['id']  # Use the actual database ID
                        existing_task = display_task
                        response += f"ℹ️  Found task at position {parsed_command.get('task_id')} (Database ID: {task_id})\n"
                
                if existing_task:
                    success = self.memory.delete_task(task_id)
                    if success:
                        response += f"✅ Task {task_id} deleted successfully!\n"
                        response += f"   Deleted: {existing_task['title']}"
                    else:
                        response += f"❌ Failed to delete task {task_id}."
                else:
                    response += f"❌ Task {task_id} not found. Available task IDs: "
                    all_tasks = self.memory.get_all_tasks()
                    if all_tasks:
                        task_ids = [str(task['id']) for task in all_tasks[:10]]  # Show first 10
                        response += ", ".join(task_ids)
                        if len(all_tasks) > 10:
                            response += f" ... and {len(all_tasks) - 10} more"
                    else:
                        response += "No tasks available"
            else:
                response += "❌ I couldn't understand which task to delete. Please specify the task ID."
        
        elif command_type == 'show_stats':
            response += self._show_analytics("")
        
        else:
            response += f"❌ I understood you want to {command_type.replace('_', ' ')}, but I'm not sure how to execute it."
        
        return response
    
    def _process_traditional_command(self, user_input: str) -> str:
        """Process traditional command format as fallback."""
        # Parse command and arguments
        parts = user_input.split(' ', 1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        # Execute command
        if command in self.commands:
            try:
                return self.commands[command](args)
            except Exception as e:
                return f"Error executing command: {str(e)}"
        else:
            return f"Unknown command: {command}. Type 'help' for available commands."
    
    def _add_task(self, args: str) -> str:
        """Add a new task."""
        if not args:
            return "Usage: add <title> | [description] | [priority] | [tags] | [due_date]"
        
        # Parse task details using regex
        # Format: title | description | priority | tag1,tag2,tag3 | due_date
        parts = args.split('|')
        
        title = parts[0].strip()
        if not title:
            return "Task title is required."
        
        description = parts[1].strip() if len(parts) > 1 else ""
        priority = parts[2].strip() if len(parts) > 2 else "medium"
        tags_str = parts[3].strip() if len(parts) > 3 else ""
        due_date = parts[4].strip() if len(parts) > 4 else None
        
        # Validate priority
        if priority not in ['low', 'medium', 'high']:
            priority = 'medium'
        
        # Parse tags
        tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()] if tags_str else []
        
        # Validate due date
        if due_date:
            try:
                # Validate date format
                datetime.strptime(due_date, '%Y-%m-%d')
                # Check if date is not in the past
                due_datetime = datetime.strptime(due_date, '%Y-%m-%d')
                if due_datetime.date() < datetime.now().date():
                    print(f"{Fore.YELLOW}Warning: Due date {due_date} is in the past.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Error: Invalid due date format. Use YYYY-MM-DD format.{Style.RESET_ALL}")
                return "Invalid due date format. Please use YYYY-MM-DD format."
        
        # Add task
        task_id = self.memory.add_task(title, description, priority, "pending", tags, due_date)
        
        return f"Task added successfully! ID: {task_id}\nTitle: {title}\nPriority: {priority}"
    
    def _search_tasks(self, args: str) -> str:
        """Search for tasks using semantic similarity."""
        if not args:
            return "Usage: search <query>"
        
        results = self.memory.search_tasks(args, k=10)
        return self._format_search_results(results, args)
    
    def _list_tasks(self, args: str) -> str:
        """List all tasks with optional filtering."""
        try:
            tasks = self.memory.get_all_tasks()
            
            if not tasks:
                return "No tasks found."
            
            # Parse filter arguments
            filters = {}
            if args:
                parts = args.split()
                for part in parts:
                    if part.startswith('priority:'):
                        filters['priority'] = part.split(':')[1]
                    elif part.startswith('tag:'):
                        filters['tag'] = part.split(':')[1]
                    elif part.startswith('status:'):
                        filters['status'] = part.split(':')[1]
                    elif part.startswith('due:'):
                        filters['due'] = part.split(':')[1]
            
            # Apply filters
            filtered_tasks = []
            for task in tasks:
                if self._task_matches_filters(task, filters):
                    filtered_tasks.append(task)
            
            if not filtered_tasks:
                return "No tasks match the specified filters."
            
            # Sort tasks by priority and due date
            filtered_tasks.sort(key=lambda x: (
                {'high': 0, 'medium': 1, 'low': 2}.get(x.get('priority', 'medium'), 1),
                x.get('due_date', '9999-12-31') if x.get('due_date') else '9999-12-31'
            ))
            
            result = f"\n📋 Task List ({len(filtered_tasks)} tasks)\n"
            result += "=" * 80 + "\n"
            
            for i, task in enumerate(filtered_tasks, 1):
                task_id = task.get('id', 'N/A')
                title = task.get('title', 'No title')
                description = task.get('description', '')
                priority = task.get('priority', 'medium')
                tags = task.get('tags', [])
                due_date = task.get('due_date')
                completed = task.get('completed', False)
                created_at = task.get('created_at', '')
                
                # Priority color
                priority_colors = {
                    'high': Fore.RED,
                    'medium': Fore.YELLOW,
                    'low': Fore.GREEN
                }
                priority_color = priority_colors.get(priority, Fore.WHITE)
                
                # Status indicator
                status_icon = "✅" if completed else "⏳"
                status_color = Fore.GREEN if completed else Fore.CYAN
                
                # Due date formatting
                due_display = ""
                if due_date:
                    try:
                        due_datetime = datetime.strptime(due_date, '%Y-%m-%d')
                        today = datetime.now().date()
                        due_date_obj = due_datetime.date()
                        
                        if completed:
                            due_display = f"{Fore.GREEN}📅 Due: {due_date} (Completed){Style.RESET_ALL}"
                        elif due_date_obj < today:
                            due_display = f"{Fore.RED}📅 Due: {due_date} (OVERDUE){Style.RESET_ALL}"
                        elif due_date_obj == today:
                            due_display = f"{Fore.YELLOW}📅 Due: {due_date} (TODAY){Style.RESET_ALL}"
                        elif (due_date_obj - today).days <= 3:
                            due_display = f"{Fore.YELLOW}📅 Due: {due_date} (Soon){Style.RESET_ALL}"
                        else:
                            due_display = f"{Fore.CYAN}📅 Due: {due_date}{Style.RESET_ALL}"
                    except ValueError:
                        due_display = f"{Fore.RED}📅 Due: {due_date} (Invalid){Style.RESET_ALL}"
                
                # Format creation date
                created_display = ""
                if created_at:
                    try:
                        created_datetime = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        created_display = f"📅 Created: {created_datetime.strftime('%Y-%m-%d %H:%M')}"
                    except:
                        created_display = f"📅 Created: {created_at}"
                
                # Build task display
                result += f"\n{Fore.CYAN}{i:2d}.{Style.RESET_ALL} {status_color}{status_icon}{Style.RESET_ALL} {Fore.WHITE}{title}{Style.RESET_ALL}\n"
                result += f"    {Fore.BLUE}ID:{Style.RESET_ALL} {task_id}\n"
                
                if description:
                    result += f"    {Fore.BLUE}Description:{Style.RESET_ALL} {description}\n"
                
                result += f"    {Fore.BLUE}Priority:{Style.RESET_ALL} {priority_color}{priority.upper()}{Style.RESET_ALL}\n"
                
                if tags:
                    tag_display = ", ".join([f"{Fore.MAGENTA}#{tag}{Style.RESET_ALL}" for tag in tags])
                    result += f"    {Fore.BLUE}Tags:{Style.RESET_ALL} {tag_display}\n"
                
                if due_display:
                    result += f"    {due_display}\n"
                
                if created_display:
                    result += f"    {Fore.GRAY}{created_display}{Style.RESET_ALL}\n"
                
                result += "-" * 80 + "\n"
            
            return result
            
        except Exception as e:
            return f"Error listing tasks: {e}"
    
    def _task_matches_filters(self, task: Dict, filters: Dict) -> bool:
        """Check if a task matches the given filters."""
        for filter_type, filter_value in filters.items():
            if filter_type == 'priority':
                if task.get('priority', '').lower() != filter_value.lower():
                    return False
            elif filter_type == 'tag':
                if filter_value.lower() not in [tag.lower() for tag in task.get('tags', [])]:
                    return False
            elif filter_type == 'status':
                if filter_value.lower() == 'completed' and not task.get('completed', False):
                    return False
                elif filter_value.lower() == 'pending' and task.get('completed', False):
                    return False
            elif filter_type == 'due':
                if filter_value.lower() == 'overdue':
                    due_date = task.get('due_date')
                    if not due_date:
                        return False
                    try:
                        due_datetime = datetime.strptime(due_date, '%Y-%m-%d')
                        if due_datetime.date() >= datetime.now().date():
                            return False
                    except ValueError:
                        return False
                elif filter_value.lower() == 'today':
                    due_date = task.get('due_date')
                    if not due_date:
                        return False
                    try:
                        due_datetime = datetime.strptime(due_date, '%Y-%m-%d')
                        if due_datetime.date() != datetime.now().date():
                            return False
                    except ValueError:
                        return False
        return True
    
    def _update_task(self, args: str) -> str:
        """Update a task."""
        if not args:
            return "Usage: update <task_id> <field>=<value> [field2=value2 ...]"
        
        # Parse task ID and updates
        parts = args.split(' ', 1)
        if len(parts) < 2:
            return "Usage: update <task_id> <field>=<value> [field2=value2 ...]"
        
        try:
            task_id = int(parts[0])
        except ValueError:
            return "Task ID must be a number."
        
        # Parse field updates
        updates = {}
        update_parts = parts[1].split()
        
        for part in update_parts:
            if '=' in part:
                field, value = part.split('=', 1)
                field = field.strip()
                value = value.strip()
                
                # Handle special cases
                if field == 'tags':
                    value = [tag.strip() for tag in value.split(',') if tag.strip()]
                elif field == 'priority' and value not in ['low', 'medium', 'high']:
                    return f"Invalid priority: {value}. Must be low, medium, or high."
                elif field == 'status' and value not in ['pending', 'in_progress', 'completed']:
                    return f"Invalid status: {value}. Must be pending, in_progress, or completed."
                
                updates[field] = value
        
        if not updates:
            return "No valid updates provided."
        
        # Update task
        success = self.memory.update_task(task_id, **updates)
        
        if success:
            return f"Task {task_id} updated successfully!"
        else:
            return f"Task {task_id} not found."
    
    def _delete_task(self, args: str) -> str:
        """Delete a task."""
        if not args:
            return "Usage: delete <task_id>"
        
        try:
            task_id = int(args.strip())
        except ValueError:
            return "Task ID must be a number."
        
        success = self.memory.delete_task(task_id)
        
        if success:
            return f"Task {task_id} deleted successfully!"
        else:
            return f"Task {task_id} not found."
    
    def _show_statistics(self, args: str) -> str:
        """Show basic task statistics."""
        stats = self.memory.get_task_statistics()
        
        response = "=== Task Statistics ===\n"
        response += f"Total tasks: {stats['total_tasks']}\n\n"
        
        if stats['by_status']:
            response += "By Status:\n"
            for status, count in stats['by_status'].items():
                response += f"  {status}: {count}\n"
            response += "\n"
        
        if stats['by_priority']:
            response += "By Priority:\n"
            for priority, count in stats['by_priority'].items():
                response += f"  {priority}: {count}\n"
        
        return response
    
    def _show_analytics(self, args: str) -> str:
        """Show comprehensive analytics and insights."""
        analytics = self.analytics.get_comprehensive_stats()
        
        response = "=== COMPREHENSIVE TASK ANALYTICS ===\n\n"
        
        # Basic Stats
        basic_stats = analytics['basic_stats']
        response += f"📊 BASIC STATISTICS\n"
        response += f"Total Tasks: {basic_stats['total_tasks']}\n"
        response += f"Average Title Length: {basic_stats['avg_title_length']:.1f} characters\n"
        response += f"Tasks with Descriptions: {basic_stats['tasks_with_descriptions']}\n"
        response += f"Tasks with Tags: {basic_stats['tasks_with_tags']}\n\n"
        
        # Priority Analysis
        priority_analysis = analytics['priority_analysis']
        if priority_analysis:
            response += f"🎯 PRIORITY ANALYSIS\n"
            for priority, count in priority_analysis['distribution'].items():
                percentage = priority_analysis['percentages'][priority]
                response += f"{priority.title()}: {count} ({percentage:.1f}%)\n"
            response += f"Priority Balance: {priority_analysis['priority_balance']}\n\n"
        
        # Status Analysis
        status_analysis = analytics['status_analysis']
        if status_analysis:
            response += f"📈 STATUS ANALYSIS\n"
            for status, count in status_analysis['distribution'].items():
                percentage = status_analysis['percentages'][status]
                response += f"{status.title()}: {count} ({percentage:.1f}%)\n"
            response += f"Completion Rate: {status_analysis['completion_rate']:.1f}%\n\n"
        
        # Productivity Metrics
        productivity = analytics['productivity_metrics']
        if productivity:
            response += f"⚡ PRODUCTIVITY METRICS\n"
            response += f"Average Daily Tasks: {productivity['avg_daily_tasks']:.1f}\n"
            response += f"Productivity Score: {productivity['productivity_score']:.1f}/100\n"
            response += f"Average Task Complexity: {productivity['avg_task_complexity']:.2f}\n\n"
        
        # Tag Analysis
        tag_analysis = analytics['tag_analysis']
        if tag_analysis and tag_analysis['most_common_tags']:
            response += f"🏷️  TAG ANALYSIS\n"
            response += f"Most Common Tags:\n"
            for tag, count in tag_analysis['most_common_tags'][:5]:
                response += f"  {tag}: {count}\n"
            response += f"Tag Usage: {tag_analysis['tag_usage_percentage']:.1f}%\n\n"
        
        return response
    
    def _show_insights(self, args: str) -> str:
        """Show actionable insights and recommendations."""
        analytics = self.analytics.get_comprehensive_stats()
        
        response = "=== ACTIONABLE INSIGHTS & RECOMMENDATIONS ===\n\n"
        
        # Insights
        insights = analytics['insights']
        if insights:
            response += "💡 INSIGHTS\n"
            for insight in insights:
                response += f"• {insight}\n"
            response += "\n"
        
        # Recommendations
        recommendations = analytics['recommendations']
        if recommendations:
            response += "🎯 RECOMMENDATIONS\n"
            for rec in recommendations:
                response += f"• {rec}\n"
            response += "\n"
        
        return response
    
    def _show_weekly_report(self, args: str) -> str:
        """Show weekly productivity report."""
        report = self.analytics.get_weekly_report()
        
        response = "=== WEEKLY PRODUCTIVITY REPORT ===\n\n"
        response += f"📅 Period: {report['period']}\n"
        response += f"📝 Tasks Created: {report['tasks_created']}\n"
        response += f"✅ Tasks Completed: {report['tasks_completed']}\n"
        response += f"📊 Completion Rate: {report['completion_rate']:.1f}%\n"
        response += f"🚀 Most Productive Day: {report['most_productive_day']}\n\n"
        
        # Priority Distribution
        if report['priority_distribution']:
            response += "🎯 Priority Distribution:\n"
            for priority, count in report['priority_distribution'].items():
                response += f"  {priority.title()}: {count}\n"
            response += "\n"
        
        # Top Tags
        if report['top_tags']:
            response += "🏷️  Top Tags This Week:\n"
            for tag, count in report['top_tags']:
                response += f"  {tag}: {count}\n"
        
        return response
    
    def _format_search_results(self, results: List[Dict], query: str) -> str:
        """Format search results for display."""
        if not results:
            return f"No tasks found matching '{query}'"
        
        response = f"Found {len(results)} tasks matching '{query}':\n\n"
        
        for i, task in enumerate(results, 1):
            score = task.get('similarity_score', 0)
            response += f"{i}. [ID: {task['id']}] {task['title']} (Score: {score:.3f})\n"
            if task['description']:
                response += f"   Description: {task['description']}\n"
            response += f"   Priority: {task['priority']}, Status: {task['status']}\n"
            if task['tags']:
                response += f"   Tags: {', '.join(task['tags'])}\n"
            response += "\n"
        
        return response
    
    def _format_task_list(self, tasks: List[Dict]) -> str:
        """Format task list for display."""
        if not tasks:
            return "No tasks found"
        
        response = f"Found {len(tasks)} tasks:\n\n"
        
        for i, task in enumerate(tasks, 1):
            # Add debugging for each task
            print(f"DEBUG: Task {i}: ID={task['id']}, Title='{task['title']}', Status='{task['status']}', Priority='{task['priority']}'")
            
            # Make the ID more prominent and clear
            response += f"{i}. [Database ID: {task['id']}] {task['title']}\n"
            if task['description']:
                response += f"   Description: {task['description']}\n"
            response += f"   Priority: {task['priority']}, Status: {task['status']}\n"
            if task['tags']:
                response += f"   Tags: {', '.join(task['tags'])}\n"
            response += f"   Created: {task['created_at'][:19]}\n"
            if task.get('updated_at'):
                response += f"   Updated: {task['updated_at'][:19]}\n"
            response += "\n"
        
        response += "💡 Tip: Use the Database ID (not the list number) when updating tasks!\n"
        response += "   Example: 'mark task 5 as completed' refers to Database ID 5\n"
        
        return response
    
    def _show_help(self, args: str) -> str:
        """Show help information."""
        help_text = """
=== AI Task Assistant Commands ===

🎯 NATURAL LANGUAGE COMMANDS (NEW!)
You can now use natural language! Examples:
• "add a high priority task to buy groceries"
• "search for meeting tasks"
• "mark task 5 as completed"
• "show me all urgent work tasks"
• "what are my task stats?"

📝 TRADITIONAL COMMANDS

add <title> | [description] | [priority] | [tags] | [due_date]
  Add a new task. Use | to separate fields.
  Priority: low, medium, high (default: medium)
  Tags: comma-separated list
  Due date: YYYY-MM-DD format
  Example: add "Buy groceries" | "Milk, bread, eggs" | high | shopping,food | 2024-05-01

search <query>
  Search for tasks using semantic similarity.
  Example: search "meeting with client"

list [filters]
  List all tasks with optional filtering.
  Filters: priority:high, tag:work, status:completed, due:overdue, due:today
  Example: list priority:high due:overdue

update <task_id> | [field] | [value]
  Update a task field. Use | to separate fields.
  Fields: title, description, priority, tags, due_date
  Example: update 1 | priority | high

delete <task_id>
  Delete a task by ID.

complete <task_id>
  Mark a task as completed.

stats
  Show task statistics and insights.

analytics
  Show detailed analytics and trends.

insights
  Show AI-powered insights and recommendations.

weekly
  Show weekly progress report.

due
  Show due date statistics, overdue tasks, and upcoming deadlines.

help
  Show this help message.

quit/exit
  Exit the assistant.

🗣️ NATURAL LANGUAGE COMMANDS

You can also use natural language to interact with the assistant:

• "Add a task to buy groceries tomorrow"
• "Search for all work-related tasks"
• "Update task 3 to high priority"
• "Show me overdue tasks"
• "List tasks due this week"

📅 NATURAL LANGUAGE DUE DATES

The assistant understands various natural language date expressions:

• "today", "tomorrow", "yesterday"
• "this morning", "this afternoon", "tonight"
• "this week", "next week", "last week"
• "this month", "next month", "last month"
• "end of month", "end of week", "end of year"
• "next Monday", "this Friday"
• "in 3 days", "in 2 weeks", "in 1 month"
• "December 15", "March 1st"
• "12/15/2024", "2024-12-15"

Examples:
• "Add task to review documents by next Friday"
• "Create task for team meeting this afternoon"
• "Schedule dentist appointment in 2 weeks"
• "Set reminder for project deadline end of month"
"""
        return help_text
    
    def _show_due_stats(self, args: str = "") -> str:
        """Show due date statistics and overdue tasks."""
        try:
            tasks = self.memory.get_all_tasks()
            
            if not tasks:
                return "No tasks found."
            
            today = datetime.now().date()
            overdue_tasks = []
            due_today = []
            due_soon = []  # Next 3 days
            upcoming = []  # Next week
            no_due_date = []
            
            for task in tasks:
                due_date = task.get('due_date')
                if not due_date:
                    no_due_date.append(task)
                    continue
                
                try:
                    due_datetime = datetime.strptime(due_date, '%Y-%m-%d')
                    due_date_obj = due_datetime.date()
                    
                    if task.get('completed', False):
                        continue  # Skip completed tasks
                    
                    if due_date_obj < today:
                        overdue_tasks.append(task)
                    elif due_date_obj == today:
                        due_today.append(task)
                    elif (due_date_obj - today).days <= 3:
                        due_soon.append(task)
                    elif (due_date_obj - today).days <= 7:
                        upcoming.append(task)
                        
                except ValueError:
                    continue  # Skip invalid dates
            
            result = f"\n📅 Due Date Statistics\n"
            result += "=" * 50 + "\n"
            
            # Summary
            result += f"📊 Summary:\n"
            result += f"   • Overdue: {len(overdue_tasks)} tasks\n"
            result += f"   • Due today: {len(due_today)} tasks\n"
            result += f"   • Due soon (3 days): {len(due_soon)} tasks\n"
            result += f"   • Upcoming (1 week): {len(upcoming)} tasks\n"
            result += f"   • No due date: {len(no_due_date)} tasks\n"
            result += f"   • Total active: {len([t for t in tasks if not t.get('completed', False)])} tasks\n\n"
            
            # Overdue tasks
            if overdue_tasks:
                result += f"🔴 OVERDUE TASKS ({len(overdue_tasks)}):\n"
                result += "-" * 30 + "\n"
                for i, task in enumerate(overdue_tasks, 1):
                    days_overdue = (today - datetime.strptime(task['due_date'], '%Y-%m-%d').date()).days
                    result += f"{i}. {Fore.RED}{task['title']}{Style.RESET_ALL} "
                    result += f"({Fore.RED}{days_overdue} days overdue{Style.RESET_ALL})\n"
                    result += f"   Priority: {task.get('priority', 'medium').upper()}\n"
                    if task.get('tags'):
                        result += f"   Tags: {', '.join(task['tags'])}\n"
                    result += "\n"
            
            # Due today
            if due_today:
                result += f"🟡 DUE TODAY ({len(due_today)}):\n"
                result += "-" * 30 + "\n"
                for i, task in enumerate(due_today, 1):
                    result += f"{i}. {Fore.YELLOW}{task['title']}{Style.RESET_ALL}\n"
                    result += f"   Priority: {task.get('priority', 'medium').upper()}\n"
                    if task.get('tags'):
                        result += f"   Tags: {', '.join(task['tags'])}\n"
                    result += "\n"
            
            # Due soon
            if due_soon:
                result += f"🟠 DUE SOON ({len(due_soon)}):\n"
                result += "-" * 30 + "\n"
                for i, task in enumerate(due_soon, 1):
                    days_until = (datetime.strptime(task['due_date'], '%Y-%m-%d').date() - today).days
                    result += f"{i}. {Fore.YELLOW}{task['title']}{Style.RESET_ALL} "
                    result += f"({Fore.YELLOW}in {days_until} days{Style.RESET_ALL})\n"
                    result += f"   Priority: {task.get('priority', 'medium').upper()}\n"
                    if task.get('tags'):
                        result += f"   Tags: {', '.join(task['tags'])}\n"
                    result += "\n"
            
            # Upcoming
            if upcoming:
                result += f"🔵 UPCOMING ({len(upcoming)}):\n"
                result += "-" * 30 + "\n"
                for i, task in enumerate(upcoming, 1):
                    days_until = (datetime.strptime(task['due_date'], '%Y-%m-%d').date() - today).days
                    result += f"{i}. {Fore.CYAN}{task['title']}{Style.RESET_ALL} "
                    result += f"({Fore.CYAN}in {days_until} days{Style.RESET_ALL})\n"
                    result += f"   Priority: {task.get('priority', 'medium').upper()}\n"
                    if task.get('tags'):
                        result += f"   Tags: {', '.join(task['tags'])}\n"
                    result += "\n"
            
            return result
            
        except Exception as e:
            return f"Error showing due statistics: {e}"
    
    def _complete_task(self, args: str) -> str:
        """Mark a task as completed."""
        if not args:
            return "Usage: complete <task_id>"
        
        try:
            task_id = args.strip()
            success = self.memory.complete_task(task_id)
            
            if success:
                return f"✅ Task {task_id} marked as completed!"
            else:
                return f"❌ Task {task_id} not found or already completed."
                
        except Exception as e:
            return f"Error completing task: {e}"
    
    def _show_suggestions(self, args: str = "") -> str:
        """Show AI-powered smart task suggestions."""
        suggestions = self.suggestions.get_smart_suggestions(limit=5)
        if not suggestions:
            return "No smart suggestions available. Add more tasks to get recommendations."
        response = "=== SMART TASK SUGGESTIONS ===\n\n"
        for i, s in enumerate(suggestions, 1):
            response += f"{i}. {s.title}\n   {s.description}\n   Priority: {s.priority.title()} | Tags: {', '.join(s.tags)}\n   Reasoning: {s.reasoning}\n\n"
        return response
    
    def run_interactive(self):
        """Run the assistant in interactive mode."""
        print("=== AI Task Assistant with Vector Memory & NLP ===")
        print("🎯 Now with Natural Language Processing!")
        print("Type 'help' for available commands.")
        print("Type 'quit' to exit.\n")
        
        while True:
            try:
                user_input = input("Assistant> ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye! Your tasks have been saved.")
                    break
                
                response = self.process_command(user_input)
                print(response)
                
            except KeyboardInterrupt:
                print("\nGoodbye! Your tasks have been saved.")
                break
            except EOFError:
                print("\nGoodbye! Your tasks have been saved.")
                break 