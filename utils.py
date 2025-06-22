import re
from typing import List, Dict, Optional
from datetime import datetime
import colorama
from colorama import Fore, Back, Style

# Initialize colorama for cross-platform colored output
colorama.init()

def format_task_display(task: Dict, show_id: bool = True, show_score: bool = False) -> str:
    """
    Format a task for display.
    
    Args:
        task: Task dictionary
        show_id: Whether to show task ID
        show_score: Whether to show similarity score
        
    Returns:
        Formatted task string
    """
    lines = []
    
    # Title line
    title_line = ""
    if show_id:
        title_line += f"[ID: {task['id']}] "
    title_line += task['title']
    if show_score and 'similarity_score' in task:
        title_line += f" (Score: {task['similarity_score']:.3f})"
    lines.append(Fore.CYAN + title_line + Style.RESET_ALL)
    
    # Description
    if task.get('description'):
        lines.append(f"  Description: {task['description']}")
    
    # Priority and status
    priority_color = {
        'low': Fore.GREEN,
        'medium': Fore.YELLOW,
        'high': Fore.RED
    }.get(task['priority'], Fore.WHITE)
    
    status_color = {
        'pending': Fore.YELLOW,
        'in_progress': Fore.BLUE,
        'completed': Fore.GREEN
    }.get(task['status'], Fore.WHITE)
    
    lines.append(f"  Priority: {priority_color}{task['priority']}{Style.RESET_ALL}, "
                f"Status: {status_color}{task['status']}{Style.RESET_ALL}")
    
    # Tags
    if task.get('tags'):
        lines.append(f"  Tags: {Fore.MAGENTA}{', '.join(task['tags'])}{Style.RESET_ALL}")
    
    # Timestamps
    if 'created_at' in task:
        created = datetime.fromisoformat(task['created_at']).strftime('%Y-%m-%d %H:%M')
        lines.append(f"  Created: {created}")
    
    return '\n'.join(lines)

def validate_priority(priority: str) -> bool:
    """Validate priority value."""
    return priority.lower() in ['low', 'medium', 'high']

def validate_status(status: str) -> bool:
    """Validate status value."""
    return status.lower() in ['pending', 'in_progress', 'completed']

def parse_tags(tags_str: str) -> List[str]:
    """
    Parse comma-separated tags string into list.
    
    Args:
        tags_str: Comma-separated tags string
        
    Returns:
        List of cleaned tags
    """
    if not tags_str:
        return []
    
    tags = [tag.strip() for tag in tags_str.split(',')]
    return [tag for tag in tags if tag]  # Remove empty tags

def format_search_results(results: List[Dict], query: str) -> str:
    """
    Format search results for display.
    
    Args:
        results: List of task dictionaries with similarity scores
        query: Original search query
        
    Returns:
        Formatted results string
    """
    if not results:
        return f"No tasks found matching '{query}'"
    
    lines = [f"Found {len(results)} tasks matching '{query}':\n"]
    
    for i, task in enumerate(results, 1):
        lines.append(f"{i}. {format_task_display(task, show_id=True, show_score=True)}")
        lines.append("")  # Empty line between tasks
    
    return '\n'.join(lines)

def format_task_list(tasks: List[Dict], filters: Dict = None) -> str:
    """
    Format a list of tasks for display.
    
    Args:
        tasks: List of task dictionaries
        filters: Optional filter information
        
    Returns:
        Formatted task list string
    """
    if not tasks:
        filter_info = ""
        if filters:
            filter_parts = []
            if filters.get('status'):
                filter_parts.append(f"status={filters['status']}")
            if filters.get('priority'):
                filter_parts.append(f"priority={filters['priority']}")
            if filter_parts:
                filter_info = f" with filters: {', '.join(filter_parts)}"
        return f"No tasks found{filter_info}"
    
    lines = [f"Found {len(tasks)} tasks:\n"]
    
    for i, task in enumerate(tasks, 1):
        lines.append(f"{i}. {format_task_display(task, show_id=True, show_score=False)}")
        lines.append("")  # Empty line between tasks
    
    return '\n'.join(lines)

