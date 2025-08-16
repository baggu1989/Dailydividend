import requests
import json
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

def check_whatsapp_token():
    """
    Utility function to check if the WhatsApp API token is valid.
    
    Returns:
        tuple: (is_valid, details) where is_valid is a boolean and details is a dict with additional info
    """
    api_token = os.getenv("WHATSAPP_API_TOKEN", "")
    phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    
    if not api_token or not phone_number_id:
        return False, {"error": "Missing API token or phone number ID in environment variables"}
    
    # Construct URL for a simple GET request to check the token
    url = f"https://graph.facebook.com/v19.0/{phone_number_id}"
    headers = {
        "Authorization": f"Bearer {api_token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return True, {"message": "Token is valid", "data": response.json()}
        else:
            error_data = response.json().get("error", {})
            if error_data.get("code") == 190:
                return False, {"error": "API token has expired", "details": error_data}
            return False, {"error": f"API request failed with status {response.status_code}", "details": error_data}
    
    except Exception as e:
        return False, {"error": f"Exception occurred: {str(e)}"}

if __name__ == "__main__":
    is_valid, details = check_whatsapp_token()
    
    if is_valid:
        print("✅ WhatsApp API token is valid!")
        print(f"Phone number details: {json.dumps(details['data'], indent=2)}")
    else:
        print("❌ WhatsApp API token is invalid or expired!")
        print(f"Error details: {json.dumps(details, indent=2)}")
        print("\nPlease refresh your token by following the instructions in docs/whatsapp_token_refresh.md")
