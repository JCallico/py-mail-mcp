"""
Script Name: configure_email.py
Description: Interactive configuration script for email settings.
            Helps users set up their .env file with correct email server settings
            for popular email providers.
Author: JCallico
Date Created: 2025-04-29
Version: 0.1.0
Python Version: >= 3.13
Dependencies: None
License: MIT

Usage:
    $ python configure_email.py
"""

import os
from getpass import getpass
from typing import Dict, NamedTuple
from pathlib import Path

class EmailProvider(NamedTuple):
    name: str
    imap_host: str
    imap_port: int
    smtp_host: str
    smtp_port: int
    instructions: str

# Email provider configurations
PROVIDERS = {
    "1": EmailProvider(
        "Gmail",
        "imap.gmail.com",
        993,
        "smtp.gmail.com",
        587,
        """
For Gmail, you need to:
1. Enable 2-Step Verification: https://myaccount.google.com/security
2. Generate an App Password: https://myaccount.google.com/apppasswords
   - Select 'Mail' as the app
   - Use the generated 16-character password
"""
    ),
    "2": EmailProvider(
        "Outlook/Hotmail",
        "outlook.office365.com",
        993,
        "smtp.office365.com",
        587,
        """
For Outlook/Hotmail:
1. If you have 2-Step Verification enabled:
   - Generate an app password: https://account.live.com/proofs/AppPassword
2. Otherwise:
   - Use your regular email password
   - You may need to enable "Less secure app access"
"""
    ),
    "3": EmailProvider(
        "Yahoo Mail",
        "imap.mail.yahoo.com",
        993,
        "smtp.mail.yahoo.com",
        587,
        """
For Yahoo Mail:
1. Enable 2-Step Verification: https://login.yahoo.com/account/security
2. Generate an app password:
   - Go to Account Security
   - Click 'Generate app password'
   - Select 'Other app'
   - Use the generated password
"""
    ),
    "4": EmailProvider(
        "Custom",
        "",
        993,
        "",
        587,
        "Please enter your custom IMAP and SMTP server details."
    )
}

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Print the configuration script header."""
    print("Email MCP Server Configuration")
    print("=============================")
    print("This script will help you configure your email settings.\n")

def get_provider_selection() -> EmailProvider:
    """Prompt user to select an email provider."""
    while True:
        print("\nSupported email providers:")
        for key, provider in PROVIDERS.items():
            print(f"{key}. {provider.name}")
        
        choice = input("\nSelect your email provider (1-4): ").strip()
        
        if choice in PROVIDERS:
            provider = PROVIDERS[choice]
            print(f"\n{provider.instructions}")
            return provider
        
        print("Invalid selection. Please try again.")

def get_custom_provider() -> EmailProvider:
    """Get custom provider settings from user."""
    print("\nEnter your custom email server settings:")
    imap_host = input("IMAP Server Host: ").strip()
    imap_port = int(input("IMAP Server Port [993]: ").strip() or "993")
    smtp_host = input("SMTP Server Host: ").strip()
    smtp_port = int(input("SMTP Server Port [587]: ").strip() or "587")
    
    return EmailProvider(
        "Custom",
        imap_host,
        imap_port,
        smtp_host,
        smtp_port,
        ""
    )

def get_user_credentials() -> tuple:
    """Get email address and password from user."""
    print("\nEnter your email credentials:")
    email = input("Email Address: ").strip()
    password = getpass("Password/App Password: ")
    return email, password

def write_env_file(email: str, password: str, provider: EmailProvider):
    """Write the configuration to .env file."""
    env_content = f"""# Email account credentials
EMAIL_USER={email}
EMAIL_PASSWORD={password}

# IMAP settings
IMAP_HOST={provider.imap_host}
IMAP_PORT={provider.imap_port}

# SMTP settings
SMTP_HOST={provider.smtp_host}
SMTP_PORT={provider.smtp_port}
"""
    
    env_path = Path(".env")
    if env_path.exists():
        backup_path = Path(".env.backup")
        env_path.rename(backup_path)
        print(f"\nCreated backup of existing .env file as {backup_path}")
    
    env_path.write_text(env_content)
    env_path.chmod(0o600)  # Set file permissions to owner read/write only
    
    print(f"\nConfiguration saved to {env_path}")
    print("File permissions set to owner read/write only")

def main():
    """Main configuration function."""
    clear_screen()
    print_header()
    
    # Get provider settings
    provider = get_provider_selection()
    if provider.name == "Custom":
        provider = get_custom_provider()
    
    # Get user credentials
    email, password = get_user_credentials()
    
    # Save configuration
    write_env_file(email, password, provider)
    
    print("\nConfiguration complete!")
    print("You can now start the email MCP server with:")
    print("$ mcp run server-email.py")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nConfiguration cancelled.")
    except Exception as e:
        print(f"\nError during configuration: {str(e)}")