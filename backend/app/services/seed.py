"""Demo job seed — the roadmap's 'small hard-coded city list' for v0.1.

Replaced by the Adzuna ingest cron in v0.5.
"""
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Job
from app.services.embedding import embed_text

_SEED_JOBS = [
    ("Senior Backend Engineer", "Northwind", "London", "GB", 51.5074, -0.1278, "senior", 90000, 120000, "GBP", "python fastapi postgres aws backend engineer"),
    ("Staff ML Engineer", "Contoso AI", "San Francisco", "US", 37.7749, -122.4194, "staff", 210000, 280000, "USD", "pytorch llm ml python engineer machine learning"),
    ("Backend Engineer", "Fabrikam", "Berlin", "DE", 52.52, 13.405, "mid", 70000, 90000, "EUR", "go java backend engineer kubernetes docker"),
    ("Senior Data Engineer", "Adventure Works", "Amsterdam", "NL", 52.3676, 4.9041, "senior", 80000, 105000, "EUR", "sql spark airflow data engineer python"),
    ("DevOps Engineer", "Tailspin", "Austin", "US", 30.2672, -97.7431, "mid", 120000, 150000, "USD", "kubernetes terraform docker aws devops ci/cd engineer"),
    ("Principal Cloud Architect", "Wingtip", "Dubai", "AE", 25.2048, 55.2708, "principal", 220000, 300000, "AED", "aws azure cloud architect kubernetes"),
    ("Senior Frontend Engineer", "Litware", "Toronto", "CA", 43.6532, -79.3832, "senior", 110000, 140000, "CAD", "react typescript javascript frontend engineer"),
    ("ML Engineer", "Proseware", "Singapore", "SG", 1.3521, 103.8198, "mid", 90000, 130000, "SGD", "tensorflow python ml engineer data"),
    ("Senior Python Engineer", "Woodgrove", "New York", "US", 40.7128, -74.006, "senior", 160000, 200000, "USD", "python django postgres backend aws engineer"),
    ("Data Scientist", "Margie's Travel", "London", "GB", 51.5074, -0.1278, "senior", 75000, 95000, "GBP", "python sklearn sql data scientist ml"),
]


async def seed_demo_jobs(session: AsyncSession) -> int:
    count = (await session.execute(select(func.count(Job.id)))).scalar_one()
    if count:
        return 0
    for title, company, city, cc, lat, lon, seniority, cmin, cmax, cur, desc in _SEED_JOBS:
        session.add(
            Job(
                source="seed",
                title=title,
                company=company,
                city=city,
                country_code=cc,
                lat=lat,
                lon=lon,
                seniority=seniority,
                comp_min=cmin,
                comp_max=cmax,
                currency=cur,
                description=desc,
                embedding=embed_text(f"{title} {desc}"),
            )
        )
    await session.commit()
    return len(_SEED_JOBS)
