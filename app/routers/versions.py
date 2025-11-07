from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.version import Version as VersionSchema
from app.models.version import Version
from app.models.note import Note
from app.models.activity_log import ActivityLog
from app.dependencies.auth import get_current_user
from app.models.user import User
from datetime import datetime

router = APIRouter()

def check_note_access(note: Note, user: User) -> bool:
    return note.owner_id == user.id or user in note.collaborators

@router.get("/{note_id}", response_model=list[VersionSchema])
def get_versions(note_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Check if note exists and belongs to user
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note or not check_note_access(note, current_user):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found or access denied")
    return db.query(Version).filter(Version.note_id == note_id).order_by(Version.version_number).all()

@router.get("/{note_id}/{version_number}", response_model=VersionSchema)
def get_version(note_id: int, version_number: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Check if note exists and belongs to user
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note or not check_note_access(note, current_user):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found or access denied")
    version = db.query(Version).filter(Version.note_id == note_id, Version.version_number == version_number).first()
    if not version:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found")
    return version

@router.post("/{note_id}/restore/{version_number}")
def restore_version(note_id: int, version_number: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Check if note exists and belongs to user
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note or not check_note_access(note, current_user):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found or access denied")
    version = db.query(Version).filter(Version.note_id == note_id, Version.version_number == version_number).first()
    if not version:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found")
    # Create a new version of current state before restoring
    last_version = db.query(Version).filter(Version.note_id == note_id).order_by(Version.version_number.desc()).first()
    new_version_number = (last_version.version_number + 1) if last_version else 1
    current_version = Version(note_id=note_id, version_number=new_version_number, content_snapshot=note.content, editor_id=current_user.id)
    db.add(current_version)
    # Restore note to version
    note.content = version.content_snapshot
    note.updated_at = datetime.utcnow()
    # Log activity
    log = ActivityLog(note_id=note_id, user_id=current_user.id, action="restore")
    db.add(log)
    db.commit()
    return {"message": f"Note restored to version {version_number}"}