def format_statistics(stats: Dict) -> str:
    """
    Format task statistics for display.
    
    Args:
        stats: Statistics dictionary
        
    Returns:
        Formatted statistics string
    """
    lines = [Fore.CYAN + "=== Task Statistics ===" + Style.RESET_ALL]
    lines.append(f"Total tasks: {Fore.GREEN}{stats['total_tasks']}{Style.RESET_ALL}\n")
    
    if stats.get('by_status'):
        lines.append(Fore.YELLOW + "By Status:" + Style.RESET_ALL)
        for status, count in stats['by_status'].items():
            status_color = {
                'pending': Fore.YELLOW,
                'in_progress': Fore.BLUE,
                'completed': Fore.GREEN
            }.get(status, Fore.WHITE)
            lines.append(f"  {status_color}{status}{Style.RESET_ALL}: {count}")
        lines.append("")
    
    if stats.get('by_priority'):
        lines.append(Fore.YELLOW + "By Priority:" + Style.RESET_ALL)
        for priority, count in stats['by_priority'].items():
            priority_color = {
                'low': Fore.GREEN,
                'medium': Fore.YELLOW,
                'high': Fore.RED
            }.get(priority, Fore.WHITE)
            lines.append(f"  {priority_color}{priority}{Style.RESET_ALL}: {count}")
    
    return '\n'.join(lines)

def parse_task_input(input_str: str) -> Dict:
    """
    Parse task input string into components.
    
    Args:
        input_str: Input string in format "title | description | priority | tags"
        
    Returns:
        Dictionary with parsed components
    """
    parts = [part.strip() for part in input_str.split('|')]
    
    result = {
        'title': parts[0] if len(parts) > 0 else "",
        'description': parts[1] if len(parts) > 1 else "",
        'priority': parts[2] if len(parts) > 2 else "medium",
        'tags': parse_tags(parts[3]) if len(parts) > 3 else []
    }
    
    # Validate and normalize priority
    if not validate_priority(result['priority']):
        result['priority'] = 'medium'
    
    return result

def parse_update_input(input_str: str) -> tuple:
    """
    Parse update input string into task ID and updates.
    
    Args:
        input_str: Input string in format "task_id field=value field2=value2"
        
    Returns:
        Tuple of (task_id, updates_dict)
    """
    parts = input_str.split(' ', 1)
    if len(parts) < 2:
        raise ValueError("Invalid update format")
    
    try:
        task_id = int(parts[0])
    except ValueError:
        raise ValueError("Task ID must be a number")
    
    updates = {}
    update_parts = parts[1].split()
    
    for part in update_parts:
        if '=' in part:
            field, value = part.split('=', 1)
            field = field.strip()
            value = value.strip()
            
            # Handle special cases
            if field == 'tags':
                value = parse_tags(value)
            elif field == 'priority' and not validate_priority(value):
                raise ValueError(f"Invalid priority: {value}")
            elif field == 'status' and not validate_status(value):
                raise ValueError(f"Invalid status: {value}")
            
            updates[field] = value
    
    return task_id, updates

def get_colored_prompt() -> str:
    """Get a colored prompt for the interactive interface."""
    return f"{Fore.GREEN}Assistant{Style.RESET_ALL}> "

def print_welcome_message():
    """Print the welcome message for the assistant."""
    print(Fore.CYAN + "=" * 50)
    print("AI Task Assistant with Vector Memory")
    print("=" * 50 + Style.RESET_ALL)
    print("Type 'help' for available commands.")
    print("Type 'quit' to exit.\n")

def print_goodbye_message():
    """Print the goodbye message."""
    print(f"\n{Fore.GREEN}Goodbye! Your tasks have been saved.{Style.RESET_ALL}") 