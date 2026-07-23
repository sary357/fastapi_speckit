"""API routes for reactions (like/dislike) endpoint."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.schemas.reaction import ReactionRequest, StatusResponse
from src.services.reaction_service import ReactionService
from src.core.rate_limit import limiter

router = APIRouter(prefix="/api", tags=["reactions"])
service = ReactionService()


@router.post("/reactions", response_model=StatusResponse)
@limiter.shared_limit("5/minute", scope="reactions_comments")
async def create_reaction(
    request: Request,
    body: ReactionRequest,
    db: AsyncSession = Depends(get_db),
) -> StatusResponse:
    """
    Submit a like or dislike reaction.
    
    Rate limited to 5 requests per minute per IP across both /api/reactions and /api/comments endpoints.
    """
    # Extract source IP
    source_ip = request.client.host if request.client else "unknown"
    
    # Create reaction record (service handles validation)
    await service.create_reaction(
        db=db,
        reaction_type=body.reaction_type,
        source_ip=source_ip,
    )
    
    return StatusResponse(status="OK")
