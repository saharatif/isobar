"""KeywordExtractor behaviour and Extraction schema validation."""
from app.schemas.extraction import DomainItem, Extraction, SkillItem
from app.services.extraction import KeywordExtractor, build_extractor
from tests.conftest import SAMPLE_RESUME


class TestExtractionSchema:
    def test_weight_clamped_above_one(self):
        assert SkillItem(name="python", weight=1.7).weight == 1.0

    def test_weight_clamped_below_zero(self):
        assert DomainItem(name="ml", weight=-0.3).weight == 0.0

    def test_years_clamped(self):
        assert Extraction(years_experience=200).years_experience == 60
        assert Extraction(years_experience=-4).years_experience == 0

    def test_defaults_are_empty(self):
        extraction = Extraction()
        assert extraction.skills == []
        assert extraction.domains == []
        assert extraction.name is None


class TestKeywordExtractor:
    def setup_method(self):
        self.extractor = KeywordExtractor()

    def test_finds_skills(self):
        extraction = self.extractor.extract(SAMPLE_RESUME)
        names = {s.name for s in extraction.skills}
        assert {"python", "fastapi", "postgres", "aws"} <= names

    def test_domain_weights_sum_to_one(self):
        extraction = self.extractor.extract(SAMPLE_RESUME)
        assert abs(sum(d.weight for d in extraction.domains) - 1.0) < 1e-9

    def test_seniority_detected(self):
        assert self.extractor.extract(SAMPLE_RESUME).seniority == "senior"

    def test_years_detected(self):
        assert self.extractor.extract(SAMPLE_RESUME).years_experience == 9

    def test_name_detected(self):
        assert self.extractor.extract(SAMPLE_RESUME).name == "Jane Doe"

    def test_empty_text_returns_empty_extraction(self):
        extraction = self.extractor.extract("")
        assert extraction.skills == []
        assert extraction.domains == []
        assert extraction.seniority is None

    def test_deterministic(self):
        a = self.extractor.extract(SAMPLE_RESUME)
        b = self.extractor.extract(SAMPLE_RESUME)
        assert a == b

    def test_word_boundaries_respected(self):
        # "gopher" must not match the skill "go"
        extraction = self.extractor.extract("I photograph gophers")
        assert "go" not in {s.name for s in extraction.skills}


class TestBuildExtractor:
    def test_no_key_returns_keyword_extractor(self):
        assert isinstance(build_extractor(None, "gpt-4o"), KeywordExtractor)

    def test_empty_key_returns_keyword_extractor(self):
        assert isinstance(build_extractor("", "gpt-4o"), KeywordExtractor)
