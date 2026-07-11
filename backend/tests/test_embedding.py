"""Hashing embedder properties the matcher depends on."""
import math

from app.schemas.extraction import Extraction, RoleItem, SkillItem
from app.services.embedding import EMBEDDING_DIM, candidate_embedding_text, embed_text


class TestEmbedText:
    def test_fixed_dimension(self):
        assert len(embed_text("python engineer")) == EMBEDDING_DIM

    def test_l2_normalized(self):
        vec = embed_text("python fastapi aws")
        assert math.sqrt(sum(v * v for v in vec)) == 1.0 or abs(
            math.sqrt(sum(v * v for v in vec)) - 1.0
        ) < 1e-9

    def test_deterministic(self):
        assert embed_text("python engineer") == embed_text("python engineer")

    def test_empty_text_is_zero_vector(self):
        assert embed_text("") == [0.0] * EMBEDDING_DIM

    def test_different_texts_differ(self):
        assert embed_text("python backend engineer") != embed_text("react frontend designer")


class TestCandidateEmbeddingText:
    def test_concatenates_roles_skills_domains(self):
        extraction = Extraction(
            current_title="Senior Engineer",
            skills=[SkillItem(name="python", weight=1.0)],
            roles=[RoleItem(company="Northwind", title="Backend Engineer")],
        )
        text = candidate_embedding_text(extraction)
        assert "python" in text
        assert "Northwind" in text
        assert "Senior Engineer" in text

    def test_empty_extraction_gives_empty_text(self):
        assert candidate_embedding_text(Extraction()) == ""
