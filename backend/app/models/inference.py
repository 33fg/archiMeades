"""MCMC and likelihood analysis models."""

from sqlmodel import Field, SQLModel

from app.models.base import BaseTable


class LikelihoodAnalysis(BaseTable, table=True):
    """Likelihood analysis linking theories to observations."""

    __tablename__ = "likelihood_analyses"

    theory_id: str = Field(foreign_key="theories.id")
    observation_id: str = Field(foreign_key="observations.id")
    likelihood_type: str | None = None


class MCMCRun(BaseTable, table=True):
    """MCMC inference run."""

    __tablename__ = "mcmc_runs"

    likelihood_analysis_id: str = Field(foreign_key="likelihood_analyses.id")
    status: str = Field(default="pending", index=True)
    n_steps: int = Field(default=1000)


class MCMCChain(BaseTable, table=True):
    """Individual chain within an MCMC run."""

    __tablename__ = "mcmc_chains"

    mcmc_run_id: str = Field(foreign_key="mcmc_runs.id")
    chain_index: int = Field(default=0)
    s3_key: str | None = Field(default=None)  # Chain samples storage
