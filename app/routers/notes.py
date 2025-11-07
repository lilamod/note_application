from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.schemas.note import NoteCreate, NoteUpdate, Note, CollaboratorAdd, SearchQuery
from app.models.note import Note as NoteModel, note_collaborators
from app.models.version import Version
from app.models.activity_log import ActivityLog
from app.dependencies.auth import get_current_user
from app.models.user import User
from datetime import datetime

router = APIRouter()

def check_note_access(note: NoteModel, user: User) -> bool:
    return note.owner_id == user.id or user in note.collaborators

@router.post("/", response_model=Note)
def create_note(note: NoteCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_note = NoteModel(title=note.title, content=note.content, owner_id=current_user.id)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

@router.get("/", response_model=list[Note])
def get_notes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(NoteModel).filter(
        or_(NoteModel.owner_id == current_user.id, NoteModel.collaborators.any(id=current_user.id))
    ).all()

@router.get("/{note_id}", response_model=Note)
def get_note(note_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    note = db.query(NoteModel).filter(NoteModel.id == note_id).first()
    if not note or not check_note_access(note, current_user):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found or access denied")
    # Log activity
    log = ActivityLog(note_id=note_id, user_id=current_user.id, action="view")
    db.add(log)
    db.commit()
    return note

@router.put("/{note_id}", response_model=Note)
def update_note(note_id: int, note_update: NoteUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    note = db.query(NoteModel).filter(NoteModel.id == note_id).first()
    if not note or not check_note_access(note, current_user):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found or access denied")
    last_version = db.query(Version).filter(Version.note_id == note_id).order_by(Version.version_number.desc()).first()
    version_number = (last_version.version_number + 1) if last_version else 1
    version = Version(note_id=note_id, version_number=version_number, content_snapshot=note.content, editor_id=current_user.id)
    db.add(version)
    note.title = note_update.title
    note.content = note_update.content
    note.updated_at = datetime.utcnow()
    log = ActivityLog(note_id=note_id, user_id=current_user.id, action="edit")
    db.add(log)
    db.commit()
    db.refresh(note)
    return note

@router.delete("/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    note = db.query(NoteModel).filter(NoteModel.id == note_id, NoteModel.owner_id == current_user.id).first()  # Only owner can delete
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found or access denied")
    db.delete(note)
    db.commit()
    return {"message": "Note deleted successfully"}

@router.post("/{note_id}/collaborators", response_model=dict)
def add_collaborator(note_id: int, collab: CollaboratorAdd, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    note = db.query(NoteModel).filter(NoteModel.id == note_id, NoteModel.owner_id == current_user.id).first()  # Only owner
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found or not owner")
    user = db.query(User).filter(User.username == collab.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user in note.collaborators:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already a collaborator")
    note.collaborators.append(user)
    db.commit()
    return {"message": f"Collaborator {collab.username} added"}

@router.delete("/{note_id}/collaborators/{user_id}")
def remove_collaborator(note_id: int, user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    note = db.query(NoteModel).filter(NoteModel.id == note_id, NoteModel.owner_id == current_user.id).first()  # Only owner
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found or not owner")
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user not in note.collaborators:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collaborator not found")
    note.collaborators.remove(user)
    db.commit()
    return {"message": f"Collaborator removed"}

@router.get("/search", response_model=list[Note])
def search_notes(search: SearchQuery, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = search.query.lower()
    notes = db.query(NoteModel).filter(
        or_(NoteModel.owner_id == current_user.id, NoteModel.collaborators.any(id=current_user.id)),
        or_(NoteModel.title.ilike(f"%{query}%"), NoteModel.content.ilike(f"%{query}%"))
    ).all()
    return notes

@router.get("/{note_id}/logs", response_model=list[ActivityLog])
def get_note_logs(note_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    note = db.query(NoteModel).filter(NoteModel.id == note_id).first()
    if not note or not check_note_access(note, current_user):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found or access denied")
    return db.query(ActivityLog).filter(ActivityLog.note_id == note_id).order_by(ActivityLog.timestamp.desc()).all()