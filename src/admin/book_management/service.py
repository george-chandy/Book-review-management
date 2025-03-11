from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from src.models import Review

# Function to Get Average Rating
def get_average_rating(db: Session, book_id: int):
    avg_rating = db.query(func.avg(Review.rating)).filter(Review.book_id == book_id).scalar()
    return round(avg_rating, 2) if avg_rating else 0  # Round to 2 decimal places