"""Data profiler: generates profiles for DataFrame variables."""

from __future__ import annotations

import json
from typing import Any

from lembic.models.profile import ColumnProfile, DataProfile


def generate_profile_code(variable_name: str) -> str:
    """Generate Python code to profile a DataFrame variable in the kernel."""
    return f"""
import json as _json_

_df_ = {variable_name}
_profile_ = {{
    "variable_name": "{variable_name}",
    "shape": list(_df_.shape),
    "memory_usage_bytes": int(_df_.memory_usage(deep=True).sum()),
    "columns": [],
    "sample_rows": _json_.loads(_df_.head(5).to_json(orient="records", date_format="iso")),
}}

for _col_ in _df_.columns:
    _s_ = _df_[_col_]
    _cp_ = {{
        "name": str(_col_),
        "dtype": str(_s_.dtype),
        "count": int(_s_.count()),
        "null_count": int(_s_.isna().sum()),
        "unique_count": int(_s_.nunique()),
    }}

    # Top values
    try:
        _vc_ = _s_.value_counts().head(5)
        _cp_["top_values"] = [
            {{"value": str(k), "count": int(v)}} for k, v in _vc_.items()
        ]
    except Exception:
        _cp_["top_values"] = []

    # Numeric stats
    if _s_.dtype.kind in ('i', 'f', 'u'):
        try:
            _cp_["mean"] = float(_s_.mean())
            _cp_["std"] = float(_s_.std())
            _cp_["min"] = float(_s_.min())
            _cp_["max"] = float(_s_.max())
            _cp_["median"] = float(_s_.median())
        except Exception:
            pass

    _profile_["columns"].append(_cp_)

print(_json_.dumps(_profile_))
del _df_, _profile_, _col_, _s_, _cp_, _json_
try:
    del _vc_
except NameError:
    pass
"""


def parse_profile_result(output_text: str) -> DataProfile | None:
    """Parse the JSON output from the profiling code."""
    try:
        data = json.loads(output_text)
        columns = [ColumnProfile(**col) for col in data.get("columns", [])]
        return DataProfile(
            variable_name=data["variable_name"],
            shape=tuple(data["shape"]),
            columns=columns,
            memory_usage_bytes=data.get("memory_usage_bytes", 0),
            sample_rows=data.get("sample_rows", []),
        )
    except (json.JSONDecodeError, KeyError, ValueError):
        return None
