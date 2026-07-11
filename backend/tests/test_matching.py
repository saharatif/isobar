"""Cosine similarity, seniority filter, and job ranking."""
from dataclasses import dataclass, field

import pytest

from app.services.matching import cosine_similarity, rank_jobs, seniority_compatible


@dataclass
class FakeJob:
    embedding: list = field(default_factory=list)
    seniority: str | None = None
    title: str = "job"


class TestCosineSimilarity:
    def test_identical_vectors(self):
        assert cosine_similarity([1.0, 2.0, 3.0], [1.0, 2.0, 3.0]) == pytest.approx(1.0)

    def test_orthogonal_vectors(self):
        assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)

    def test_opposite_vectors(self):
        assert cosine_similarity([1.0, 0.0], [-1.0, 0.0]) == pytest.approx(-1.0)

    def test_zero_vector_returns_zero(self):
        assert cosine_similarity([0.0, 0.0], [1.0, 2.0]) == 0.0

    def test_length_mismatch_raises(self):
        with pytest.raises(ValueError):
            cosine_similarity([1.0, 2.0], [1.0])


class TestSeniorityCompatible:
    def test_same_tier(self):
        assert seniority_compatible("senior", "senior")

    def test_adjacent_tier(self):
        assert seniority_compatible("senior", "staff")
        assert seniority_compatible("senior", "mid")

    def test_two_tiers_apart_rejected(self):
        assert not seniority_compatible("junior", "senior")
        assert not seniority_compatible("principal", "senior")
        assert not seniority_compatible("junior", "principal")

    def test_unknown_passes(self):
        assert seniority_compatible(None, "senior")
        assert seniority_compatible("senior", None)
        assert seniority_compatible("wizard", "senior")  # unrecognized tier passes


class TestRankJobs:
    def test_empty_jobs(self):
        assert rank_jobs([1.0, 0.0], "senior", []) == []

    def test_orders_best_first(self):
        close = FakeJob(embedding=[1.0, 0.1])
        far = FakeJob(embedding=[0.1, 1.0])
        ranked = rank_jobs([1.0, 0.0], None, [far, close])
        assert ranked[0][0] is close
        assert ranked[0][1] > ranked[1][1]

    def test_seniority_filter_applied(self):
        junior_job = FakeJob(embedding=[1.0, 0.0], seniority="junior")
        senior_job = FakeJob(embedding=[1.0, 0.0], seniority="senior")
        ranked = rank_jobs([1.0, 0.0], "principal", [junior_job, senior_job])
        assert [job for job, _ in ranked] == []  # both >1 tier from principal? senior is 1 away

    def test_seniority_filter_keeps_adjacent(self):
        staff_job = FakeJob(embedding=[1.0, 0.0], seniority="staff")
        ranked = rank_jobs([1.0, 0.0], "principal", [staff_job])
        assert len(ranked) == 1

    def test_skips_jobs_without_embedding(self):
        ranked = rank_jobs([1.0, 0.0], None, [FakeJob(embedding=None)])
        assert ranked == []

    def test_top_k_limits(self):
        jobs = [FakeJob(embedding=[1.0, float(i)]) for i in range(10)]
        assert len(rank_jobs([1.0, 0.0], None, jobs, top_k=3)) == 3

    def test_scores_clamped_non_negative(self):
        opposite = FakeJob(embedding=[-1.0, 0.0])
        ranked = rank_jobs([1.0, 0.0], None, [opposite])
        assert ranked[0][1] == 0.0
