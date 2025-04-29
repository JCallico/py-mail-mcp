"""
Script Name: server-email.py
Description: MCP server implementation for email operations. Provides programmatic
            access to email functionality through IMAP and SMTP protocols with support
            for common email operations like sending, receiving, searching, and folder management.
Author: JCallico
Date Created: 2025-04-29
Version: 0.1.0
Python Version: >= 3.13
Dependencies: 
    - mcp[cli]>=0.1.0
    - python-dotenv>=1.0.0
    - aiosmtplib>=2.0.2
    - aioimaplib>=1.0.1
    - email-validator>=2.1.0
License: MIT

Usage:
    Start the server:
    $ mcp run server-email.py
    
    The server will be available at http://127.0.0.1:6274
"""

import asyncio
import json
import os
import email
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

from dotenv import load_dotenv, find_dotenv
from mcp.server.fastmcp import FastMCP
import aiosmtplib
from aioimaplib import aioimaplib
from email_validator import validate_email, EmailNotValidError

# Try to find and load .env file
env_path = find_dotenv(usecwd=True)
if env_path:
    print(f"Found .env file at: {env_path}")
    # Load env vars and make them available to child processes
    load_dotenv(env_path)
    for key, value in os.environ.items():
        if key.startswith(('EMAIL_', 'IMAP_', 'SMTP_')):
            print(f"Setting environment variable: {key}")
            os.environ[key] = value
else:
    print("Warning: No .env file found")

# Print current working directory and environment variables for debugging
print(f"Current working directory: {os.getcwd()}")
print("Environment variables:")
print(f"EMAIL_USER: {os.getenv('EMAIL_USER', 'Not set')}")
print(f"IMAP_HOST: {os.getenv('IMAP_HOST', 'Not set')}")
print(f"SMTP_HOST: {os.getenv('SMTP_HOST', 'Not set')}")

server_url = os.getenv("SERVER_URL", "http://127.0.0.1:6274")
print(f"Using server URL: {server_url}")

# Initialize MCP server
mcp = FastMCP("Email", server_url=server_url)

# Global connections
imap_client = None
smtp_client = None

async def ensure_imap_connection():
    """Ensure IMAP connection is established and authenticated."""
    global imap_client
    
    try:
        # Check if client exists and is authenticated
        if imap_client is None or not hasattr(imap_client, 'protocol') or imap_client.protocol.state != 'AUTH':
            imap_host = os.getenv("IMAP_HOST")
            imap_port = int(os.getenv("IMAP_PORT", "993"))
            email_user = os.getenv("EMAIL_USER")
            email_pass = os.getenv("EMAIL_PASSWORD")
            
            if not all([imap_host, email_user, email_pass]):
                raise ValueError("Missing IMAP credentials in environment variables")
            
            print(f"Connecting to IMAP server {imap_host}:{imap_port}")
            
            # If client exists but is not authenticated, close it first
            if imap_client is not None:
                try:
                    await imap_client.logout()
                except:
                    pass
                imap_client = None
            
            # Create new connection
            imap_client = aioimaplib.IMAP4_SSL(imap_host, imap_port)
            await imap_client.wait_hello_from_server()
            
            # Authenticate
            print("Authenticating with IMAP server...")
            login_result = await imap_client.login(email_user, email_pass)

            if imap_client.protocol.state != "AUTH":
                raise ValueError(f"Failed to authenticate with IMAP server: {login_result}")      
            
            print("Successfully authenticated with IMAP server")
    
    except Exception as e:
        print(f"IMAP connection error: {str(e)}", file=sys.stderr)
        # Reset the client on error so we can try to reconnect
        if imap_client is not None:
            try:
                await imap_client.logout()
            except:
                pass
        imap_client = None
        raise

async def ensure_smtp_connection():
    """Ensure SMTP connection is established."""
    global smtp_client
    
    try:
        if smtp_client is None or not smtp_client.is_connected:
            smtp_host = os.getenv("SMTP_HOST")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            email_user = os.getenv("EMAIL_USER")
            email_pass = os.getenv("EMAIL_PASSWORD")
            
            if not all([smtp_host, email_user, email_pass]):
                raise ValueError("Missing SMTP credentials in environment variables")
            
            print(f"Connecting to SMTP server {smtp_host}:{smtp_port}")
            
            # Create new connection
            if smtp_client:
                try:
                    await smtp_client.quit()
                except:
                    pass
            
            smtp_client = aiosmtplib.SMTP(
                hostname=smtp_host,
                port=smtp_port,
                use_tls=False,
                start_tls=True  # This will automatically handle STARTTLS
            )
            
            # Connect and authenticate
            print("Establishing connection and authenticating...")
            await smtp_client.connect()
            await smtp_client.login(email_user, email_pass)
            print("Successfully connected and authenticated with SMTP server")
            
    except Exception as e:
        print(f"SMTP connection error: {str(e)}", file=sys.stderr)
        # Reset client on error
        if smtp_client:
            try:
                await smtp_client.quit()
            except:
                pass
        smtp_client = None
        raise

