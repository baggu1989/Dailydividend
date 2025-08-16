# Financial News Chatbot

An AI-powered chatbot for financial news, market analysis, and economic insights using Groq's Mixtral model and real-time RSS feeds.

## Features

- 🤖 **AI-Powered Responses**: Uses Groq's Llama-3.3-70B-Versatile model for intelligent financial analysis
- 📰 **Real-time News**: Fetches latest financial news from Yahoo Finance and Investing.com
- 🧠 **Context Awareness**: Maintains conversation history for personalized responses
- 📊 **Topic Classification**: Automatically categorizes queries (economy, market, general)
- 🔍 **Semantic Search**: Uses vector embeddings for relevant news retrieval
- ⏰ **Scheduled Updates**: Automatic news fetching every 12 hours
- 🐳 **Docker Ready**: Containerized for easy deployment

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │───▶│  LangGraph      │───▶│  Groq LLM       │
│   (main.py)     │    │  Workflow       │    │  (Mixtral)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  User Sessions  │    │  ChromaDB       │    │  RSS Feeds      │
│  (Memory)       │    │  (Vector Store) │    │  (News Source)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Setup

### 1. Environment Setup

Create a `.env` file in the project root:

```bash
# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

# Model Configuration
LLM_MODEL=llama-3.3-70b-versatile
EMBED_MODEL=all-MiniLM-L6-v2

# Application Configuration
CHROMA_PATH=./chroma_news
LOG_LEVEL=INFO

# WhatsApp Meta API Configuration
WHATSAPP_API_TOKEN=your_whatsapp_api_token_here
WHATSAPP_PHONE_NUMBER_ID=your_whatsapp_phone_number_id
WHATSAPP_VERIFY_TOKEN=your_custom_verification_token
WHATSAPP_BUSINESS_ACCOUNT_ID=your_whatsapp_business_account_id
```

### 2. Install Dependencies

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 3. Get Groq API Key

1. Sign up at [Groq Console](https://console.groq.com/)
2. Create an API key
3. Add it to your `.env` file

## Usage

### Start the Chatbot

```bash
# Run the FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Start News Scheduler

```bash
# Run the news fetcher scheduler
python schedule_news.py
```

### API Endpoints

- `POST /webhook` - WhatsApp Meta API webhook for receiving messages
- `GET /webhook` - WhatsApp webhook verification endpoint
- `POST /chat` - Legacy endpoint for direct API messages
- `GET /health` - Health check
- `GET /` - API information

### Example API Call

```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "user123",
       "query": "What are the latest market trends?"
     }'
```

## WhatsApp Meta API Setup

### 1. Create a Meta Developer Account

1. Visit [Meta for Developers](https://developers.facebook.com/) and create an account
2. Create a new app with the "Business" type
3. Add the "WhatsApp" product to your app

### 2. Set up WhatsApp API

1. In the Meta Developer Dashboard, go to the WhatsApp > Getting Started section
2. Connect a phone number to your WhatsApp Business account
3. Note down your:
   - WhatsApp Business Account ID
   - Phone Number ID
   - Permanent API Token

### 3. Configure Webhook

1. Set up a server with a public HTTPS URL (you can use ngrok for development)
2. Create a custom verification token in your .env file
3. Configure a webhook subscription in the Meta Developer Dashboard:
   - URL: `https://your-server.com/webhook`
   - Verify Token: Same value as `WHATSAPP_VERIFY_TOKEN`
   - Subscribe to the `messages` field

4. The webhook will receive messages in this format:
```json
{
  "object": "whatsapp_business_account",
  "entry": [{
    "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
    "changes": [{
      "value": {
        "messaging_product": "whatsapp",
        "metadata": {
          "display_phone_number": "PHONE_NUMBER",
          "phone_number_id": "PHONE_NUMBER_ID"
        },
        "contacts": [{
          "profile": {
            "name": "CONTACT_NAME"
          },
          "wa_id": "CONTACT_PHONE_NUMBER"
        }],
        "messages": [{
          "from": "CONTACT_PHONE_NUMBER",
          "id": "MESSAGE_ID",
          "timestamp": "TIMESTAMP",
          "text": {
            "body": "MESSAGE_CONTENT"
          },
          "type": "text"
        }]
      },
      "field": "messages"
    }]
  }]
}
```

## Docker Deployment

```bash
# Build the image
docker build -t financial-chatbot .

# Run the container
docker run -p 8000:8000 --env-file .env financial-chatbot
```

## Project Structure

```
├── app/
│   ├── __init__.py
│   ├── chatbot.py      # LangGraph workflow and LLM integration
│   ├── config.py       # Configuration settings
│   ├── logger.py       # Logging setup
│   ├── news_fetcher.py # RSS feed processing
│   └── topic_classifier.py # Advanced topic classification
├── schema/
│   ├── __init__.py
│   ├── chat_models.py  # Chat input/output models
│   └── models.py       # Additional data models
├── main.py             # FastAPI application
├── schedule_news.py    # News scheduler
├── requirements.txt    # Python dependencies
├── Dockerfile         # Docker configuration
└── README.md          # This file
```

## Configuration

### Models Used

- **LLM**: `llama-3.3-70b-versatile` (Groq) - For generating responses
- **Embeddings**: `all-MiniLM-L6-v2` (HuggingFace) - For semantic search

### News Sources

- Yahoo Finance RSS
- Investing.com Economic News

### Topic Classification

- **Economy**: GDP, inflation, economic indicators
- **Market**: Stocks, trading, market indices
- **General**: Other financial topics

## Error Handling

The application includes comprehensive error handling for:
- API failures
- Network issues
- Invalid inputs
- Model errors
- Database connection issues

## Logging

All operations are logged with appropriate levels:
- INFO: Normal operations
- WARNING: Non-critical issues
- ERROR: Critical errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License 