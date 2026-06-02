"""ccscores — reference calculation engine for critical-care score definitions.

Stdlib-only (Python >= 3.11), matching the project's tooling ethos. This is the
*reference* implementation: the TypeScript engine under web/src/engine must
reproduce every golden vector this engine produces (dual-implementation V&V,
IEC 62304 style).

Public API:
    load_definition(path)        -> dict   (parsed + minimally checked)
    compute(definition, inputs)  -> Result (score, band, per-input breakdown)
    EngineError                            (raised on bad definition or input)
"""

from .engine import Result, compute, load_definition
from .errors import EngineError

__all__ = ["Result", "compute", "load_definition", "EngineError"]
__version__ = "0.1.0"