@mcp.resource("email://mailbox/list")
async def list_mailboxes() -> str:
    """List all mailboxes/folders in the email account."""
    await ensure_imap_connection()
    # Use '' as reference name (root level) and '*' to match all mailboxes
    response = await imap_client.list('', '*')
    folders = []
    
    for line in response.lines:
        if line:
            parts = line.decode().split('" "')
            if len(parts) >= 2:
                folder_name = parts[1].strip('"')
                folders.append(folder_name)
    
    return json.dumps(folders)

@mcp.resource("email://mailbox/create/{name}")
async def create_mailbox(name: str) -> str:
    """Create a new mailbox/folder."""
    await ensure_imap_connection()
    response = await imap_client.create(name)
    return json.dumps({"status": "success", "message": f"Created mailbox {name}"})

@mcp.resource("email://mailbox/delete/{name}")
async def delete_mailbox(name: str) -> str:
    """Delete a mailbox/folder."""
    await ensure_imap_connection()
    response = await imap_client.delete(name)
    return json.dumps({"status": "success", "message": f"Deleted mailbox {name}"})

@mcp.resource("email://messages/list/{folder}/{limit}")
async def list_messages(folder: str, limit: int = 50) -> str:
    """List messages in a folder with optional limit."""
    try:
        await ensure_imap_connection()
        
        print(f"Selecting folder: {folder}")
        select_response = await imap_client.select(folder)
        if select_response.result != "OK":
            return json.dumps({
                "error": f"Failed to select folder {folder}: {select_response.lines[0].decode()}"
            })
        
        print(f"Searching for messages...")
        search_response = await imap_client.search("ALL")
        if search_response.result != "OK":
            return json.dumps({
                "error": f"Failed to search folder: {search_response.lines[0].decode()}"
            })
            
        message_numbers = search_response.lines[0].decode().split()
        
        messages = []
        for num in message_numbers[-limit:]:  # Get the most recent messages
            fetch_response = await imap_client.fetch(num, "(RFC822.HEADER)")
            if fetch_response.result == "OK":
                email_data = email.message_from_bytes(fetch_response.lines[1])
                messages.append({
                    "id": num,
                    "subject": email_data["subject"],
                    "from": email_data["from"],
                    "date": email_data["date"],
                    "to": email_data["to"]
                })
        
        print(f"Found {len(messages)} messages")
        return json.dumps(messages)
        
    except Exception as e:
        print(f"Error listing messages: {str(e)}", file=sys.stderr)
        return json.dumps({"error": str(e)})

@mcp.resource("email://messages/search/{folder}/{query}")
async def search_messages(folder: str, query: str) -> str:
    """Search for messages in a folder."""
    try:
        await ensure_imap_connection()
        
        print(f"Selecting folder: {folder}")
        select_response = await imap_client.select(folder)
        if select_response.result != "OK":
            return json.dumps({
                "error": f"Failed to select folder {folder}: {select_response.lines[0].decode()}"
            })
        
        print(f"Searching for messages matching: {query}")
        search_response = await imap_client.search(f'TEXT "{query}"')
        if search_response.result != "OK":
            return json.dumps({
                "error": f"Failed to search folder: {search_response.lines[0].decode()}"
            })
        
        message_numbers = search_response.lines[0].decode().split()
        
        messages = []
        for num in message_numbers:
            fetch_response = await imap_client.fetch(num, "(RFC822.HEADER)")
            if fetch_response.result == "OK":
                email_data = email.message_from_bytes(fetch_response.lines[1])
                messages.append({
                    "id": num,
                    "subject": email_data["subject"],
                    "from": email_data["from"],
                    "date": email_data["date"],
                    "to": email_data["to"]
                })
        
        print(f"Found {len(messages)} matching messages")
        return json.dumps(messages)
        
    except Exception as e:
        print(f"Error searching messages: {str(e)}", file=sys.stderr)
        return json.dumps({"error": str(e)})

@mcp.resource("email://messages/get/{folder}/{message_id}")
async def get_message(folder: str, message_id: str) -> str:
    """Get a specific message's full content."""
    await ensure_imap_connection()
    
    await imap_client.select(folder)
    response = await imap_client.fetch(message_id, "(RFC822)")
    email_data = email.message_from_bytes(response.lines[1])
    
    # Extract message content
    body = ""
    attachments = []
    
    if email_data.is_multipart():
        for part in email_data.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode()
            elif part.get_content_type() != "multipart/alternative":
                attachments.append({
                    "filename": part.get_filename(),
                    "type": part.get_content_type()
                })
    else:
        body = email_data.get_payload(decode=True).decode()
    
    return json.dumps({
        "id": message_id,
        "subject": email_data["subject"],
        "from": email_data["from"],
        "to": email_data["to"],
        "date": email_data["date"],
        "body": body,
        "attachments": attachments
    })

