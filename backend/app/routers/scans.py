"""WO-31/33: Parameter scan API with HDF5 storage."""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.models.scan import ParameterScan
from app.scans.runner import run_scan
from app.scans.storage import load_scan_hdf5, save_scan_hdf5

router = APIRouter(prefix="/api/scans", tags=["scans"])



class AxisConfig(BaseModel):
    name: str
    min: float
    max: float
    n: int
    scale: str = "linear"


class CreateScanRequest(BaseModel):
    theory_id: str
    dataset_id: str
    axes: list[AxisConfig]
    fixed_params: dict | None = None


@router.post("")
async def create_scan(body: CreateScanRequest, session: AsyncSession = Depends(get_db)):
    """Submit parameter scan. Runs synchronously for small grids."""
    axes_config = [a.model_dump() for a in body.axes]
    if not axes_config:
        raise HTTPException(422, "At least one axis required")

    total = 1
    for a in axes_config:
        total *= a["n"]
    if total > 100_000:
        raise HTTPException(422, f"Grid too large: {total} points (max 100k)")

    scan = ParameterScan(
        theory_id=body.theory_id,
        dataset_id=body.dataset_id,
        axes_config=axes_config,
        fixed_params=body.fixed_params or {},
        status="running",
        total_points=total,
    )
    session.add(scan)
    await session.commit()
    await session.refresh(scan)

    try:
        chi2, shape = run_scan(
            theory_id=body.theory_id,
            dataset_id=body.dataset_id,
            axes_config=axes_config,
            fixed_params=body.fixed_params,
        )
        scan.status = "completed"
        scan.result_shape = shape
        rel_path = save_scan_hdf5(
            str(scan.id),
            chi2,
            shape,
            axes_config,
            body.fixed_params or {},
            body.theory_id,
            body.dataset_id,
        )
        scan.result_ref = f"h5:{rel_path}"
        session.add(scan)
        await session.commit()
        await session.refresh(scan)
    except Exception as e:
        scan.status = "failed"
        scan.error_message = str(e)
        session.add(scan)
        await session.commit()
        await session.refresh(scan)
        raise HTTPException(500, str(e)) from e

    return {
        "id": scan.id,
        "theory_id": scan.theory_id,
        "dataset_id": scan.dataset_id,
        "status": scan.status,
        "total_points": total,
        "result_shape": scan.result_shape,
        "has_result": scan.result_ref is not None,
    }


