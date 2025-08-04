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

- `POST /chat` - Send a message to the chatbot
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