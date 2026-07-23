"""API routes for comments endpoint."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.schemas.comment import CommentRequest, CommentResponse
from src.schemas.reaction import StatusResponse
from src.services.comment_service import CommentService
from src.core.rate_limit import limiter

router = APIRouter(prefix="/api", tags=["comments"])
service = CommentService()


@router.post("/comments", response_model=StatusResponse)
@limiter.shared_limit("5/minute", scope="reactions_comments")
async def create_comment(
    request: Request,
    body: CommentRequest,
    db: AsyncSession = Depends(get_db),
) -> StatusResponse:
    """
    Submit a comment.
    
    Rate limited to 5 requests per minute per IP across both /api/reactions and /api/comments endpoints.
    
    Comment content:
    - Must not be empty or whitespace-only
    - Maximum 1000 characters
    """
    # Extract source IP
    source_ip = request.client.host if request.client else "unknown"
    
    # Create comment record (service handles validation)
    await service.create_comment(
        db=db,
        content=body.content,
        source_ip=source_ip,
    )
    
    return StatusResponse(status="OK")
