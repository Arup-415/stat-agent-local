import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.dataset_store import dataset_store
from app.memory import session_memory_store


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        test_client.headers.update({"X-Session-ID": "test-session-00000001"})
        yield test_client
    dataset_store.clear()
    session_memory_store.clear()


@pytest.fixture
def csv_file():
    rows = ["value,after,cohort,segment,department,constant"]
    for index in range(18):
        rows.append(
            f"{index + 1 + (index % 3) * 0.13},{index + 2 if index % 3 else index + 1},"
            f"{chr(65 + index % 3)},{chr(88 + index % 2)},"
            f"{chr(77 + (index // 2) % 2)},ONE"
        )
    return ("sample.csv", ("\n".join(rows) + "\n").encode(), "text/csv")


def test_upload_and_profile_return_frontend_metadata(client, csv_file):
    upload = client.post("/upload", files={"file": csv_file})
    assert upload.status_code == 200
    assert upload.json()["numerical_columns"] == ["value", "after"]

    profile = client.post("/descriptive-statistics", files={"file": csv_file})
    assert profile.status_code == 200
    assert {"summary", "numerical", "categorical", "missing", "correlation", "outliers", "histograms"} <= profile.json().keys()


@pytest.mark.parametrize(
    ("test_name", "fields"),
    [
        ("shapiro", {"column": "value"}),
        ("confidence-interval", {"column": "value"}),
        ("adf", {"column": "value"}),
        ("kpss", {"column": "value"}),
        ("pearson", {"column": "value", "second_column": "after"}),
        ("spearman", {"column": "value", "second_column": "after"}),
        ("paired-t-test", {"column": "value", "second_column": "after"}),
        ("wilcoxon", {"column": "value", "second_column": "after"}),
        ("independent-t-test", {"column": "value", "group_column": "segment"}),
        ("mann-whitney", {"column": "value", "group_column": "segment"}),
        ("anova", {"column": "value", "group_column": "cohort"}),
        ("kruskal", {"column": "value", "group_column": "cohort"}),
        ("chi-square", {"column": "segment", "second_column": "department"}),
    ],
)
def test_run_supported_test_families(client, csv_file, test_name, fields):
    response = client.post(
        "/run-test",
        data={"test": test_name, **fields},
        files={"file": csv_file},
    )
    assert response.status_code == 200, response.json()
    assert response.json()["Result"]
    assert response.json()["Sample sizes"]
    assert response.json()["Assumptions and limitations"]
    if test_name in {"independent-t-test", "mann-whitney", "anova", "kruskal"}:
        assert response.json()["Group summaries"]


def test_grouped_test_returns_validation_error_for_single_group(client, csv_file):
    response = client.post(
        "/run-test",
        data={"test": "independent-t-test", "column": "value", "group_column": "constant"},
        files={"file": csv_file},
    )
    assert response.status_code == 400
    assert "at least 2 groups" in response.json()["detail"]


@pytest.mark.parametrize(
    ("filename", "content", "expected_status"),
    [
        ("empty.csv", b"", 400),
        ("broken.csv", b"\xff\xfe", 400),
        ("data.txt", b"value\n1\n", 400),
    ],
)
def test_upload_rejects_empty_malformed_and_non_csv_files(client, filename, content, expected_status):
    response = client.post("/upload", files={"file": (filename, content, "text/csv")})
    assert response.status_code == expected_status


def test_upload_enforces_size_limit(client, monkeypatch):
    import app.main as main

    monkeypatch.setattr(main, "MAX_UPLOAD_BYTES", 12)
    response = client.post("/upload", files={"file": ("large.csv", b"value\n1234567890", "text/csv")})
    assert response.status_code == 413
    assert "12 bytes" in response.json()["detail"]


def test_upload_requires_session_id(csv_file):
    with TestClient(app) as client_without_session:
        response = client_without_session.post("/upload", files={"file": csv_file})
    assert response.status_code == 422


def test_shapiro_rejects_underpowered_sample(client):
    tiny_csv = ("tiny.csv", b"value\n1\n2\n", "text/csv")
    response = client.post("/run-test", data={"test": "shapiro", "column": "value"}, files={"file": tiny_csv})
    assert response.status_code == 400
    assert "at least 3" in response.json()["detail"]


