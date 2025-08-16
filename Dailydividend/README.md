# Dailydividend Scheduler

This application sends scheduled WhatsApp messages with financial news updates to subscribed users.

## Architecture

- **Celery Beat**: Schedules tasks at specified intervals
- **Celery Worker**: Executes the scheduled tasks
- **Redis**: Message broker for Celery
- **WhatsApp API**: Sends messages to users

## Running with Docker

The application is containerized using Docker and can be run with Docker Compose.

### Prerequisites

- Docker and Docker Compose installed
- Valid WhatsApp Business API credentials

### Setup

1. Clone the repository
2. Update the `.env` file with your WhatsApp API credentials
3. Make sure users are defined in `app/backend/scheduler/users.json`

### Running the Services

```bash
# Build and start all services
docker-compose up --build

# Run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the services
docker-compose down
```

## Checking Logs

```bash
# View all logs
docker-compose logs -f

# View logs for a specific service
docker-compose logs -f celery-worker
docker-compose logs -f celery-beat
```

## Manual Testing

You can test the WhatsApp message sending functionality manually:

```bash
# Test WhatsApp token validity
python -m app.backend.tasks.send_message --test

# Send a test message
python -m app.backend.tasks.send_message --send --number=<PHONE_NUMBER>
```

## Updating User List

To add or remove users from the messaging list:
1. Edit the `app/backend/scheduler/users.json` file
2. Restart the celery-beat service: `docker-compose restart celery-beat`

## Configuration

Schedule configuration is managed in `app/backend/scheduler/scheduler.py`.
Default schedules:
- 1 time per day: 12:00 PM
- 2 times per day: 12:00 PM, 11:59 PM
- 3 times per day: 8:00 AM, 12:00 PM, 11:59 PM
