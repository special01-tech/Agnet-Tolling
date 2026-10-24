#!/usr/bin/env python3
"""
🛠️ Module centralisé d'outils pour l'Agent IA Personnel
"""

from .tavily_search import tavily_search
from .weather_tool import get_weather, get_weather_forecast, compare_weather_tool
from .send_mail import send_email, create_email_draft
from .calendar_manager import (
    get_todays_events, get_upcoming_events, create_event, 
    update_event, delete_event
)
from .notion_tool import (
    search_notion_tool, read_notion_page_tool, 
    create_notion_page_tool, append_to_notion_page_tool
)
from .drive_tool import search_drive_tool, read_drive_file_tool

__all__ = [
    "tavily_search",
    "get_weather",
    "get_weather_forecast",
    "compare_weather_tool",
    "send_email",
    "create_email_draft",
    "get_todays_events",
    "get_upcoming_events",
    "create_event",
    "update_event",
    "delete_event",
    "search_notion_tool",
    "read_notion_page_tool",
    "create_notion_page_tool",
    "append_to_notion_page_tool",
    "search_drive_tool",
    "read_drive_file_tool"
]
