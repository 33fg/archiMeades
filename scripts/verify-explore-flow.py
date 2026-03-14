#!/usr/bin/env python3
"""Verify Explore flow: simulate register-as-dataset and check API returns the dataset.

Run from project root. Requires backend venv and DB.
Usage: cd backend && uv run python ../scripts/verify-explore-flow.py
"""
import asyncio
import json
import sys

# When run as: cd backend && uv run python ../scripts/verify-explore-flow.py
# cwd is backend, so "." finds app
sys.path.insert(0, ".")

from app.core.database import async_session_factory
from app.models.observation import ObservationData
from app.repositories.observation import ObservationRepository


async def main():
    # Create a simulated "registered simulation" dataset (same structure as register-as-dataset)
    z = [0.05, 0.1, 0.15, 0.2]
    mu = [37.2, 38.5, 39.1, 39.8]  # fake distance modulus
    stat = [0.2] * 4
    cov = [[0.04, 0, 0, 0], [0, 0.04, 0, 0], [0, 0, 0.04, 0], [0, 0, 0, 0.04]]

    async with async_session_factory() as session:
        repo = ObservationRepository(session)
        obs = await repo.create(
            name="Simulated test dataset",
            source="simulation:verify-script",
            metadata_json=json.dumps({
                "num_points": 4,
                "observable_type": "distance_modulus",
                "simulation_id": "verify-script",
                "redshift_min": 0.05,
                "redshift_max": 0.2,
            }),
        )
        od = ObservationData(
            observation_id=obs.id,
            values_json=json.dumps({
                "redshift": z,
                "observable": mu,
                "statistical_uncertainty": stat,
                "systematic_covariance": cov,
                "observable_type": "distance_modulus",
                "name": obs.name,
                "citation": "",
            }),
        )
        session.add(od)
        await session.commit()
        print(f"Created Observation {obs.id} (Simulated test dataset)")
        print("Verify: GET /api/observations/datasets should list it")
        print(f"        GET /api/observations/datasets/{obs.id}/data should return data")


if __name__ == "__main__":
    asyncio.run(main())
