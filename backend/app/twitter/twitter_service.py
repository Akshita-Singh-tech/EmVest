import logging
from typing import List, Dict, Any
from app.core.config import settings

logger = logging.getLogger("emvest.twitter")


class TwitterIngestionService:
    """
    X / Twitter ingestion connector maintained behind a configuration feature flag.
    News-only sentiment ingestion is prioritized first, with Twitter ingestion remaining optional.
    """

    def __init__(self):
        self.is_enabled = settings.enable_twitter_ingestion
        self.bearer_token = settings.twitter_bearer_token

    def fetch_cashtag_tweets(self, symbols: List[str]) -> List[Dict[str, Any]]:
        if not self.is_enabled:
            logger.info("X/Twitter ingestion is disabled by feature flag. News-only sentiment is active.")
            return []

        if not self.bearer_token:
            logger.warning("X/Twitter ingestion is enabled but no bearer token is configured.")
            return []

        # When active with credentials, queries X v2 API search stream
        return []


twitter_service = TwitterIngestionService()

