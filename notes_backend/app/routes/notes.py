from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask import request
from sqlalchemy import or_

from app.models import Note, db
from app.auth import get_current_user

blp = Blueprint("Notes", "notes", url_prefix="/notes", description="Notes CRUD and search routes")

# PUBLIC_INTERFACE
@blp.route("/")
class NotesList(MethodView):
    """Create or list notes."""
    def get(self):
        """Get all notes for current user (optionally search)."""
        user = get_current_user()
        query_param = request.args.get("q")
        query = Note.query.filter_by(user_id=user.id)
        if query_param:
            search = f"%{query_param}%"
            query = query.filter(or_(Note.title.ilike(search), Note.content.ilike(search)))
        notes = query.order_by(Note.updated_at.desc()).all()
        return [serialize_note(note) for note in notes]

    def post(self):
        """Create a new note for current user."""
        user = get_current_user()
        data = request.get_json()
        title = data.get("title", "")
        content = data.get("content", "")
        note = Note(title=title, content=content, user_id=user.id)
        db.session.add(note)
        db.session.commit()
        return serialize_note(note), 201

# PUBLIC_INTERFACE
@blp.route("/<int:note_id>")
class NoteDetail(MethodView):
    """Read, update, or delete a note."""
    def get(self, note_id):
        note = Note.query.get(note_id)
        user = get_current_user()
        if not note or note.user_id != user.id:
            abort(404, message="Note not found.")
        return serialize_note(note)

    def put(self, note_id):
        note = Note.query.get(note_id)
        user = get_current_user()
        if not note or note.user_id != user.id:
            abort(404, message="Note not found.")
        data = request.get_json()
        note.title = data.get("title", note.title)
        note.content = data.get("content", note.content)
        db.session.commit()
        return serialize_note(note)

    def delete(self, note_id):
        note = Note.query.get(note_id)
        user = get_current_user()
        if not note or note.user_id != user.id:
            abort(404, message="Note not found.")
        db.session.delete(note)
        db.session.commit()
        return {"message": "Note deleted."}

def serialize_note(note):
    """Serialize note for output."""
    return {
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "created_at": note.created_at.isoformat(),
        "updated_at": note.updated_at.isoformat(),
    }
