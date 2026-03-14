# Repository Pattern (WO-6)

Data access abstraction using the repository pattern with SQLModel. Provides consistent CRUD operations, eager loading, and dependency injection.

## Overview

- **BaseRepository**: Generic CRUD (`create`, `get_by_id`, `list`, `update`, `delete`), pagination, filtering, sorting
- **Eager loading**: Use `options` parameter with `selectinload` to prevent N+1 queries
- **Domain repositories**: UserRepository, TheoryRepository, SimulationRepository, ObservationRepository, JobRepository, SimulationOutputRepository

## BaseRepository API

| Method | Description |
|--------|-------------|
| `create(**kwargs)` | Create and return a new record |
| `get_by_id(id, options=...)` | Get by primary key; optional eager loading |
| `exists(id)` | Check if record exists |
| `list(limit, offset, order_by, options, **filters)` | List with pagination, sorting, filtering, eager loading |
| `update(id, **kwargs)` | Update and return record, or None |
| `delete(id)` | Delete record; returns True if found |

## Eager Loading

Use `selectinload` to load relationships in a single query and avoid N+1:

```python
from sqlalchemy.orm import selectinload
from app.models.simulation import Simulation
from app.repositories.simulation import SimulationRepository

# Get simulation with theory loaded
sim = await repo.get_by_id_with_theory(simulation_id)
# sim.theory is loaded (no extra query)

# Or use options directly
sim = await repo.get_by_id(
    simulation_id,
    options=(selectinload(Simulation.theory),),
)

# List with theory
sims = await repo.list_with_theory(limit=20, status="completed")
```

## Dependency Injection

Repository dependencies are available in `app.core.dependencies`:

- `get_theory_repository(session)` → TheoryRepository
- `get_user_repository(session)` → UserRepository

Routers can also instantiate repositories directly:

```python
from app.repositories.simulation import SimulationRepository

@router.get("/simulations/{id}")
async def get_simulation(id: str, session: AsyncSession = Depends(get_db)):
    repo = SimulationRepository(session)
    sim = await repo.get_by_id_with_theory(id)
    if not sim:
        raise HTTPException(404)
    return sim
```

## Transaction Management

Sessions are request-scoped via `get_db`. The session commits on success and rolls back on exception. Repositories use the same session—no explicit transaction handling needed at the repository layer.

## Soft Delete

`SoftDeleteMixin` exists in `app.models.base` for models that need soft delete. To use:

1. Add `SoftDeleteMixin` to the model and `deleted_at` column (migration required)
2. Override `list` and `get_by_id` in the repository to filter `deleted_at.is_(None)`
3. Add `soft_delete(id)` that sets `deleted_at` instead of hard delete

## Related Documentation

- [API_INTEGRATION.md](./API_INTEGRATION.md) – Frontend API patterns
- [MIGRATIONS.md](./MIGRATIONS.md) – Schema changes