@mcp.resource("email://messages/move/{folder}/{message_id}/{target_folder}")
async def move_message(folder: str, message_id: str, target_folder: str) -> str:
    """Move a message to a different folder."""
    await ensure_imap_connection()
    
    await imap_client.select(folder)
    await imap_client.copy(message_id, target_folder)
    await imap_client.store(message_id, "+FLAGS", "\\Deleted")
    await imap_client.expunge()
    
    return json.dumps({
        "status": "success",
        "message": f"Moved message {message_id} to {target_folder}"
    })

@mcp.resource("email://messages/delete/{folder}/{message_id}")
async def delete_message(folder: str, message_id: str) -> str:
    """Delete a message."""
    await ensure_imap_connection()
    
    await imap_client.select(folder)
    await imap_client.store(message_id, "+FLAGS", "\\Deleted")
    await imap_client.expunge()
    
    return json.dumps({
        "status": "success",
        "message": f"Deleted message {message_id}"
    })

@mcp.resource("email://messages/send/{to}/{subject}")
async def send_message(to: str, subject: str) -> str:
    """Send a new email message.
    
    Body and optional parameters (cc, bcc, attachments) should be provided in the request body as JSON:
    {
        "body": "Email content",
        "cc": "cc@example.com",  # optional
        "bcc": "bcc@example.com",  # optional
        "attachments": [  # optional
            {"path": "/path/to/file", "filename": "file.txt"}
        ]
    }
    """
    request_data = mcp.get_request_body() or {}
    body = request_data.get("body", "")
    cc = request_data.get("cc")
    bcc = request_data.get("bcc")
    attachments = request_data.get("attachments")
    
    await ensure_smtp_connection()
    
    # Validate email addresses
    try:
        validate_email(to)
        if cc:
            validate_email(cc)
        if bcc:
            validate_email(bcc)
    except EmailNotValidError as e:
        return json.dumps({
            "status": "error",
            "message": f"Invalid email address: {str(e)}"
        })
    
    # Create message
    msg = MIMEMultipart()
    msg["From"] = os.getenv("EMAIL_USER")
    msg["To"] = to
    msg["Subject"] = subject
    
    if cc:
        msg["Cc"] = cc
    if bcc:
        msg["Bcc"] = bcc
    
    # Add body
    msg.attach(MIMEText(body, "plain"))
    
    # Add attachments if any
    if attachments:
        for attachment in attachments:
            if "path" in attachment and "filename":
                with open(attachment["path"], "rb") as f:
                    part = MIMEApplication(f.read(), Name=attachment["filename"])
                    part["Content-Disposition"] = f'attachment; filename="{attachment["filename"]}"'
                    msg.attach(part)
    
    # Send the email
    await smtp_client.send_message(msg)
    
    return json.dumps({
        "status": "success",
        "message": "Email sent successfully"
    })

@mcp.resource("email://messages/mark/{folder}/{message_id}/{flag}")
async def mark_message(folder: str, message_id: str, flag: str) -> str:
    """Mark a message with a flag (read, unread, flagged, unflagged)."""
    await ensure_imap_connection()
    
    flag_map = {
        "read": "\\Seen",
        "unread": "\\Seen",
        "flagged": "\\Flagged",
        "unflagged": "\\Flagged"
    }
    
    if flag not in flag_map:
        return json.dumps({
            "status": "error",
            "message": f"Invalid flag: {flag}"
        })
    
    await imap_client.select(folder)
    if flag in ["unread", "unflagged"]:
        await imap_client.store(message_id, "-FLAGS", flag_map[flag])
    else:
        await imap_client.store(message_id, "+FLAGS", flag_map[flag])
    
    return json.dumps({
        "status": "success",
        "message": f"Marked message {message_id} as {flag}"
    })

# Add tools for executing email commands
@mcp.tool()
async def list_folders() -> str:
    """List all folders in the email account."""
    try:
        print("Executing list_folders command...")
        return await list_mailboxes()
    except Exception as e:
        print(f"Error executing list_folders: {str(e)}", file=sys.stderr)
        return json.dumps({"error": str(e)})

@mcp.tool()
async def create_folder(name: str) -> str:
    """Create a new folder in the email account."""
    try:
        print(f"Creating folder: {name}")
        return await create_mailbox(name)
    except Exception as e:
        print(f"Error creating folder: {str(e)}", file=sys.stderr)
        return json.dumps({"error": str(e)})

