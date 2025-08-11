# backend/app/api/routes/chat.py

from flask import Blueprint, request, jsonify, g
from app.models import ChatSession, ChatMessage, User, Report
from app.services.llm_service import LLMService
from app.api.dependencies import login_required
from app.schemas.chat import (
    ChatMessageCreate, ChatMessageResponse, ChatSessionResponse,
    QuickChatRequest, QuickChatResponse
)
from app.core.database import db
import uuid
import json
import asyncio

chat_bp = Blueprint('chat', __name__)
llm_service = LLMService()

def run_async(coro):
    """Helper function to run an async coroutine in a sync context."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(coro)
    finally:
        loop.close()
    return result

async def build_chat_context(session: ChatSession) -> str:
    """Build context for chat from session history and report data"""
    context_parts = []

    if session.report_id:
        report = db.session.query(Report).filter(Report.id == session.report_id).first()
        if report and report.parsed_data:
            context_parts.append("Report Data:")
            context_parts.append(f"Patient: {report.patient_name or 'Unknown'}")
            if report.parsed_data.get("tests"):
                context_parts.append("Lab Tests:")
                for test in report.parsed_data["tests"][:5]:
                    context_parts.append(f"- {test.get('test_name', 'Unknown')}: {test.get('value', 'N/A')} {test.get('unit', '')}")

    recent_messages = db.session.query(ChatMessage).filter(
        ChatMessage.session_id == session.id
    ).order_by(ChatMessage.created_at.desc()).limit(10).all()

    if recent_messages:
        context_parts.append("\nRecent Conversation:")
        for message in reversed(recent_messages):
            context_parts.append(f"{message.role}: {message.content}")

    return "\n".join(context_parts)

@chat_bp.route("/quick", methods=["POST"])
def quick_chat():
    """Minimal dev endpoint for quick chatbot"""
    payload = QuickChatRequest(**request.get_json())
    reply = run_async(llm_service.chat_response(user_message=payload.message, context=payload.context or ""))
    return jsonify(QuickChatResponse(reply=reply).dict())

@chat_bp.route("/sessions", methods=["POST"])
@login_required
def create_chat_session():
    """Create a new chat session"""
    data = request.get_json()
    report_id = data.get("report_id")

    if report_id:
        report = db.session.query(Report).filter(Report.id == report_id, Report.user_id == g.current_user.id).first()
        if not report:
            return jsonify({"detail": "Report not found"}), 404

    session = ChatSession(
        user_id=g.current_user.id,
        session_id=str(uuid.uuid4()),
        report_id=report_id,
        title=data.get('title', f"Chat Session {uuid.uuid4().hex[:8]}")
    )
    db.session.add(session)
    db.session.commit()
    db.session.refresh(session)
    return jsonify(ChatSessionResponse.from_orm(session).dict())

@chat_bp.route("/sessions", methods=["GET"])
@login_required
def list_chat_sessions():
    """List user's chat sessions"""
    sessions = db.session.query(ChatSession).filter(
        ChatSession.user_id == g.current_user.id,
        ChatSession.is_active == "active"
    ).order_by(ChatSession.updated_at.desc()).all()
    return jsonify([ChatSessionResponse.from_orm(s).dict() for s in sessions])

@chat_bp.route("/sessions/<session_id>/messages", methods=["GET"])
@login_required
def get_chat_messages(session_id: str):
    """Get messages for a chat session"""
    session = db.session.query(ChatSession).filter(ChatSession.session_id == session_id, ChatSession.user_id == g.current_user.id).first()
    if not session:
        return jsonify({"detail": "Chat session not found"}), 404

    messages = db.session.query(ChatMessage).filter(ChatMessage.session_id == session.id).order_by(ChatMessage.created_at.asc()).all()
    return jsonify([ChatMessageResponse.from_orm(m).dict() for m in messages])


@chat_bp.route("/sessions/<session_id>/messages", methods=["POST"])
@login_required
def send_message(session_id: str):
    """Send a message in a chat session"""
    session = db.session.query(ChatSession).filter(ChatSession.session_id == session_id, ChatSession.user_id == g.current_user.id).first()
    if not session:
        return jsonify({"detail": "Chat session not found"}), 404

    message_data = ChatMessageCreate(**request.get_json())
    user_message = ChatMessage(
        session_id=session.id,
        role="user",
        content=message_data.content,
        message_id=str(uuid.uuid4())
    )
    db.session.add(user_message)
    db.session.commit()
    db.session.refresh(user_message)

    try:
        context = run_async(build_chat_context(session))
        ai_response_content = run_async(llm_service.chat_response(user_message=message_data.content, context=context))

        ai_message = ChatMessage(
            session_id=session.id,
            role="assistant",
            content=ai_response_content,
            message_id=str(uuid.uuid4()),
            parent_message_id=user_message.message_id
        )
        db.session.add(ai_message)
        db.session.commit()
        db.session.refresh(ai_message)
        return jsonify(ChatMessageResponse.from_orm(ai_message).dict())

    except Exception as e:
        db.session.delete(user_message)
        db.session.commit()
        return jsonify({"detail": f"Failed to generate response: {str(e)}"}), 500