# app/scheduler_config.py

"""Configuration for the enhanced news scheduler"""

from datetime import time

# Scheduler Configuration
SCHEDULER_CONFIG = {
    # Frequency-based scheduling
    "frequencies": {
        "hourly": {
            "enabled": True,
            "interval": "every hour",
            "description": "Fetch from sources that update hourly"
        },
        "daily": {
            "enabled": True,
            "time": time(6, 0),  # 6:00 AM
            "description": "Fetch from sources that update daily"
        },
        "weekly": {
            "enabled": True,
            "day": "sunday",
            "time": time(8, 0),  # 8:00 AM
            "description": "Fetch from sources that update weekly"
        }
    },
    
    # Comprehensive fetch settings
    "comprehensive_fetch": {
        "enabled": True,
        "interval_hours": 6,
        "description": "Fetch from all sources every 6 hours"
    },
    
    # Health check settings
    "health_check": {
        "enabled": True,
        "interval_hours": 2,
        "description": "Perform health check every 2 hours"
    },
    
    # Cleanup settings
    "cleanup": {
        "enabled": True,
        "time": time(2, 0),  # 2:00 AM
        "description": "Cleanup old data daily at 2 AM"
    },
    
    # Performance settings
    "performance": {
        "max_concurrent_fetches": 5,
        "fetch_timeout_seconds": 30,
        "retry_attempts": 3,
        "retry_delay_seconds": 60
    },
    
    # Logging settings
    "logging": {
        "level": "INFO",
        "file": "scheduler.log",
        "max_file_size_mb": 10,
        "backup_count": 5
    },
    
    # Error handling
    "error_handling": {
        "max_consecutive_failures": 5,
        "failure_cooldown_minutes": 30,
        "notify_on_failure": False
    }
}

# Topic-specific scheduling (optional overrides)
TOPIC_SCHEDULING = {
    "market": {
        "priority": "high",
        "max_articles_per_fetch": 10,
        "enabled": True
    },
    "economy": {
        "priority": "high", 
        "max_articles_per_fetch": 8,
        "enabled": True
    },
    "crypto": {
        "priority": "medium",
        "max_articles_per_fetch": 6,
        "enabled": True
    },
    "forex": {
        "priority": "medium",
        "max_articles_per_fetch": 6,
        "enabled": True
    },
    "commodities": {
        "priority": "medium",
        "max_articles_per_fetch": 5,
        "enabled": True
    },
    "tech_markets": {
        "priority": "low",
        "max_articles_per_fetch": 4,
        "enabled": True
    },
    "global_markets": {
        "priority": "low",
        "max_articles_per_fetch": 4,
        "enabled": True
    }
}

# Time-based scheduling rules
TIME_RULES = {
    "market_hours": {
        "start": time(9, 30),  # 9:30 AM
        "end": time(16, 0),    # 4:00 PM
        "description": "US Market hours - more frequent updates"
    },
    "off_hours": {
        "start": time(16, 0),  # 4:00 PM
        "end": time(9, 30),    # 9:30 AM
        "description": "Off market hours - less frequent updates"
    }
}

# Notification settings
NOTIFICATION_CONFIG = {
    "enabled": False,
    "methods": {
        "email": {
            "enabled": False,
            "recipients": [],
            "smtp_server": "",
            "smtp_port": 587
        },
        "webhook": {
            "enabled": False,
            "url": "",
            "headers": {}
        },
        "slack": {
            "enabled": False,
            "webhook_url": "",
            "channel": "#news-alerts"
        }
    },
    "triggers": {
        "on_failure": True,
        "on_success": False,
        "on_health_check": False,
        "daily_summary": True
    }
}

def get_scheduler_config():
    """Get the scheduler configuration"""
    return SCHEDULER_CONFIG

def get_topic_scheduling():
    """Get topic-specific scheduling configuration"""
    return TOPIC_SCHEDULING

def get_time_rules():
    """Get time-based scheduling rules"""
    return TIME_RULES

def get_notification_config():
    """Get notification configuration"""
    return NOTIFICATION_CONFIG

def is_market_hours():
    """Check if current time is during market hours"""
    from datetime import datetime
    now = datetime.now().time()
    market_start = TIME_RULES["market_hours"]["start"]
    market_end = TIME_RULES["market_hours"]["end"]
    
    if market_start <= market_end:
        return market_start <= now <= market_end
    else:  # Handles overnight periods
        return now >= market_start or now <= market_end

def get_adaptive_interval():
    """Get adaptive interval based on market hours"""
    if is_market_hours():
        return 2  # More frequent during market hours
    else:
        return 6  # Less frequent during off hours 