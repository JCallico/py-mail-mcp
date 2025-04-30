# Mail MCP Server

A Model Context Protocol (MCP) server implementation that provides programmatic access to email functionality through IMAP and SMTP protocols. This server enables seamless email operations with comprehensive support for mailbox management, message handling, and email composition.

## Features

### Mailbox Management
- List all mailboxes/folders
- Create new mailboxes
- Delete existing mailboxes

### Message Operations
- List messages in folders with pagination
- Search messages by content
- Get full message content including attachments
- Send new messages with CC, BCC, and attachments
- Move messages between folders
- Delete messages
- Mark messages as read/unread/flagged

### Email Composition
- Support for plain text messages
- CC and BCC recipients
- File attachments
- Email address validation

## Prerequisites

- Python 3.13 or higher
- IMAP-enabled email account
- SMTP-enabled email account

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd py-mail-mcp
```

2. Install dependencies using `uv`:
```bash
uv pip install -r requirements.txt
```

## Configuration

1. Copy the template environment file:
```bash
cp .env.template .env
```

2. Edit the `.env` file with your email settings:
```bash
# Email account credentials
EMAIL_USER=your.email@example.com
EMAIL_PASSWORD=your_email_password

# IMAP settings
IMAP_HOST=imap.example.com
IMAP_PORT=993  # Default port for IMAP over SSL

# SMTP settings
SMTP_HOST=smtp.example.com
SMTP_PORT=587  # Default port for SMTP with TLS
```

Common email provider settings:

Gmail:
- IMAP: imap.gmail.com:993
- SMTP: smtp.gmail.com:587
- Requires App Password if 2FA is enabled

Outlook:
- IMAP: outlook.office365.com:993
- SMTP: smtp.office365.com:587

Yahoo Mail:
- IMAP: imap.mail.yahoo.com:993
- SMTP: smtp.mail.yahoo.com:587

Note: For providers that use 2FA, you'll need to generate an App Password.

## Claude Desktop Configuration

Configure the Mail MCP server in Claude Desktop:

```json
{
  "Mail": {
    "command": "/path/to/uv",
    "args": [
      "pip",
      "install",
      "--system",
      "mcp[cli]>=1.6.0",
      "aiosmtplib>=2.0.2",
      "aioimaplib>=1.0.1",
      "email-validator>=2.1.0",
      "python-multipart>=0.0.6",
      "python-dotenv>=1.0.0",
      "--",
      "python",
      "-m",
      "mcp",
      "run",
      "/path/to/server-email.py"
    ],
    "env": {
      "SERVER_URL": "http://127.0.0.1:8001",
      "PYTHONPATH": "/path/to/py-mail-mcp"
    }
  }
}
```

Location:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

## Available Tools

### Mailbox Tools
- `list_folders()` - List all mail folders
- `create_folder(name)` - Create new folder
- `delete_folder(name)` - Delete folder

### Message Tools
- `list_recent_emails(folder, limit=50)` - List recent emails
- `search_email(folder, query)` - Search for emails
- `read_email(folder, message_id)` - Get email content
- `send_email(to, subject, body, cc=None, bcc=None, attachments=None)` - Send email
- `move_email(folder, message_id, target_folder)` - Move email
- `delete_email(folder, message_id)` - Delete email
- `mark_email(folder, message_id, flag)` - Mark email (read/unread/flagged)

## Dependencies

- Python >= 3.13
- mcp[cli] >= 1.6.0
- python-dotenv >= 1.0.0
- asyncio >= 3.4.3
- aiosmtplib >= 2.0.2
- aioimaplib >= 1.0.1
- email-validator >= 2.1.0
- python-multipart >= 0.0.6

## Project Structure

- `server-email.py`: Main MCP server implementation
- `main.py`: Package entry point with usage examples
- `pyproject.toml`: Project dependencies and configuration
- `.env.template`: Template for email configuration
- `.env`: Environment variables (not tracked in git)
- `.python-version`: Python version requirement
- `email_server.log`: Log file containing server operations and errors

## Logging

The server now implements a comprehensive logging system:

- All operations and errors are logged to `email_server.log` in the script directory
- Console output is suppressed for silent operation
- Detailed logging of IMAP/SMTP operations for troubleshooting
- Error messages with stack traces for debugging
- Timestamp and log level categorization
- Custom error redirection from stderr to log file

## Error Handling

The server includes comprehensive error handling for:
- Email address validation
- Connection errors
- Authentication errors
- Invalid mailbox/message operations
- Attachment handling

## Security

- Uses SSL/TLS for secure connections
- Supports app-specific passwords for 2FA
- Environment variable configuration for credentials
- Input validation
- Secure attachment handling

## Recent Changes

- **04/30/2025**: Improved IMAP mailbox listing with proper command syntax for Gmail compatibility
- **04/30/2025**: Added comprehensive logging system with output redirection to `email_server.log`
- **04/30/2025**: Fixed error handling for IMAP connection and authentication
- **04/30/2025**: Optimized parsing of LIST command responses

## License

MIT License

Copyright (c) 2025

See LICENSE file for details.