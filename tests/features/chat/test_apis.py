"""Tests for Chat API."""

import json

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.utils import timezone

from features.chat.models import Conversation, Message

User = get_user_model()


@pytest.fixture
def auth_client(user: User) -> Client:
    """Authenticated client for chat tests using force_login (bypasses email verification)."""
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture
@pytest.mark.django_db
def second_user(db: None) -> User:
    """Create a second user for chat participant."""
    return User.objects.create_user(
        email="otheruser@example.com",
        password="testpassword123",  # noqa: S106
        username="otheruser",
        user_type=User.UserTypeChoices.HELPER,
    )


@pytest.fixture
@pytest.mark.django_db
def conversation(user: User, second_user: User) -> Conversation:
    """Create a conversation between two users."""
    return Conversation.objects.create(
        participant_1=user,
        participant_2=second_user,
    )


@pytest.fixture
@pytest.mark.django_db
def message(conversation: Conversation, second_user: User) -> Message:
    """Create a message in the conversation from second_user."""
    return Message.objects.create(
        conversation=conversation,
        sender=second_user,
        content="Hello from other user!",
    )


@pytest.fixture
@pytest.mark.django_db
def third_user(db: None) -> User:
    """Create a third user who is not a participant in shared conversations."""
    return User.objects.create_user(
        email="third@example.com",
        password="testpassword123",  # noqa: S106
        username="thirduser",
        user_type=User.UserTypeChoices.HELPER,
    )


