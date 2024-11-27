# Helper-

# Telegram Account Deletion Bot

This bot automates the deletion of Telegram accounts. It can log in to Telegram, delete accounts, or request account deletion (if two-step verification is enabled).

## Features

1. Deletes accounts if login is successful.
2. Requests account deletion (7-day wait) if two-step verification is enabled.
3. Tracks pending deletion requests persistently using a JSON file.
4. Sends reminders after 7 days to finalize account deletions.
5. Allows users to cancel pending deletion requests.
