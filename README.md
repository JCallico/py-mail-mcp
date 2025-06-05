# Email MCP Server

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

Or using pip:
```bash
pip install -r requirements.txt
```

## Configuration

### Option 1: Interactive Configuration (Recommended)

Run the interactive configuration script to set up your email provider:

```bash
python configure_email.py
```

This script supports:
- **Gmail** (with App Password setup instructions)
- **Outlook/Hotmail** (with security configuration guidance)
- **Yahoo Mail** (with 2FA and App Password setup)
- **Custom providers** (manual IMAP/SMTP configuration)

### Option 2: Manual Configuration

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

### Pre-configured Provider Settings

**Gmail:**
- IMAP: imap.gmail.com:993
- SMTP: smtp.gmail.com:587
- Requires App Password if 2FA is enabled
- Generate at: https://myaccount.google.com/apppasswords

**Outlook/Hotmail:**
- IMAP: outlook.office365.com:993 (or imap-mail.outlook.com:993)
- SMTP: smtp.office365.com:587 (or smtp-mail.outlook.com:587)
- May require App Password for 2FA accounts

**Yahoo Mail:**
- IMAP: imap.mail.yahoo.com:993
- SMTP: smtp.mail.yahoo.com:587
- Requires App Password for 2FA accounts

## Usage

### Starting the Server

Start the MCP server directly:
```bash
mcp run server-email.py
```

Or run the main entry point to see available operations:
```bash
python main.py
```

### Claude Desktop Configuration

Configure the Email MCP server in Claude Desktop by adding this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "email": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/py-mail-mcp/",
        "--with",
        "mcp[cli]",
        "mcp",
        "run",
        "/path/to/py-mail-mcp/server-email.py"
      ],
      "env": {
        "SERVER_URL": "http://127.0.0.1:8001"
      }      
    }
  }
}
```

**Configuration file locations:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

## Available Tools

### Mailbox Management Tools
- **`list_folders()`** - List all email folders/mailboxes
- **`create_folder(name)`** - Create a new folder
- **`delete_folder(name)`** - Delete an existing folder

### Message Management Tools
- **`list_recent_emails(folder, limit=50)`** - List recent emails in a folder
- **`search_email(folder, query)`** - Search for emails containing specific text
- **`read_email(folder, message_id)`** - Get full email content including headers and body
- **`send_email(to, subject, body, cc=None, bcc=None, attachments=None)`** - Send new email
- **`move_email(folder, message_id, target_folder)`** - Move email between folders
- **`delete_email(folder, message_id)`** - Delete an email permanently
- **`mark_email(folder, message_id, flag)`** - Mark email as read/unread/flagged/unflagged

## Dependencies

All dependencies are managed through `pyproject.toml` and `requirements.txt`:

- **Python** >= 3.13
- **mcp[cli]** >= 1.6.0 - Model Context Protocol framework
- **python-dotenv** >= 1.0.0 - Environment variable management
- **asyncio** >= 3.4.3 - Asynchronous I/O support
- **aiosmtplib** >= 2.0.2 - Async SMTP client
- **aioimaplib** >= 1.0.1 - Async IMAP client
- **email-validator** >= 2.1.0 - Email address validation
- **python-multipart** >= 0.0.6 - Multipart form data handling

## Project Structure

```
py-mail-mcp/
├── server-email.py         # Main MCP server implementation
├── main.py                 # Package entry point with usage examples
├── configure_email.py      # Interactive email configuration script
├── pyproject.toml         # Project dependencies and metadata
├── requirements.txt       # Pip-compatible dependencies list
├── README.md              # This documentation file
├── LICENSE.md             # MIT License file
├── .env.template          # Template for email configuration
├── .env                   # Active environment variables (gitignored)
├── .python-version        # Python version requirement (3.13)
├── .gitignore            # Git ignore patterns
├── uv.lock               # UV package manager lock file
└── server-email.log      # Runtime log file (auto-generated)
```

## Logging & Monitoring

The server implements comprehensive logging for debugging and monitoring:

- **Log File**: `server-email.log` (auto-created in project directory)
- **Log Contents**: 
  - Connection attempts and authentication status
  - IMAP/SMTP operations and responses
  - Error messages with detailed stack traces
  - Performance and timing information
- **Log Format**: Timestamped entries with log levels (INFO, ERROR, WARNING)
- **Error Handling**: Automatic stderr redirection to log file for silent operation

## Error Handling & Security

### Robust Error Handling
- Email address validation with detailed error messages
- Graceful handling of connection timeouts and network issues
- Authentication failure detection and recovery
- Invalid mailbox/message operation protection
- Safe attachment handling with file validation

### Security Features
- **Encrypted Connections**: SSL/TLS for all IMAP/SMTP communications
- **Credential Protection**: Environment-based configuration (no hardcoded secrets)
- **App Password Support**: Compatible with 2FA-enabled accounts
- **Input Validation**: Comprehensive validation of all user inputs
- **File Permissions**: Automatic `.env` file permission restriction (600)

## Recent Updates

- **Enhanced Provider Support**: Added `configure_email.py` with guided setup for major email providers
- **Improved Gmail Compatibility**: Fixed IMAP mailbox listing with proper command syntax
- **Comprehensive Logging**: Added detailed logging system with `server-email.log` output
- **Better Error Handling**: Enhanced connection management and authentication error recovery
- **Multiple Environment Configs**: Support for provider-specific `.env` files
- **UV Package Manager**: Added `uv.lock` for reproducible dependency management

## Troubleshooting

### Common Issues

1. **Authentication Failures**:
   - Ensure 2FA is enabled and App Password is generated
   - Verify credentials in `.env` file
   - Check `server-email.log` for detailed error messages

2. **Connection Timeouts**:
   - Verify IMAP/SMTP server addresses and ports
   - Check firewall and network connectivity
   - Review provider-specific security settings

3. **Folder/Mailbox Issues**:
   - Different providers use different folder naming conventions
   - Gmail uses labels, others use traditional folders
   - Check folder names with `list_folders()` tool

### Debug Mode

Enable detailed logging by checking the `server-email.log` file after operations. All IMAP commands, responses, and errors are logged with timestamps.

## License

MIT License - see [LICENSE.md](LICENSE.md) for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Update documentation
6. Submit a pull request

For questions or issues, please check the `server-email.log` file first, then open an issue with relevant log excerpts.
