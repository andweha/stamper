from datetime import datetime, timezone
from app.models import db, History, User

# add/updates user viewing history
def add_to_history(user_id, media_type, media_id, title, poster_url):
    existing_entry = History.query.filter_by(user_id=user_id, media_type=media_type, media_id=media_id).first()
    if existing_entry:
        existing_entry.watched_at = datetime.now(timezone.utc)
    else:
        new_history_entry = History(
            user_id=user_id,
            media_type=media_type,
            media_id=media_id,
            title=title,
            poster_url=poster_url
        )
        db.session.add(new_history_entry)
    db.session.commit()
