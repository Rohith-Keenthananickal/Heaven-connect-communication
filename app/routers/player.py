"""
API Router for Player (Device) Registration
"""

from datetime import datetime
from typing import List, Optional
from math import ceil

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.player import Player, PlayerCreate, PlayerResponse, PlayerUpdate, DeviceStatus, PlayerListResponse

router = APIRouter(
    prefix="/players",
    tags=["players"],
    responses={404: {"description": "Not found"}},
)


@router.post("/register", response_model=PlayerResponse, status_code=status.HTTP_201_CREATED)
def register_player(player_in: PlayerCreate, db: Session = Depends(get_db)):
    """
    Register a new player (device) or update existing one if player_id exists (via logic, though here we might just create new or find by token).
    
    Since player_id is usually generated on client side or server side and persisted. 
    If the client sends a player_id, we should probably use that to look up.
    However, the requirement says player_id is UUID / Auto ID. 
    
    Strategy:
    1. Check if a player with the same push_token exists.
    2. If yes, update it.
    3. If no, create a new one.
    
    Wait, usually player_id is unique per device. 
    If the client doesn't send player_id, we create one.
    But for "registration", usually the client wants to tell us "I am this device".
    
    Let's assume for now we look up by push_token for simplicity if player_id is not provided (though it's not in the input schema).
    Actually, let's look at the input schema `PlayerCreate`. It doesn't have player_id.
    So we will check if `push_token` exists.
    """
    
    # Check if player with this push_token already exists
    existing_player = db.query(Player).filter(Player.push_token == player_in.push_token).first()
    
    if existing_player:
        # Update existing player
        existing_player.user_id = player_in.user_id
        existing_player.device_type = player_in.device_type
        existing_player.one_signal_id = player_in.one_signal_id
        existing_player.device_model = player_in.device_model
        existing_player.os_version = player_in.os_version
        existing_player.app_version = player_in.app_version
        existing_player.last_login_at = datetime.utcnow()
        existing_player.status = DeviceStatus.ACTIVE
        
        db.commit()
        db.refresh(existing_player)
        return existing_player
    
    # Create new player
    new_player = Player(
        user_id=player_in.user_id,
        device_type=player_in.device_type,
        push_token=player_in.push_token,
        one_signal_id=player_in.one_signal_id,
        device_model=player_in.device_model,
        os_version=player_in.os_version,
        app_version=player_in.app_version,
        last_login_at=datetime.utcnow(),
        status=DeviceStatus.ACTIVE
    )
    
    db.add(new_player)
    db.commit()
    db.refresh(new_player)
    return new_player


@router.get("", response_model=PlayerListResponse)
def list_players(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    device_type: Optional[str] = Query(None, description="Filter by device type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db)
):
    """
    Get a paginated list of players with optional filters
    
    - **page**: Page number (starts from 1)
    - **page_size**: Number of items per page (1-100)
    - **user_id**: Optional filter by user ID
    - **device_type**: Optional filter by device type
    - **status**: Optional filter by status (active, blocked, logout)
    """
    # Build query with filters
    query = db.query(Player)
    
    if user_id:
        query = query.filter(Player.user_id == user_id)
    
    if device_type:
        query = query.filter(Player.device_type == device_type)
    
    if status:
        query = query.filter(Player.status == status)
    
    # Get total count
    total = query.count()
    
    # Calculate pagination
    skip = (page - 1) * page_size
    total_pages = ceil(total / page_size) if total > 0 else 0
    
    # Get paginated results
    players = query.order_by(Player.updated_at.desc()).offset(skip).limit(page_size).all()
    
    return PlayerListResponse(
        items=players,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{player_id}", response_model=PlayerResponse)
def get_player(player_id: str, db: Session = Depends(get_db)):
    """Get player details by player_id"""
    player = db.query(Player).filter(Player.player_id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@router.put("/{player_id}", response_model=PlayerResponse)
def update_player(player_id: str, player_in: PlayerUpdate, db: Session = Depends(get_db)):
    """Update player details"""
    player = db.query(Player).filter(Player.player_id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    update_data = player_in.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(player, field, value)
    
    if "status" in update_data and update_data["status"] == DeviceStatus.ACTIVE:
         player.last_login_at = datetime.utcnow()

    db.commit()
    db.refresh(player)
    return player


@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_player(player_id: str, db: Session = Depends(get_db)):
    """Delete a player (or mark as blocked/logout depending on policy, but here physical delete)"""
    player = db.query(Player).filter(Player.player_id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    
    db.delete(player)
    db.commit()
    return None