@pytest.mark.django_db
class TestChatAPI:
    """Test cases for Chat API."""

    def test_create_conversation_success(
        self,
        auth_client: Client,
        user: User,
        second_user: User,
    ) -> None:
        """Test successful creation of a new conversation."""
        payload = {"participant_id": str(second_user.id)}

        response = auth_client.post(
            "/api/chat/conversations",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = response.json()

        assert "id" in data
        participant_ids = {data["participant_1"]["id"], data["participant_2"]["id"]}
        assert str(user.id) in participant_ids
        assert str(second_user.id) in participant_ids
        assert data["unread_count"] == 0
        assert "created_at" in data

    def test_create_conversation_returns_existing(
        self,
        auth_client: Client,
        user: User,
        second_user: User,
        conversation: Conversation,
    ) -> None:
        """Test that creating conversation with same user returns existing one."""
        payload = {"participant_id": str(second_user.id)}

        response = auth_client.post(
            "/api/chat/conversations",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = response.json()
        assert data["id"] == str(conversation.id)

    def test_create_conversation_with_self_fails(
        self,
        auth_client: Client,
        user: User,
    ) -> None:
        """Test that creating conversation with yourself fails."""
        payload = {"participant_id": str(user.id)}

        response = auth_client.post(
            "/api/chat/conversations",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 403

    def test_create_conversation_unauthenticated_returns_403(self, second_user: User) -> None:
        """Test creating conversation without authentication returns 403."""
        client = Client()
        payload = {"participant_id": str(second_user.id)}

        response = client.post(
            "/api/chat/conversations",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 403

    def test_create_conversation_invalid_participant(
        self,
        auth_client: Client,
    ) -> None:
        """Test creating conversation with non-existent user fails."""
        payload = {"participant_id": "00000000-0000-0000-0000-000000000000"}

        response = auth_client.post(
            "/api/chat/conversations",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 404

    def test_list_conversations_success(
        self,
        auth_client: Client,
        user: User,
        conversation: Conversation,
        second_user: User,
    ) -> None:
        """Test successful listing of conversations."""
        response = auth_client.get("/api/chat/conversations")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == str(conversation.id)
        participant_ids = {data[0]["participant_1"]["id"], data[0]["participant_2"]["id"]}
        assert str(user.id) in participant_ids
        assert str(second_user.id) in participant_ids

    def test_list_conversations_empty(self, auth_client: Client) -> None:
        """Test listing conversations when user has none."""
        response = auth_client.get("/api/chat/conversations")

        assert response.status_code == 200
        assert response.json() == []

    def test_list_conversations_not_authenticated(self) -> None:
        """Test listing conversations without authentication fails."""
        client = Client()
        response = client.get("/api/chat/conversations")
        assert response.status_code == 403

    def test_get_messages_success(
        self,
        auth_client: Client,
        conversation: Conversation,
        message: Message,
        second_user: User,
    ) -> None:
        """Test successful retrieval of messages."""
        response = auth_client.get(
            f"/api/chat/conversations/{conversation.id}/messages"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["page"] == 1
        assert data["page_size"] == 50
        assert data["has_next"] is False
        assert len(data["messages"]) == 1
        assert data["messages"][0]["content"] == message.content
        assert data["messages"][0]["sender"]["id"] == str(second_user.id)

    def test_get_messages_pagination(
        self,
        auth_client: Client,
        conversation: Conversation,
        user: User,
    ) -> None:
        """Test message pagination."""
        for i in range(5):
            Message.objects.create(
                conversation=conversation,
                sender=user,
                content=f"Message {i}",
            )

        response = auth_client.get(
            f"/api/chat/conversations/{conversation.id}/messages?page_size=2&page=1"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert data["page_size"] == 2
        assert len(data["messages"]) == 2
        assert data["has_next"] is True

    def test_get_messages_page_size_capped(
        self,
        auth_client: Client,
        conversation: Conversation,
    ) -> None:
        """Test that page_size is capped at 100."""
        response = auth_client.get(
            f"/api/chat/conversations/{conversation.id}/messages?page_size=99999"
        )
        assert response.status_code == 200
        assert response.json()["page_size"] == 100

    def test_get_messages_negative_page_becomes_first(
        self,
        auth_client: Client,
        conversation: Conversation,
    ) -> None:
        """Test that negative page number is treated as page 1."""
        response = auth_client.get(
            f"/api/chat/conversations/{conversation.id}/messages?page=-5"
        )
        assert response.status_code == 200
        assert response.json()["page"] == 1

    def test_get_messages_not_participant_forbidden(
        self,
        client: Client,
        conversation: Conversation,
        third_user: User,
    ) -> None:
        """Test getting messages when not a participant returns 403."""
        client.force_login(third_user)
        resp = client.get(f"/api/chat/conversations/{conversation.id}/messages")
        assert resp.status_code == 403

    def test_get_messages_conversation_not_found(
        self,
        auth_client: Client,
    ) -> None:
        """Test getting messages for non-existent conversation fails."""
        response = auth_client.get(
            "/api/chat/conversations/00000000-0000-0000-0000-000000000000/messages"
        )

        assert response.status_code == 404

    def test_send_message_success(
        self,
        auth_client: Client,
        conversation: Conversation,
        user: User,
    ) -> None:
        """Test successful sending of a message."""
        payload = {"content": "Hello, this is a test message!"}

        response = auth_client.post(
            f"/api/chat/conversations/{conversation.id}/messages",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 201
        data = response.json()
        assert data["content"] == payload["content"]
        assert data["sender"]["id"] == str(user.id)
        assert data["conversation_id"] == str(conversation.id)
        assert data["read_at"] is None

        assert Message.objects.filter(conversation=conversation).count() == 1

    def test_send_message_empty_content_fails(
        self,
        auth_client: Client,
        conversation: Conversation,
    ) -> None:
        """Test that sending an empty message is rejected."""
        payload = {"content": ""}

        response = auth_client.post(
            f"/api/chat/conversations/{conversation.id}/messages",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 422

    def test_send_message_too_long_fails(
        self,
        auth_client: Client,
        conversation: Conversation,
    ) -> None:
        """Test that sending a message exceeding max length is rejected."""
        payload = {"content": "x" * 5001}

        response = auth_client.post(
            f"/api/chat/conversations/{conversation.id}/messages",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 422

    def test_send_message_updates_last_message_at(
        self,
        auth_client: Client,
        conversation: Conversation,
        user: User,
    ) -> None:
        """Test that sending message updates conversation's last_message_at."""
        assert conversation.last_message_at is None

        payload = {"content": "Test message"}
        response = auth_client.post(
            f"/api/chat/conversations/{conversation.id}/messages",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 201
        conversation.refresh_from_db()
        assert conversation.last_message_at is not None

    def test_send_message_not_authenticated(
        self,
        conversation: Conversation,
    ) -> None:
        """Test sending message without authentication fails."""
        client = Client()
        payload = {"content": "Hello"}

        response = client.post(
            f"/api/chat/conversations/{conversation.id}/messages",
            data=json.dumps(payload),
            content_type="application/json",
        )

        assert response.status_code == 403

    def test_mark_messages_as_read_success(
        self,
        auth_client: Client,
        conversation: Conversation,
        message: Message,
        user: User,
    ) -> None:
        """Test marking messages as read."""
        response = auth_client.patch(
            f"/api/chat/conversations/{conversation.id}/read",
            data=json.dumps({}),
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1

        message.refresh_from_db()
        assert message.read_at is not None

    def test_mark_messages_as_read_not_authenticated(
        self,
        conversation: Conversation,
    ) -> None:
        """Test marking as read without authentication fails."""
        client = Client()
        response = client.patch(
            f"/api/chat/conversations/{conversation.id}/read",
            data=json.dumps({}),
            content_type="application/json",
        )

        assert response.status_code == 403

    def test_delete_conversation_success(
        self,
        auth_client: Client,
        conversation: Conversation,
    ) -> None:
        """Test successful deletion of a conversation."""
        response = auth_client.delete(
            f"/api/chat/conversations/{conversation.id}"
        )

        assert response.status_code == 200
        assert not Conversation.objects.filter(id=conversation.id).exists()

    def test_delete_conversation_not_participant_forbidden(
        self,
        client: Client,
        conversation: Conversation,
        third_user: User,
    ) -> None:
        """Test deleting conversation when not a participant returns 403."""
        client.force_login(third_user)
        resp = client.delete(f"/api/chat/conversations/{conversation.id}")
        assert resp.status_code == 403


@pytest.mark.django_db
class TestChatAPIIntegration:
    """Integration tests for Chat API - full workflow."""

    def test_full_chat_workflow(
        self,
        auth_client: Client,
        user: User,
        second_user: User,
    ) -> None:
        """Test complete chat workflow: create conversation, send messages, list, mark read."""
        create_resp = auth_client.post(
            "/api/chat/conversations",
            data=json.dumps({"participant_id": str(second_user.id)}),
            content_type="application/json",
        )
        assert create_resp.status_code == 201
        conversation_id = create_resp.json()["id"]

        send_resp = auth_client.post(
            f"/api/chat/conversations/{conversation_id}/messages",
            data=json.dumps({"content": "Hi there!"}),
            content_type="application/json",
        )
        assert send_resp.status_code == 201
        assert send_resp.json()["content"] == "Hi there!"

        messages_resp = auth_client.get(
            f"/api/chat/conversations/{conversation_id}/messages"
        )
        assert messages_resp.status_code == 200
        messages_data = messages_resp.json()
        assert messages_data["total"] == 1
        assert messages_data["messages"][0]["content"] == "Hi there!"

        list_resp = auth_client.get("/api/chat/conversations")
        assert list_resp.status_code == 200
        convos = list_resp.json()
        assert len(convos) == 1
        assert convos[0]["id"] == conversation_id