@mcp.tool()
async def delete_folder(name: str) -> str:
    """Delete a folder from the email account."""
    try:
        print(f"Deleting folder: {name}")
        return await delete_mailbox(name)
    except Exception as e:
        print(f"Error deleting folder: {str(e)}", file=sys.stderr)
        return json.dumps({"error": str(e)})

@mcp.tool()
async def search_email(folder: str, query: str) -> str:
    """Search for emails in a specific folder."""
    try:
        print(f"Searching in folder '{folder}' for: {query}")
        return await search_messages(folder, query)
    except Exception as e:
        print(f"Error searching emails: {str(e)}", file=sys.stderr)
        return json.dumps({"error": str(e)})

@mcp.tool()
async def send_email(to: str, subject: str, body: str = "", 
                    cc: Optional[str] = None, 
                    bcc: Optional[str] = None,
                    attachments: Optional[List[Dict]] = None) -> str:
    """Send an email with optional CC, BCC, and attachments."""
    try:
        print(f"Sending email to: {to}")
        print(f"Subject: {subject}")
        
        # Handle empty strings for optional parameters
        cc = None if not cc or cc in ["", "null"] else cc
        bcc = None if not bcc or bcc in ["", "null"] else bcc
        attachments = None if not attachments or attachments in ["", "null"] else attachments
        
        await ensure_smtp_connection()
        
        # Validate email addresses
        try:
            validate_email(to)
            if cc:
                validate_email(cc)
            if bcc:
                validate_email(bcc)
        except EmailNotValidError as e:
            return json.dumps({
                "status": "error",
                "message": f"Invalid email address: {str(e)}"
            })
        
        # Create message
        msg = MIMEMultipart()
        msg["From"] = os.getenv("EMAIL_USER")
        msg["To"] = to
        msg["Subject"] = subject
        
        if cc:
            msg["Cc"] = cc
        if bcc:
            msg["Bcc"] = bcc
        
        # Add body
        msg.attach(MIMEText(body, "plain"))
        
        # Add attachments if any
        if attachments and isinstance(attachments, list):
            for attachment in attachments:
                if "path" in attachment and "filename" in attachment:
                    with open(attachment["path"], "rb") as f:
                        part = MIMEApplication(f.read(), Name=attachment["filename"])
                        part["Content-Disposition"] = f'attachment; filename="{attachment["filename"]}"'
                        msg.attach(part)
        
        # Send the email
        await smtp_client.send_message(msg)
        
        return json.dumps({
            "status": "success",
            "message": "Email sent successfully"
        })
    except Exception as e:
        print(f"Error sending email: {str(e)}", file=sys.stderr)
        return json.dumps({
            "error": str(e)
        })

@mcp.tool()
async def read_email(folder: str, message_id: str) -> str:
    """Read a specific email's content."""
    try:
        print(f"Reading email {message_id} from folder: {folder}")
        return await get_message(folder, message_id)
    except Exception as e:
        print(f"Error reading email: {str(e)}", file=sys.stderr)
        return json.dumps({"error": str(e)})

@mcp.tool()
async def move_email(folder: str, message_id: str, target_folder: str) -> str:
    """Move an email to a different folder."""
    try:
        print(f"Moving email {message_id} from {folder} to {target_folder}")
        return await move_message(folder, message_id, target_folder)
    except Exception as e:
        print(f"Error moving email: {str(e)}", file=sys.stderr)
        return json.dumps({"error": str(e)})

@mcp.tool()
async def delete_email(folder: str, message_id: str) -> str:
    """Delete an email."""
    try:
        print(f"Deleting email {message_id} from folder: {folder}")
        return await delete_message(folder, message_id)
    except Exception as e:
        print(f"Error deleting email: {str(e)}", file=sys.stderr)
        return json.dumps({"error": str(e)})

@mcp.tool()
async def mark_email(folder: str, message_id: str, flag: str) -> str:
    """Mark an email with a flag (read, unread, flagged, unflagged)."""
    try:
        print(f"Marking email {message_id} as {flag}")
        return await mark_message(folder, message_id, flag)
    except Exception as e:
        print(f"Error marking email: {str(e)}", file=sys.stderr)
        return json.dumps({"error": str(e)})

@mcp.tool()
async def list_recent_emails(folder: str, limit: int = 50) -> str:
    """List recent emails in a folder."""
    try:
        print(f"Listing {limit} recent emails from folder: {folder}")
        return await list_messages(folder, limit)
    except Exception as e:
        print(f"Error listing emails: {str(e)}", file=sys.stderr)
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    print("Starting Email MCP Server...")
    
    try:
        mcp.run()
    except Exception as e:
        print(f"Server error: {str(e)}", file=sys.stderr)
        raise