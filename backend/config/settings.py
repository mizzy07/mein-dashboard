from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""

    # API Keys
    ANTHROPIC_API_KEY: str
    BINANCE_API_KEY: str = ""
    BINANCE_API_SECRET: str = ""
    COINGECKO_API_KEY: str = ""

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # Database
    DATABASE_URL: str = "sqlite:///./data/trading.db"

    # Application
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Rate Limiting
    COINGECKO_MAX_CALLS_PER_MINUTE: int = 50
    BINANCE_MAX_CALLS_PER_MINUTE: int = 1200

    # AI Settings
    CLAUDE_MODEL: str = "claude-sonnet-4-20250514"
    CLAUDE_MAX_TOKENS: int = 4096

    # Trading
    TRACKED_COINS: str = "BTC,ETH,SOL,BNB,AVAX,LINK,MATIC,DOT,ADA,XRP,INJ,SEI,ARB,OP,TIA,SUI"
    DEFAULT_TIMEFRAME: str = "1h"
    SIGNAL_UPDATE_INTERVAL: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def coins_list(self) -> List[str]:
        """Get list of tracked coins"""
        return [coin.strip() for coin in self.TRACKED_COINS.split(",")]

    @property
    def redis_url(self) -> str:
        """Get Redis connection URL"""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


settings = Settings()