@router.get("")
async def list_scans(session: AsyncSession = Depends(get_db)):
    """List parameter scans."""
    stmt = select(ParameterScan).order_by(ParameterScan.created_at.desc()).limit(100)
    result = await session.execute(stmt)
    scans = result.scalars().all()
    return [
        {
            "id": s.id,
            "theory_id": s.theory_id,
            "dataset_id": s.dataset_id,
            "status": s.status,
            "total_points": s.total_points,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in scans
    ]


def _load_result(scan: ParameterScan):
    """Load result values from HDF5 or legacy inline."""
    if not scan.result_ref:
        return None
    if scan.result_ref.startswith("h5:"):
        path = scan.result_ref[3:].replace(".h5", "")
        data = load_scan_hdf5(path)
        return data["chi2"].ravel().tolist()
    # Legacy inline (comma-separated)
    return [float(x) for x in scan.result_ref.split(",")]


@router.get("/{scan_id}")
async def get_scan(scan_id: str, session: AsyncSession = Depends(get_db)):
    """Get scan details and result."""
    scan = await session.get(ParameterScan, scan_id)
    if not scan:
        raise HTTPException(404, "Scan not found")
    result_values = None
    if scan.result_ref:
        try:
            result_values = _load_result(scan)
        except Exception:
            result_values = None
    return {
        "id": str(scan.id),
        "theory_id": scan.theory_id,
        "dataset_id": scan.dataset_id,
        "axes_config": scan.axes_config,
        "fixed_params": scan.fixed_params,
        "status": scan.status,
        "total_points": scan.total_points,
        "result_shape": scan.result_shape,
        "result": result_values,
        "error_message": scan.error_message,
        "created_at": scan.created_at.isoformat() if scan.created_at else None,
    }


@router.get("/{scan_id}/slice")
async def get_scan_slice(
    scan_id: str,
    axis0: int = Query(0, description="First axis index"),
    axis1: int = Query(1, description="Second axis index"),
    slice_axis: int | None = Query(None, description="Axis to slice (for 3D)"),
    slice_index: int | None = Query(None, description="Index along slice_axis"),
    session: AsyncSession = Depends(get_db),
):
    """Get 2D slice for visualization. For 3D: specify slice_axis and slice_index."""
    scan = await session.get(ParameterScan, scan_id)
    if not scan or not scan.result_ref:
        raise HTTPException(404, "Scan not found or no result")
    if not scan.result_ref or not scan.result_ref.startswith("h5:"):
        raise HTTPException(400, "No HDF5 result for this scan")
    path = scan.result_ref[3:].replace(".h5", "")
    data = load_scan_hdf5(path)
    chi2 = data["chi2"]
    shape = data["shape"]
    axis_1d = data["axis_1d"]
    if len(shape) == 1:
        return {"x": axis_1d[0].tolist(), "chi2": chi2.ravel().tolist(), "ndim": 1}
    if len(shape) == 2:
        return {
            "x": axis_1d[0].tolist(),
            "y": axis_1d[1].tolist(),
            "chi2": chi2.tolist(),
            "ndim": 2,
        }
    if len(shape) == 3 and slice_axis is not None and slice_index is not None:
        slc = [slice(None)] * 3
        slc[slice_axis] = slice_index
        chi2_2d = chi2[tuple(slc)]
        ax0, ax1 = [i for i in range(3) if i != slice_axis]
        return {
            "x": axis_1d[ax0].tolist(),
            "y": axis_1d[ax1].tolist(),
            "chi2": chi2_2d.tolist(),
            "ndim": 2,
            "slice_axis": slice_axis,
            "slice_index": slice_index,
        }
    raise HTTPException(400, "For 3D scans specify slice_axis and slice_index")


@router.get("/{scan_id}/profile")
async def get_scan_profile(
    scan_id: str,
    axis: int = Query(0, description="Axis to profile (marginalize over others)"),
    session: AsyncSession = Depends(get_db),
):
    """Get 1D marginalized profile: min chi2 at each value of the specified axis."""
    scan = await session.get(ParameterScan, scan_id)
    if not scan or not scan.result_ref:
        raise HTTPException(404, "Scan not found or no result")
    if not scan.result_ref or not scan.result_ref.startswith("h5:"):
        raise HTTPException(400, "No HDF5 result for this scan")
    path = scan.result_ref[3:].replace(".h5", "")
    data = load_scan_hdf5(path)
    chi2_arr = data["chi2"]
    axis_1d = data["axis_1d"]
    # Marginalize: min over all other axes
    profile = chi2_arr.min(axis=tuple(i for i in range(chi2_arr.ndim) if i != axis))
    return {
        "x": axis_1d[axis].tolist(),
        "chi2_min": profile.tolist(),
        "axis_index": axis,
        "axis_name": (data.get("axes_config") or scan.axes_config or [{}])[axis].get("name", ""),
    }


@router.get("/{scan_id}/bestfit")
async def get_scan_bestfit(
    scan_id: str,
    session: AsyncSession = Depends(get_db),
):
    """Get best-fit parameters (argmin chi2) and chi2 value."""
    scan = await session.get(ParameterScan, scan_id)
    if not scan or not scan.result_ref or not scan.result_ref.startswith("h5:"):
        raise HTTPException(404, "Scan not found or no result")
    path = scan.result_ref[3:].replace(".h5", "")
    data = load_scan_hdf5(path)
    chi2_arr = data["chi2"]
    flat_arrays = data["flat_arrays"]
    flat_idx = int(chi2_arr.argmin())
    best_params = dict(scan.fixed_params or {})
    for i, arr in enumerate(flat_arrays):
        name = (data.get("axes_config") or scan.axes_config or [{}])[i].get("name", f"axis_{i}")
        best_params[name] = float(arr[flat_idx])
    return {
        "chi2_min": float(chi2_arr.ravel()[flat_idx]),
        "bestfit_params": best_params,
    }


@router.get("/{scan_id}/download")
async def download_scan(
    scan_id: str,
    session: AsyncSession = Depends(get_db),
):
    """Download scan result as HDF5 file."""
    scan = await session.get(ParameterScan, scan_id)
    if not scan or not scan.result_ref or not scan.result_ref.startswith("h5:"):
        raise HTTPException(404, "Scan not found or no result")
    from app.scans.storage import SCAN_STORAGE_DIR
    path = SCAN_STORAGE_DIR / scan.result_ref[3:]
    if not path.exists():
        raise HTTPException(404, "Scan file not found")
    return FileResponse(path, filename=f"scan_{scan_id}.h5", media_type="application/octet-stream")
