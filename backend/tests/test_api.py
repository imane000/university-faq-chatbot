import httpx
import pytest
from app.main import app
from app.rag.store import get_collection
from app.services import llm_service
from fastapi.testclient import TestClient
from groq import Groq


@pytest.fixture
def client():
    return TestClient(app)


def seed_context():
    get_collection(create=True).upsert(
        ids=["inscription"],
        documents=["Inscription en ligne."],
        metadatas=[{"source": "faq.json"}],
    )


def mock_groq(monkeypatch, handler):
    sdk = Groq(
        api_key="test-key",
        max_retries=0,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    monkeypatch.setattr(llm_service, "get_groq_client", lambda: sdk)
    return sdk


def test_health_and_no_shared_history(client):
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/history").status_code == 404
    assert client.delete("/history").status_code == 404


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"question": " "},
        {"question": "x" * 2001},
        {"question": None},
        {"question": 42},
        {"question": "ok", "unexpected": True},
    ],
)
def test_validation(client, payload):
    assert client.post("/chat", json=payload).status_code == 422


def test_empty_index_does_not_call_groq(client, monkeypatch):
    def unexpected():
        pytest.fail("Groq must not be called without context")

    monkeypatch.setattr(llm_service, "get_groq_client", unexpected)
    result = client.post("/chat", json={"question": "inscription"})
    assert result.status_code == 200
    assert result.json() == {"response": llm_service.NO_CONTEXT, "sources": []}


def test_missing_key_is_actionable_and_redacted(client):
    seed_context()
    result = client.post("/chat", json={"question": "inscription"})
    assert result.status_code == 503
    assert "configuré" in result.json()["detail"]


def test_official_groq_sdk_request_and_answer(client, monkeypatch, isolated_settings):
    import json

    seed_context()

    def handler(request):
        assert request.url == "https://api.groq.com/openai/v1/chat/completions"
        body = json.loads(request.content)
        assert body["model"] == isolated_settings.groq_model
        assert body["max_completion_tokens"] == isolated_settings.groq_max_tokens
        assert body["messages"][0]["role"] == "system"
        assert "Inscription en ligne." in body["messages"][1]["content"]
        assert "faq.json" in body["messages"][1]["content"]
        return httpx.Response(
            200,
            json={
                "id": "test",
                "object": "chat.completion",
                "created": 0,
                "model": body["model"],
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": "En ligne [1]."},
                        "finish_reason": "stop",
                    }
                ],
            },
        )

    with mock_groq(monkeypatch, handler):
        result = client.post("/chat", json={"question": "  inscription  "})
    assert result.status_code == 200
    assert result.json() == {
        "response": "En ligne [1].",
        "sources": [{"reference": 1, "source": "faq.json", "page": None}],
    }


@pytest.mark.parametrize(("status", "expected"), [(401, 502), (400, 502), (429, 429), (500, 502)])
def test_provider_errors_are_sanitized(client, monkeypatch, status, expected):
    seed_context()
    with mock_groq(
        monkeypatch,
        lambda request: httpx.Response(
            status, json={"error": {"message": "SENSITIVE_PROVIDER_DETAILS"}}
        ),
    ):
        result = client.post("/chat", json={"question": "inscription"})
    assert result.status_code == expected
    assert "SENSITIVE" not in result.text


@pytest.mark.parametrize(
    ("error", "expected"), [(httpx.ReadTimeout, 504), (httpx.ConnectError, 503)]
)
def test_network_failures(client, monkeypatch, error, expected):
    seed_context()

    def handler(request):
        raise error("private diagnostics", request=request)

    with mock_groq(monkeypatch, handler):
        result = client.post("/chat", json={"question": "inscription"})
    assert result.status_code == expected
    assert "private" not in result.text


def test_empty_completion_is_handled(client, monkeypatch):
    seed_context()
    with mock_groq(monkeypatch, lambda request: httpx.Response(200, json={"choices": []})):
        result = client.post("/chat", json={"question": "inscription"})
    assert result.status_code == 502


def test_retrieval_failure_is_sanitized(client, monkeypatch):
    def fail(question):
        raise RuntimeError("private filesystem path")

    monkeypatch.setattr(llm_service, "retrieve_passages", fail)
    result = client.post("/chat", json={"question": "inscription"})
    assert result.status_code == 503
    assert "private" not in result.text


def test_cors_is_restricted(client):
    for origin, allowed in [("http://localhost:5173", True), ("https://untrusted.test", False)]:
        result = client.options(
            "/chat", headers={"Origin": origin, "Access-Control-Request-Method": "POST"}
        )
        assert (result.headers.get("access-control-allow-origin") == origin) is allowed
        assert "access-control-allow-credentials" not in result.headers