def test_shapiro_rejects_samples_above_supported_limit(client):
    rows = ["value", *(str(index + (index % 7) * 0.1) for index in range(5001))]
    large_sample = ("large-sample.csv", ("\n".join(rows) + "\n").encode(), "text/csv")
    response = client.post("/run-test", data={"test": "shapiro", "column": "value"}, files={"file": large_sample})
    assert response.status_code == 400
    assert "at most 5,000" in response.json()["detail"]


@pytest.mark.parametrize("test_name", ["adf", "kpss"])
def test_stationarity_tests_reject_too_few_observations(client, test_name):
    short_series = ("short.csv", b"time\n1\n2\n3\n4\n5\n6\n7\n", "text/csv")
    response = client.post("/run-test", data={"test": test_name, "column": "time"}, files={"file": short_series})
    assert response.status_code == 400
    assert "at least 8" in response.json()["detail"]


def test_correlation_rejects_constant_column(client):
    constant_csv = ("constant.csv", b"x,y\n1,4\n1,5\n1,6\n", "text/csv")
    response = client.post(
        "/run-test",
        data={"test": "pearson", "column": "x", "second_column": "y"},
        files={"file": constant_csv},
    )
    assert response.status_code == 400
    assert "non-constant" in response.json()["detail"]


def test_chi_square_flags_low_expected_counts(client):
    sparse_csv = ("sparse.csv", b"first,second\nA,X\nA,Y\nB,X\nB,Y\n", "text/csv")
    response = client.post(
        "/run-test",
        data={"test": "chi-square", "column": "first", "second_column": "second"},
        files={"file": sparse_csv},
    )
    assert response.status_code == 200
    assert response.json()["Sample sizes"] == [{"observations": 4}]
    assert "below 5" in response.json()["Diagnostics"][0]


def test_uploaded_datasets_are_isolated_by_session(client, csv_file, monkeypatch):
    import app.agent as agent

    monkeypatch.setattr(agent, "ask_llm", lambda prompt: "Mock explanation")
    first_session = "test-session-aaaaaaaa"
    second_session = "test-session-bbbbbbbb"
    first_upload = client.post("/upload", files={"file": csv_file}, headers={"X-Session-ID": first_session})
    second_csv = ("other.csv", b"score\n10\n20\n", "text/csv")
    second_upload = client.post("/upload", files={"file": second_csv}, headers={"X-Session-ID": second_session})
    assert first_upload.status_code == second_upload.status_code == 200

    first_chat = client.post("/ai/chat", json={"question": "show the dataset overview"}, headers={"X-Session-ID": first_session})
    second_chat = client.post("/ai/chat", json={"question": "show the dataset overview"}, headers={"X-Session-ID": second_session})
    assert first_chat.json()["Result"]["Rows"] == 18
    assert second_chat.json()["Result"]["Rows"] == 2


def test_chat_history_is_isolated_by_session(client, csv_file, monkeypatch):
    import app.agent as agent

    monkeypatch.setattr(agent, "ask_llm", lambda prompt: prompt)
    first_session = "test-session-cccccccc"
    second_session = "test-session-dddddddd"
    for session_id in (first_session, second_session):
        response = client.post("/upload", files={"file": csv_file}, headers={"X-Session-ID": session_id})
        assert response.status_code == 200

    client.post("/ai/chat", json={"question": "Remember SECRET_ALPHA for this chat"}, headers={"X-Session-ID": first_session})
    second_chat = client.post("/ai/chat", json={"question": "What did I ask before?"}, headers={"X-Session-ID": second_session})
    assert "SECRET_ALPHA" not in second_chat.json()["Response"]


@pytest.mark.parametrize(
    "question",
    [
        "run the Shapiro normality test on value",
        "run a paired t-test for value and after",
        "run Mann-Whitney on value by segment",
        "run a Kruskal test on value by cohort",
        "test chi-square association between segment and department",
        "show missing values",
        "show the dataset overview",
        "show outliers",
        "give descriptive statistics",
    ],
)
def test_chat_routes_dataset_questions(client, csv_file, monkeypatch, question):
    import app.agent as agent

    monkeypatch.setattr(agent, "ask_llm", lambda prompt: "Mock explanation")
    upload = client.post("/upload", files={"file": csv_file})
    assert upload.status_code == 200

    response = client.post("/ai/chat", json={"question": question})
    assert response.status_code == 200
    assert "Error" not in response.json()
    assert response.json().get("Test")
    dataset_store.clear()