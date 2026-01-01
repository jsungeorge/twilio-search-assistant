import os
import requests
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

# 1. Load secrets from .env file
load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
SEARCH_ENGINE_ID = os.getenv('SEARCH_ENGINE_ID')

app = Flask(__name__)

def search_google(query):
    """
    Takes a query string, asks Google, and returns the Title and Link of the first result.
    """
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': GOOGLE_API_KEY,
        'cx': SEARCH_ENGINE_ID,
        'q': query,
        'num': 1 # We only want the top result
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()

        # Check if we got results
        if 'items' in data:
            first_result = data['items'][0]
            title = first_result['title']
            link = first_result['link']
            return f"{title}\n{link}"
        else:
            return "No results found."
            
    except Exception as e:
        return f"Error searching Google: {str(e)}"

# 2. The Webhook (This handles incoming texts)
@app.route('/sms', methods=['POST'])
def sms_reply():
    # Get the message the user sent
    incoming_msg = request.values.get('Body', '').strip()
    
    # Create a Twilio response object
    resp = MessagingResponse()
    
    # Perform the search
    if incoming_msg:
        result = search_google(incoming_msg)
        resp.message(result)
    else:
        resp.message("Please send a search query!")
        
    return str(resp)

if __name__ == '__main__':
    app.run(debug=True, port=5001)