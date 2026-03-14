#!/usr/bin/env python3
"""Seed a theory with executable code for API v1 testing.
Run from project root: python scripts/seed-api-theory.py
"""

import asyncio
import os
import sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend = os.path.join(root, "backend")
sys.path.insert(0, backend)
os.chdir(backend)

from sqlalchemy import select
from app.core.database import async_session_factory
from app.models.theory import Theory
from app.repositories.theory import TheoryRepository

# Lambda-CDM-like theory with luminosity_distance and hubble_parameter
LAMBDA_CDM_CODE = '''
def luminosity_distance(z, params):
    """Luminosity distance in Mpc (simplified Lambda-CDM)."""
    H0 = params.get("H0", 67.36)
    # d_L = (1+z) * comoving_distance; simplified: d_L ~ (1+z)*z*c/H0 for low z
    c = 299792.458  # km/s
    return (1 + z) * z * c / H0

def age_of_universe(params):
    """Age of universe in Gyr."""
    return 13.8

def hubble_parameter(z, params):
    """H(z) in km/s/Mpc."""
    H0 = params.get("H0", 67.36)
    Om = params.get("Om", 0.315)
    Ode = params.get("Ode", 0.6847)
    # H(z) = H0 * sqrt(Om*(1+z)^3 + Ode)
    return H0 * (Om * (1 + z) ** 3 + Ode) ** 0.5
'''


async def seed():
    async with async_session_factory() as session:
        repo = TheoryRepository(session)
        existing = await repo.get_by_identifier("lambdacdm")
        if existing:
            print(f"Theory lambdacdm exists: {existing.id}")
            return
        theory = await repo.create(
            name="Lambda-CDM",
            identifier="lambdacdm",
            version="1.0",
            description="Standard cosmological model",
            code=LAMBDA_CDM_CODE,
            validation_passed=True,
        )
        await session.commit()
        print(f"Created theory: {theory.name} (identifier: lambdacdm)")
        print("Test: curl -H 'Authorization: Bearer <api_key>' http://localhost:8002/api/v1/theories")


if __name__ == "__main__":
    asyncio.run(seed())
