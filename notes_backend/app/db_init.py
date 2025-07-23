from app.models import db

def init_db(app):
    """Initialize the database context and create tables if not exist."""
    db.init_app(app)
    with app.app_context():
        db.create_all()
