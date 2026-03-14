#!/usr/bin/env python3
"""Seed a theory and simulation for testing. Run from project root: python scripts/seed-simulation.py"""

import asyncio
import os
import sys
from datetime import datetime, timezone

# Add backend to path so app imports work
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend = os.path.join(root, "backend")
sys.path.insert(0, backend)
os.chdir(backend)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_factory
from app.models.theory import Theory
from app.models.simulation import Simulation
from app.services.provenance_sync import sync_theory, sync_simulation


async def seed():
    async with async_session_factory() as session:
        # Get or create theory
        result = await session.execute(select(Theory).limit(1))
        theory = result.scalar_one_or_none()
        if not theory:
            theory = Theory(
                name="General Relativity",
                description="Einstein field equations describing spacetime curvature",
                equation_spec="G_μν = 8πT_μν",
            )
            session.add(theory)
            await session.commit()
            await session.refresh(theory)
            print(f"Created theory: {theory.name} ({theory.id})")
        else:
            print(f"Using existing theory: {theory.name} ({theory.id})")

        # Create simulation
        sim = Simulation(
            theory_id=theory.id,
            status="completed",
            progress_percent=100.0,
            started_at=datetime.now(timezone.utc).isoformat(),
            completed_at=datetime.now(timezone.utc).isoformat(),
        )
        session.add(sim)
        await session.commit()
        await session.refresh(sim)
        print(f"Created simulation: {sim.id} (status: {sim.status})")

        # Sync to Neo4j for provenance
        try:
            sync_theory(theory.id, identifier=getattr(theory, "identifier", None))
            sync_simulation(sim.id, sim.theory_id, status=sim.status)
            print("Synced to Neo4j (provenance)")
        except Exception as e:
            print(f"Neo4j sync skipped: {e}")

        print(f"\nOpen: http://localhost:5173/simulations/{sim.id}")


if __name__ == "__main__":
    asyncio.run(seed())
