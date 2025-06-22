import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta

class NLPProcessor:
    def __init__(self):
        """Initialize the NLP processor."""
        # Command patterns for natural language understanding
        self.command_patterns = {
            'add_task': [
                r'add\s+(?:a\s+)?(?:new\s+)?task\s+(?:called\s+)?["\']([^"\']+)["\']',
                r'create\s+(?:a\s+)?(?:new\s+)?task\s+(?:called\s+)?["\']([^"\']+)["\']',
                r'new\s+task\s+(?:called\s+)?["\']([^"\']+)["\']',
                r'add\s+["\']([^"\']+)["\']\s+to\s+my\s+tasks',
                r'add\s+(?:a\s+)?task\s+(?:about\s+)?(.+)',
                r'create\s+(?:a\s+)?task\s+(?:about\s+)?(.+)',
            ],
            'search_tasks': [
                r'search\s+(?:for\s+)?["\']([^"\']+)["\']',
                r'find\s+(?:tasks\s+)?(?:about\s+)?["\']([^"\']+)["\']',
                r'look\s+for\s+(?:tasks\s+)?(?:about\s+)?["\']([^"\']+)["\']',
                r'show\s+me\s+(?:tasks\s+)?(?:about\s+)?["\']([^"\']+)["\']',
                r'search\s+(?:for\s+)?(.+)',
                r'find\s+(?:tasks\s+)?(?:about\s+)?(.+)',
            ],
            'list_tasks': [
                r'list\s+(?:all\s+)?tasks',
                r'show\s+(?:all\s+)?tasks',
                r'display\s+(?:all\s+)?tasks',
                r'what\s+tasks\s+do\s+I\s+have',
                r'my\s+tasks',
                r'all\s+tasks',
            ],
            'update_task': [
                r'(?:mark|set)\s+task\s+(\d+)\s+as\s+(\w+)',
                r'update\s+task\s+(\d+)\s+to\s+(\w+)',
                r'change\s+task\s+(\d+)\s+to\s+(\w+)',
                r'task\s+(\d+)\s+is\s+now\s+(\w+)',
                r'mark\s+(\d+)\s+as\s+(\w+)',
                r'complete\s+task\s+(\d+)',
                r'finish\s+task\s+(\d+)',
                r'update\s+(\d+)\s+to\s+(\w+)',
                r'change\s+(\d+)\s+to\s+(\w+)',
                r'set\s+(\d+)\s+to\s+(\w+)',
                r'mark\s+task\s+(\d+)\s+as\s+(\w+)',
                r'set\s+task\s+(\d+)\s+to\s+(\w+)',
                r'change\s+(\d+)\s+priority\s+to\s+(\w+)',
                r'update\s+(\d+)\s+priority\s+to\s+(\w+)',
                r'set\s+(\d+)\s+priority\s+to\s+(\w+)',
                r'mark\s+(\d+)\s+priority\s+as\s+(\w+)',
            ],
            'delete_task': [
                r'delete\s+task\s+(\d+)',
                r'remove\s+task\s+(\d+)',
                r'cancel\s+task\s+(\d+)',
                r'drop\s+task\s+(\d+)',
                r'delete\s+(\d+)',
                r'remove\s+(\d+)',
            ],
            'show_stats': [
                r'show\s+(?:task\s+)?statistics',
                r'display\s+(?:task\s+)?stats',
                r'what\s+are\s+my\s+task\s+stats',
                r'give\s+me\s+a\s+summary',
                r'stats',
                r'statistics',
            ]
        }
    
    def parse_command(self, user_input: str) -> Dict:
        """
        Parse natural language input and return structured command.
        
        Args:
            user_input: Natural language input from user
            
        Returns:
            Dictionary with parsed command information
        """
        user_input = user_input.strip()
        original_input = user_input
        user_input_lower = user_input.lower()
        
        print(f"DEBUG: Parsing input: '{user_input}'")
        
        # Check for exact command matches first
        for command_type, patterns in self.command_patterns.items():
            for i, pattern in enumerate(patterns):
                match = re.search(pattern, user_input_lower, re.IGNORECASE)
                if match:
                    print(f"DEBUG: Matched pattern {i} for command type '{command_type}'")
                    print(f"DEBUG: Match groups: {match.groups()}")
                    result = self._extract_command_details(command_type, original_input, match)
                    print(f"DEBUG: Extracted result: {result}")
                    return result
        
        # If no exact match, try to infer command type
        print("DEBUG: No exact pattern match, trying inference")
        result = self._infer_command(original_input)
        print(f"DEBUG: Inferred result: {result}")
        return result
    
    def _extract_command_details(self, command_type: str, user_input: str, match) -> Dict:
        """Extract detailed information from matched command."""
        result = {
            'command_type': command_type,
            'confidence': 0.9,
            'raw_input': user_input
        }
        
        # Extract entities
        entities = self._extract_entities(user_input)
        result.update(entities)
        
        # Extract specific command details
        if command_type == 'add_task':
            result.update(self._extract_add_task_details(user_input, match))
        elif command_type == 'search_tasks':
            result.update(self._extract_search_details(user_input, match))
        elif command_type == 'update_task':
            result.update(self._extract_update_details(user_input, match))
        elif command_type == 'delete_task':
            result.update(self._extract_delete_details(user_input, match))
        
        return result
    
    def _extract_entities(self, user_input: str) -> Dict:
        """Extract entities like priority, status, due dates from text."""
        entities = {}
        
        # Extract priority
        priority_patterns = {
            'high': r'\b(?:urgent|critical|asap|emergency|high|important|priority)\b',
            'medium': r'\b(?:medium|normal|moderate)\b',
            'low': r'\b(?:low|minor|optional)\b'
        }
        
        for priority, pattern in priority_patterns.items():
            if re.search(pattern, user_input, re.IGNORECASE):
                entities['priority'] = priority
                break
        
        # Extract status
        status_patterns = {
            'completed': r'\b(?:done|completed|finished|complete)\b',
            'in_progress': r'\b(?:in\s+progress|working|ongoing)\b',
            'pending': r'\b(?:pending|waiting|not\s+started)\b'
        }
        
        for status, pattern in status_patterns.items():
            if re.search(pattern, user_input, re.IGNORECASE):
                entities['status'] = status
                break
        
        # Extract due date
        due_date = self._parse_due_date(user_input)
        if due_date:
            entities['due_date'] = due_date
        
        return entities
    
    def _parse_due_date(self, text: str) -> Optional[str]:
        """Parse due date text to ISO format with enhanced natural language support."""
        today = datetime.now()
        text_lower = text.lower()
        
        # Basic time references
        if re.search(r'\btoday\b', text_lower):
            return today.strftime('%Y-%m-%d')
        elif re.search(r'\btomorrow\b', text_lower):
            return (today + timedelta(days=1)).strftime('%Y-%m-%d')
        elif re.search(r'\byesterday\b', text_lower):
            return (today - timedelta(days=1)).strftime('%Y-%m-%d')
        
        # Time of day
        elif re.search(r'\bthis\s+morning\b', text_lower):
            return today.strftime('%Y-%m-%d')
        elif re.search(r'\bthis\s+afternoon\b', text_lower):
            return today.strftime('%Y-%m-%d')
        elif re.search(r'\bthis\s+evening\b', text_lower):
            return today.strftime('%Y-%m-%d')
        elif re.search(r'\btonight\b', text_lower):
            return today.strftime('%Y-%m-%d')
        
        # Week references
        elif re.search(r'\bthis\s+week\b', text_lower):
            # End of current week (Sunday)
            days_until_weekend = 6 - today.weekday()
            return (today + timedelta(days=days_until_weekend)).strftime('%Y-%m-%d')
        elif re.search(r'\bnext\s+week\b', text_lower):
            # Start of next week (Monday)
            days_until_next_week = 7 - today.weekday()
            return (today + timedelta(days=days_until_next_week)).strftime('%Y-%m-%d')
        elif re.search(r'\blast\s+week\b', text_lower):
            # Start of last week (Monday)
            days_since_last_week = today.weekday() + 7
            return (today - timedelta(days=days_since_last_week)).strftime('%Y-%m-%d')
        
        # Month references
        elif re.search(r'\bthis\s+month\b', text_lower):
            # End of current month
            last_day = (today.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            return last_day.strftime('%Y-%m-%d')
        elif re.search(r'\bnext\s+month\b', text_lower):
            # Start of next month
            next_month = (today.replace(day=1) + timedelta(days=32)).replace(day=1)
            return next_month.strftime('%Y-%m-%d')
        elif re.search(r'\blast\s+month\b', text_lower):
            # Start of last month
            last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
            return last_month.strftime('%Y-%m-%d')
        
        # End of period references
        elif re.search(r'\bend\s+of\s+month\b', text_lower):
            last_day = (today.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            return last_day.strftime('%Y-%m-%d')
        elif re.search(r'\bend\s+of\s+week\b', text_lower):
            days_until_weekend = 6 - today.weekday()
            return (today + timedelta(days=days_until_weekend)).strftime('%Y-%m-%d')
        elif re.search(r'\bend\s+of\s+year\b', text_lower):
            return today.replace(month=12, day=31).strftime('%Y-%m-%d')
        
        # Specific days of the week
        elif re.search(r'\bnext\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', text_lower):
            day_match = re.search(r'\bnext\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', text_lower)
            if day_match:
                target_day = day_match.group(1)
                return self._get_next_weekday(target_day)
        
        elif re.search(r'\bthis\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', text_lower):
            day_match = re.search(r'\bthis\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', text_lower)
            if day_match:
                target_day = day_match.group(1)
                return self._get_this_weekday(target_day)
        
        # Relative days
        elif re.search(r'\bin\s+(\d+)\s+days?\b', text_lower):
            days_match = re.search(r'\bin\s+(\d+)\s+days?\b', text_lower)
            if days_match:
                days = int(days_match.group(1))
                return (today + timedelta(days=days)).strftime('%Y-%m-%d')
        
        elif re.search(r'\bin\s+(\d+)\s+weeks?\b', text_lower):
            weeks_match = re.search(r'\bin\s+(\d+)\s+weeks?\b', text_lower)
            if weeks_match:
                weeks = int(weeks_match.group(1))
                return (today + timedelta(weeks=weeks)).strftime('%Y-%m-%d')
        
        elif re.search(r'\bin\s+(\d+)\s+months?\b', text_lower):
            months_match = re.search(r'\bin\s+(\d+)\s+months?\b', text_lower)
            if months_match:
                months = int(months_match.group(1))
                # Approximate month calculation
                new_month = today.month + months
                new_year = today.year + (new_month - 1) // 12
                new_month = ((new_month - 1) % 12) + 1
                return today.replace(year=new_year, month=new_month).strftime('%Y-%m-%d')
        
        # Specific date patterns
        elif re.search(r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b', text_lower):
            date_match = re.search(r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b', text_lower)
            if date_match:
                month, day, year = date_match.groups()
                # Handle 2-digit years
                if len(year) == 2:
                    year = '20' + year
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        # Month name patterns
        elif re.search(r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})\b', text_lower):
            month_match = re.search(r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2})\b', text_lower)
            if month_match:
                month_name, day = month_match.groups()
                month_num = self._month_name_to_number(month_name)
                year = today.year
                # If the date has passed this year, assume next year
                if month_num < today.month or (month_num == today.month and int(day) < today.day):
                    year += 1
                return f"{year}-{month_num:02d}-{int(day):02d}"
        
        return None
    
    def _get_next_weekday(self, day_name: str) -> str:
        """Get the next occurrence of a specific weekday."""
        today = datetime.now()
        day_map = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        target_day = day_map.get(day_name.lower(), 0)
        
        days_ahead = target_day - today.weekday()
        if days_ahead <= 0:  # Target day already happened this week
            days_ahead += 7
        return (today + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
    
    def _get_this_weekday(self, day_name: str) -> str:
        """Get this week's occurrence of a specific weekday."""
        today = datetime.now()
        day_map = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        target_day = day_map.get(day_name.lower(), 0)
        
        days_ahead = target_day - today.weekday()
        if days_ahead < 0:  # Target day already happened this week
            return None  # This week's occurrence has passed
        return (today + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
    
    def _month_name_to_number(self, month_name: str) -> int:
        """Convert month name to number."""
        months = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4,
            'may': 5, 'june': 6, 'july': 7, 'august': 8,
            'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        return months.get(month_name.lower(), 1)
    
    def _extract_add_task_details(self, user_input: str, match) -> Dict:
        """Extract details for add task command."""
        title = match.group(1) if match.groups() else ""
        
        # Extract description
        description = ""
        desc_patterns = [
            r'description[:\s]+([^,]+)',
            r'about[:\s]+([^,]+)',
            r'for[:\s]+([^,]+)',
        ]
        
        for pattern in desc_patterns:
            desc_match = re.search(pattern, user_input, re.IGNORECASE)
            if desc_match:
                description = desc_match.group(1).strip()
                break
        
        # Extract tags - improved logic
        tags = self._extract_tags_from_text(user_input, title)
        
        return {
            'title': title,
            'description': description,
            'tags': tags
        }
    
    def _extract_tags_from_text(self, user_input: str, title: str) -> List[str]:
        """Extract tags from natural language input."""
        tags = []
        user_input_lower = user_input.lower()
        
        # 1. Extract explicit tags (after "tags:" or "category:")
        explicit_tag_patterns = [
            r'tags?[:\s]+([^,]+)',
            r'category[:\s]+([^,]+)',
            r'with\s+tags?\s+([^,]+)',
        ]
        
        for pattern in explicit_tag_patterns:
            tag_match = re.search(pattern, user_input, re.IGNORECASE)
            if tag_match:
                explicit_tags = [tag.strip() for tag in tag_match.group(1).split(',')]
                tags.extend(explicit_tags)
                break
        
        # 2. Extract implicit tags based on keywords in the text
        implicit_tags = self._extract_implicit_tags(user_input_lower, title.lower())
        tags.extend(implicit_tags)
        
        # 3. Extract time-based tags
        time_tags = self._extract_time_tags(user_input_lower)
        tags.extend(time_tags)
        
        # Remove duplicates and empty tags
        unique_tags = list(set([tag.strip() for tag in tags if tag.strip()]))
        
        return unique_tags
    
    def _extract_implicit_tags(self, text: str, title: str) -> List[str]:
        """Extract implicit tags based on keywords and context."""
        tags = []
        
        # Common task categories and their keywords
        category_keywords = {
            'work': ['work', 'job', 'office', 'meeting', 'presentation', 'client', 'project', 'deadline', 'report', 'email', 'call', 'conference'],
            'personal': ['personal', 'home', 'family', 'friend', 'relationship', 'life'],
            'shopping': ['buy', 'purchase', 'shop', 'grocery', 'store', 'market', 'mall', 'online'],
            'health': ['health', 'medical', 'doctor', 'dentist', 'exercise', 'gym', 'workout', 'fitness', 'wellness', 'appointment'],
            'finance': ['money', 'finance', 'bank', 'bill', 'payment', 'budget', 'expense', 'investment', 'tax', 'insurance'],
            'learning': ['learn', 'study', 'course', 'book', 'read', 'education', 'training', 'skill', 'knowledge', 'research'],
            'travel': ['travel', 'trip', 'vacation', 'flight', 'hotel', 'booking', 'reservation', 'destination'],
            'cleaning': ['clean', 'organize', 'tidy', 'declutter', 'laundry', 'dishes', 'housework'],
            'cooking': ['cook', 'meal', 'food', 'recipe', 'dinner', 'lunch', 'breakfast', 'kitchen'],
            'entertainment': ['movie', 'game', 'music', 'party', 'event', 'fun', 'entertainment', 'hobby'],
            'urgent': ['urgent', 'asap', 'emergency', 'critical', 'immediate', 'rush'],
            'important': ['important', 'priority', 'key', 'essential', 'vital'],
            'routine': ['routine', 'daily', 'weekly', 'monthly', 'regular', 'habit'],
        }
        
        # Check for category keywords in the text
        for category, keywords in category_keywords.items():
            if any(keyword in text for keyword in keywords):
                tags.append(category)
        
        # Extract specific items that might be tags
        specific_items = [
            'groceries', 'milk', 'bread', 'eggs', 'vegetables', 'fruits',
            'meeting', 'call', 'email', 'presentation', 'report',
            'exercise', 'gym', 'workout', 'running', 'yoga',
            'doctor', 'dentist', 'appointment', 'checkup',
            'bill', 'payment', 'rent', 'mortgage', 'insurance',
            'book', 'reading', 'study', 'course', 'class',
            'cleaning', 'laundry', 'dishes', 'organizing',
            'cooking', 'meal', 'dinner', 'lunch', 'breakfast'
        ]
        
        for item in specific_items:
            if item in text:
                tags.append(item)
        
        return tags
    
    def _extract_time_tags(self, text: str) -> List[str]:
        """Extract time-based tags."""
        time_tags = []
        
        # Time-based patterns
        if re.search(r'\btoday\b', text):
            time_tags.append('today')
        if re.search(r'\btomorrow\b', text):
            time_tags.append('tomorrow')
        if re.search(r'\bthis\s+week\b', text):
            time_tags.append('this_week')
        if re.search(r'\bnext\s+week\b', text):
            time_tags.append('next_week')
        if re.search(r'\bthis\s+month\b', text):
            time_tags.append('this_month')
        if re.search(r'\bnext\s+month\b', text):
            time_tags.append('next_month')
        if re.search(r'\bweekend\b', text):
            time_tags.append('weekend')
        if re.search(r'\bweekday\b', text):
            time_tags.append('weekday')
        
        # Time of day
        if re.search(r'\bmorning\b', text):
            time_tags.append('morning')
        if re.search(r'\bafternoon\b', text):
            time_tags.append('afternoon')
        if re.search(r'\bevening\b', text):
            time_tags.append('evening')
        if re.search(r'\bnight\b', text):
            time_tags.append('night')
        
        return time_tags
    
    def _extract_search_details(self, user_input: str, match) -> Dict:
        """Extract details for search command."""
        query = match.group(1) if match.groups() else ""
        return {'query': query}
    
    def _extract_update_details(self, user_input: str, match) -> Dict:
        """Extract details for update command."""
        task_id = int(match.group(1)) if match.groups() else None
        new_value = match.group(2) if len(match.groups()) > 1 else ""
        
        # Determine what field is being updated
        field = 'status'  # default
        if any(word in user_input.lower() for word in ['priority', 'important']):
            field = 'priority'
        elif any(word in user_input.lower() for word in ['title', 'name']):
            field = 'title'
        elif any(word in user_input.lower() for word in ['description', 'desc']):
            field = 'description'
        
        # Normalize the value
        if field == 'status':
            if any(word in new_value.lower() for word in ['complete', 'done', 'finish']):
                new_value = 'completed'
            elif any(word in new_value.lower() for word in ['progress', 'working']):
                new_value = 'in_progress'
            else:
                new_value = 'pending'
        elif field == 'priority':
            if any(word in new_value.lower() for word in ['high', 'urgent', 'important']):
                new_value = 'high'
            elif any(word in new_value.lower() for word in ['low', 'minor']):
                new_value = 'low'
            else:
                new_value = 'medium'
        
        return {
            'task_id': task_id,
            'field': field,
            'value': new_value
        }
    
    def _extract_delete_details(self, user_input: str, match) -> Dict:
        """Extract details for delete command."""
        task_id = int(match.group(1)) if match.groups() else None
        return {'task_id': task_id}
    
    def _infer_command(self, user_input: str) -> Dict:
        """Infer command type from natural language input."""
        user_input_lower = user_input.lower()
        
        # Simple keyword-based inference
        if any(word in user_input_lower for word in ['add', 'create', 'new', 'make']):
            return {
                'command_type': 'add_task',
                'confidence': 0.7,
                'raw_input': user_input,
                'title': self._extract_title_from_text(user_input)
            }
        elif any(word in user_input_lower for word in ['find', 'search', 'look', 'show']):
            return {
                'command_type': 'search_tasks',
                'confidence': 0.7,
                'raw_input': user_input,
                'query': self._extract_query_from_text(user_input)
            }
        elif any(word in user_input_lower for word in ['list', 'all', 'tasks']):
            return {
                'command_type': 'list_tasks',
                'confidence': 0.8,
                'raw_input': user_input
            }
        elif any(word in user_input_lower for word in ['stats', 'statistics', 'summary']):
            return {
                'command_type': 'show_stats',
                'confidence': 0.8,
                'raw_input': user_input
            }
        else:
            return {
                'command_type': 'unknown',
                'confidence': 0.0,
                'raw_input': user_input,
                'error': 'Could not understand command'
            }
    
    def _extract_title_from_text(self, text: str) -> str:
        """Extract potential task title from text."""
        # Simple heuristic: look for quoted text or first meaningful phrase
        quote_match = re.search(r'["\']([^"\']+)["\']', text)
        if quote_match:
            return quote_match.group(1)
        
        # Otherwise, take the first meaningful phrase
        words = text.split()
        command_words = ['add', 'create', 'new', 'task', 'a', 'an']
        meaningful_words = [word for word in words if word.lower() not in command_words]
        
        if meaningful_words:
            return ' '.join(meaningful_words[:3])  # Take first 3 meaningful words
        return text
    
    def _extract_query_from_text(self, text: str) -> str:
        """Extract search query from text."""
        # Remove command words
        command_words = ['find', 'search', 'look', 'for', 'show', 'me', 'tasks', 'about']
        words = [word for word in text.split() if word.lower() not in command_words]
        return ' '.join(words)
    
    def format_response(self, parsed_command: Dict) -> str:
        """Format parsed command into human-readable response."""
        if parsed_command['command_type'] == 'unknown':
            return f"I'm not sure what you mean by '{parsed_command['raw_input']}'. Try saying something like 'add a new task' or 'search for meetings'."
        
        confidence = parsed_command.get('confidence', 0)
        if confidence < 0.5:
            return f"I think you want to {parsed_command['command_type'].replace('_', ' ')}, but I'm not sure. Could you rephrase that?"
        
        return f"Understood! I'll {parsed_command['command_type'].replace('_', ' ')} for you." 