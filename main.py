"""
Script Name: main.py
Description: Main entry point for the Email MCP Server package, providing
            example usage and package-level functionality.
Author: JCallico
Date Created: 2025-04-29
Version: 0.1.0
Python Version: >= 3.13
Dependencies: None
License: MIT
"""

def main():
    print("Email MCP Server")
    print("Available operations:")
    print("\nMailbox Management:")
    print("- List mailboxes")
    print("- Create mailbox")
    print("- Delete mailbox")
    print("\nMessage Operations:")
    print("- List messages in folder")
    print("- Search messages")
    print("- Get message content")
    print("- Send message")
    print("- Move message")
    print("- Delete message")
    print("- Mark message (read/unread/flagged)")
    print("\nStart the server:")
    print("$ mcp run server-email.py")


if __name__ == "__main__":
    main()
