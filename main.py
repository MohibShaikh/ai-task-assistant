#!/usr/bin/env python3
"""
AI Task Assistant with Vector Memory
A powerful task management system using semantic search and vector storage.
"""

import sys
import os
from task_assistant import TaskAssistant
from utils import print_welcome_message, print_goodbye_message, get_colored_prompt
import colorama
from colorama import Fore, Style

def main():
    """Main entry point for the AI Task Assistant."""
    # Initialize colorama for cross-platform colored output
    colorama.init()
    
    try:
        # Print welcome message
        print_welcome_message()
        
        # Initialize the task assistant
        assistant = TaskAssistant()
        
        # Run interactive mode
        assistant.run_interactive()
        
    except KeyboardInterrupt:
        print_goodbye_message()
    except Exception as e:
        print(f"{Fore.RED}An error occurred: {e}{Style.RESET_ALL}")
        print("Please check your installation and try again.")
        sys.exit(1)
    finally:
        # Clean up colorama
        colorama.deinit()

if __name__ == "__main__":
    main() 