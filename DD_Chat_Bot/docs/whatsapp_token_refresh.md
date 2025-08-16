# WhatsApp Meta API Token Refresh Guide

This guide explains how to refresh your WhatsApp API token when it expires.

## When to Refresh Your Token

You'll need to refresh your token when you see this error in the logs:
```
Error validating access token: Session has expired
```

## Steps to Generate a New Token

1. **Log in to Meta Developer Dashboard**
   - Go to [Meta Developer Dashboard](https://developers.facebook.com/apps/)
   - Log in with your credentials
   - Select your WhatsApp business app

2. **Navigate to WhatsApp API Settings**
   - In your app dashboard, go to "WhatsApp" > "API Setup"
   - Alternatively, go to "App Settings" > "Advanced" > "Access Tokens"

3. **Generate a New Permanent Token**
   - Look for "Permanent/System Users" or "Generate New Token"
   - Select the appropriate permissions:
     - `whatsapp_business_messaging`
     - `whatsapp_business_management`
   - Set the token expiration to "Never" if available

4. **Copy the New Token**
   - Copy the newly generated token

5. **Update Your .env File**
   - Open your project's `.env` file
   - Replace the value of `WHATSAPP_API_TOKEN` with your new token
   - Save the file

6. **Restart Your Application**
   - Restart the server to apply the new token

## Verifying Your Token

After updating your token, you can verify it's working correctly by:

1. Sending a test message to your WhatsApp number
2. Checking the server logs for successful message delivery
3. Accessing the `/debug` endpoint to confirm the token is loaded correctly

## Token Security Best Practices

- Never share your token publicly
- Store tokens securely in environment variables
- Rotate tokens regularly even if they don't expire
- Use system users with minimal required permissions

## Troubleshooting

If you're still experiencing issues after refreshing your token:

1. Ensure your business account is active and in good standing
2. Verify that your phone number ID is correct
3. Check that you have the proper permissions set for your token
4. Look for any WhatsApp Business API status updates or outages
