"""End-to-end API tests: upload → candidate → snapshot → delete, plus edge cases."""
from tests.conftest import SAMPLE_RESUME, make_settings


def create_candidate(client, uploaded: dict) -> dict:
    response = client.post(
        "/candidates",
        json={
            "file_key": uploaded["file_key"],
            "filename": uploaded["filename"],
            "mime_type": uploaded["mime_type"],
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


class TestHealth:
    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestUploads:
    def test_upload_text_resume(self, client):
        response = client.post(
            "/uploads",
            files={"file": ("jane.txt", SAMPLE_RESUME.encode(), "text/plain")},
        )
        assert response.status_code == 201
        body = response.json()
        assert body["size_bytes"] == len(SAMPLE_RESUME.encode())
        assert body["mime_type"] == "text/plain"
        assert len(body["file_key"]) == 36  # server-generated UUID

    def test_unsupported_type_rejected(self, client):
        response = client.post(
            "/uploads", files={"file": ("x.png", b"\x89PNG", "image/png")}
        )
        assert response.status_code == 415

    def test_empty_file_rejected(self, client):
        response = client.post(
            "/uploads", files={"file": ("x.txt", b"", "text/plain")}
        )
        assert response.status_code == 422

    def test_oversized_file_rejected(self, tmp_path):
        from fastapi.testclient import TestClient

        from app.main import create_app

        app = create_app(make_settings(tmp_path, max_upload_bytes=10))
        with TestClient(app) as client:
            response = client.post(
                "/uploads",
                files={"file": ("x.txt", b"x" * 100, "text/plain")},
            )
            assert response.status_code == 413


class TestCreateCandidate:
    def test_full_pipeline(self, client, uploaded_resume):
        candidate = create_candidate(client, uploaded_resume)
        assert candidate["status"] == "matched"
        assert candidate["name"] == "Jane Doe"
        assert candidate["seniority"] == "senior"
        assert candidate["years_exp"] == 9
        assert 0 <= candidate["signal_score"] <= 100

    def test_unknown_file_key_404(self, client):
        response = client.post(
            "/candidates",
            json={
                "file_key": "00000000-0000-0000-0000-000000000000",
                "filename": "ghost.txt",
                "mime_type": "text/plain",
            },
        )
        assert response.status_code == 404

    def test_malformed_file_key_rejected(self, client):
        response = client.post(
            "/candidates",
            json={
                "file_key": "../../etc/passwd",
                "filename": "evil",
                "mime_type": "text/plain",
            },
        )
        assert response.status_code == 422

    def test_unparseable_upload_is_422_not_500(self, client):
        # A blank-page (scanned-looking) PDF passes upload but fails parsing.
        import pymupdf

        doc = pymupdf.open()
        doc.new_page()
        blank_pdf = doc.tobytes()
        doc.close()

        uploaded = client.post(
            "/uploads",
            files={"file": ("scan.pdf", blank_pdf, "application/pdf")},
        ).json()
        response = client.post(
            "/candidates",
            json={
                "file_key": uploaded["file_key"],
                "filename": "scan.pdf",
                "mime_type": "application/pdf",
            },
        )
        assert response.status_code == 422
        assert "scanned" in response.json()["detail"].lower()

    def test_missing_body_fields_422(self, client):
        response = client.post("/candidates", json={})
        assert response.status_code == 422


class TestReadCandidate:
    def test_get_candidate(self, client, uploaded_resume):
        created = create_candidate(client, uploaded_resume)
        response = client.get(f"/candidates/{created['id']}")
        assert response.status_code == 200
        assert response.json()["id"] == created["id"]

    def test_get_unknown_candidate_404(self, client):
        assert client.get("/candidates/nope").status_code == 404

    def test_snapshot_shape(self, client, uploaded_resume):
        created = create_candidate(client, uploaded_resume)
        response = client.get(f"/candidates/{created['id']}/snapshot")
        assert response.status_code == 200
        snapshot = response.json()

        assert snapshot["candidate"]["id"] == created["id"]
        assert snapshot["skills"], "expected extracted skills"
        assert snapshot["domains"], "expected extracted domains"
        assert snapshot["opportunities"], "expected matches against seeded jobs"
        assert snapshot["markets_matched"] >= 1
        assert snapshot["markets_matched"] >= len(snapshot["hotspots"])
        for opp in snapshot["opportunities"]:
            assert 0 <= opp["match_pct"] <= 100
        for hotspot in snapshot["hotspots"]:
            assert 0 <= hotspot["demand_score"] <= 100
            assert hotspot["open_roles"] >= 1

    def test_snapshot_unknown_candidate_404(self, client):
        assert client.get("/candidates/nope/snapshot").status_code == 404


class TestDeleteCandidate:
    def test_delete_removes_candidate_and_file(self, client, uploaded_resume, settings):
        created = create_candidate(client, uploaded_resume)
        stored_file = settings.storage_dir / uploaded_resume["file_key"]
        assert stored_file.exists()

        response = client.delete(f"/candidates/{created['id']}")
        assert response.status_code == 204
        assert client.get(f"/candidates/{created['id']}").status_code == 404
        assert not stored_file.exists(), "GDPR delete must remove the stored file"

    def test_delete_unknown_candidate_404(self, client):
        assert client.delete("/candidates/nope").status_code == 404
