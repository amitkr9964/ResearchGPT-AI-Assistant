"""Export API routes."""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_current_user
from backend.database.database import get_db
from backend.database.models import User
from backend.models.schemas import ExportRequest
from backend.services.chat_service import ChatService
from backend.utils.export import export_to_docx, export_to_markdown, export_to_pdf

router = APIRouter(prefix="/export", tags=["Export"])
chat_service = ChatService()


@router.post("")
async def export_chat(
    request: ExportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    conv = await chat_service.get_conversation(db, current_user, request.conversation_id)

    if request.format == "markdown":
        content = export_to_markdown(conv)
        return StreamingResponse(
            iter([content]),
            media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="{conv.title}.md"'},
        )
    elif request.format == "docx":
        buffer = export_to_docx(conv)
        return StreamingResponse(
            buffer,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f'attachment; filename="{conv.title}.docx"'},
        )
    elif request.format == "pdf":
        buffer = export_to_pdf(conv)
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{conv.title}.pdf"'},
        )
    else:
        content = export_to_markdown(conv)
        return StreamingResponse(
            iter([content]),
            media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="{conv.title}.md"'},
        )
