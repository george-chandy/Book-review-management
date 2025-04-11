from src.config import BookReviewBaseSetting

class Config(BookReviewBaseSetting):

    JWT_ACCESS_SECRET: str
    JWT_REFRESH_SECRET: str
    JWT_ACCESS_EXPIRY_MINUTES: int
    JWT_REFRESH_EXPIRY_DAYS: int
    JWT_ISSUER: str
    JWT_AUDIENCE: str

    
    EMAIL_VERIFICATION_TOKEN_EXPIRY_HOURS: int = 24
    PASSWORD_RESET_TOKEN_EXPIRY_HOURS: int = 1
    HOST_ADDRESS: str = "http://localhost:8000"

config = Config()

