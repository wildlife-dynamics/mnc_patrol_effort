#!/bin/bash

# Parse flags: --local is consumed by the script, everything else passed to compiler
local_mode=false
compiler_flags=()
for arg in "$@"; do
    case $arg in
        --local) local_mode=true ;;
        *) compiler_flags+=("$arg") ;;
    esac
done
flags="${compiler_flags[*]}"

# Helper to run commands with or without pixi
run_cmd() {
    if [ "$local_mode" = true ]; then
        "$@"
    else
        pixi run --manifest-path pixi.toml -e compile "$@"
    fi
}

# Derive generated directory from spec.yaml id field
WORKFLOW_ID=$(grep '^id:' spec.yaml | sed 's/^id: *//' | tr '_' '-')
GENERATED_DIR="ecoscope-workflows-${WORKFLOW_ID}-workflow"
WORKFLOW_UNDERSCORE=$(grep '^id:' spec.yaml | sed 's/^id: *//')

if [ "$local_mode" = false ]; then
    pixi update --manifest-path pixi.toml -e compile
fi

# (re)initialize dot executable to ensure graphviz is available
run_cmd dot -c

echo "recompiling spec.yaml with flags '--clobber ${flags}'"

run_cmd ecoscope-workflows compile --spec spec.yaml --clobber ${flags}
compile_exit=$?

if [ $compile_exit -ne 0 ]; then
    exit $compile_exit
fi

# Patch the generated cli.py to always enable OTEL console tracing writing to
# otel_traces.jsonl in ECOSCOPE_WORKFLOWS_RESULTS (no CLI flags or env vars needed).
cli_py="${GENERATED_DIR}/ecoscope_workflows_${WORKFLOW_UNDERSCORE}_workflow/cli.py"

if [ -f "$cli_py" ]; then
  echo "Patching ${cli_py} to enable per-task timing by default..."
  sed -i.bak \
    's/    default=None,$/    default="console",/' \
    "$cli_py"
  sed -i.bak \
    's/    default="stdout",$/    default="file",/' \
    "$cli_py"
  rm -f "${cli_py}.bak"
  echo "Patched. Per-task timing will be written to otel_traces.jsonl in ECOSCOPE_WORKFLOWS_RESULTS."

  echo "Patching ${cli_py} to hardcode async as default execution mode..."
  # Make --execution-mode optional with a default of "async"
  sed -i.bak \
    '/--execution-mode/{n;s/    required=True,/    required=False,/}' \
    "$cli_py"
  sed -i.bak \
    's/    type=click.Choice(\["async", "sequential"\]),$/    type=click.Choice(["async", "sequential"]),\n    default="async",/' \
    "$cli_py"
  rm -f "${cli_py}.bak"
  echo "Patched. --execution-mode defaults to async."
fi

# The async DAG compiler drops empty-list values from partial dicts (compiler bug).
# Patch run_async.py and run_async_mock_io.py to restore event_types: [] for
# get_events_data (required arg with no default) and widgets: [] for mnc_events_dashboard.
dags_dir="${GENERATED_DIR}/ecoscope_workflows_${WORKFLOW_UNDERSCORE}_workflow/dags"
python3 - "$dags_dir" << 'PYEOF'
import sys
from pathlib import Path

dags = Path(sys.argv[1])
MARKER = '"include_display_values": False,'
INSERT = '                "event_types": [],'
files = [dags / "run_async.py", dags / "run_async_mock_io.py"]

for f in files:
    if not f.exists():
        continue
    text = f.read_text()
    modified = False

    # Restore event_types: [] for get_events_data
    if '"event_types"' not in text and MARKER in text:
        text = text.replace(MARKER, f'{INSERT}\n                {MARKER}')
        modified = True
        print(f"{f.name}: added event_types=[] to get_events_data partial")
    else:
        print(f"{f.name}: event_types already present or marker not found, skipping")

    # Restore widgets: [] for mnc_events_dashboard (gather_dashboard requires it)
    WIDGETS_MARKER = '"details": DependsOn("workflow_details"),'
    WIDGETS_INSERT = '                "widgets": [],'
    if '"mnc_events_dashboard"' in text and '"widgets"' not in text.split('"mnc_events_dashboard"')[1][:300]:
        if WIDGETS_MARKER in text:
            text = text.replace(WIDGETS_MARKER, f'{WIDGETS_INSERT}\n                {WIDGETS_MARKER}', 1)
            modified = True
            print(f"{f.name}: added widgets=[] to mnc_events_dashboard partial")
    else:
        print(f"{f.name}: widgets already present in mnc_events_dashboard, skipping")

    if modified:
        f.write_text(text)
PYEOF

# The async DAG compiler emits plain list literals for multi-dependency args, but
# gather_dependencies only resolves DependsOnSequence, not plain list. Wrap every
# list-of-only-DependsOn values with DependsOnSequence(...) and add the import.
python3 - "$dags_dir" << 'PYEOF'
import sys, re
from pathlib import Path

dags = Path(sys.argv[1])
files = [dags / "run_async.py", dags / "run_async_mock_io.py"]

IMPORT_OLD = 'from ecoscope_workflows_core.graph import DependsOn, Graph, Node'
IMPORT_NEW = 'from ecoscope_workflows_core.graph import DependsOn, DependsOnSequence, Graph, Node'

DEPENDS_ON_LIST = re.compile(r'\[(?:\n\s+DependsOn\("[^"]+"\),)+\n\s+\]')

for f in files:
    if not f.exists():
        continue
    text = f.read_text()
    modified = False

    if IMPORT_OLD in text:
        text = text.replace(IMPORT_OLD, IMPORT_NEW)
        modified = True
        print(f"{f.name}: added DependsOnSequence to import")

    new_text = DEPENDS_ON_LIST.sub(lambda m: f'DependsOnSequence({m.group(0)})', text)
    if new_text != text:
        text = new_text
        modified = True
        print(f"{f.name}: wrapped DependsOn list literals with DependsOnSequence")

    if modified:
        f.write_text(text)
    else:
        print(f"{f.name}: no DependsOnSequence changes needed")
PYEOF

# Serialize the CPU-intensive grid creation tasks so they never run concurrently.
# The compiler schedules foot/vehicle/motor/combined grids in parallel (they share
# no data dependency), but each create_patrol_coverage_grid call is CPU-heavy enough
# to saturate small machines when all run at once.  Chain them so each waits for the
# previous to finish before starting.
python3 - "$dags_dir" << 'PYEOF'
import sys
from pathlib import Path

dags = Path(sys.argv[1])
files = [dags / "run_async.py", dags / "run_async_mock_io.py"]

replacements = [
    (
        '"vehicle_patrol_grid_visits": ["rename_vehicle_trajs"],',
        '"vehicle_patrol_grid_visits": ["rename_vehicle_trajs", "foot_patrol_grid_visits"],',
    ),
    (
        '"motor_patrol_grid_visits": ["rename_motor_trajs"],',
        '"motor_patrol_grid_visits": ["rename_motor_trajs", "vehicle_patrol_grid_visits"],',
    ),
    (
        '"patrol_grid_visits": ["rename_combined_trajs"],',
        '"patrol_grid_visits": ["rename_combined_trajs", "motor_patrol_grid_visits"],',
    ),
]

for f in files:
    if not f.exists():
        continue
    text = f.read_text()
    modified = False
    for old, new in replacements:
        task = new.split(":")[0].strip().strip('"')
        if old in text:
            text = text.replace(old, new)
            modified = True
            print(f"{f.name}: {task} now waits for previous grid task")
        elif new in text:
            print(f"{f.name}: {task} already serialized, skipping")
        else:
            print(f"Warning: {f.name}: expected dep line for {task} not found, skipping")
    if modified:
        f.write_text(text)
PYEOF

# Make mnc_events_dashboard the final task so dispatch.py always receives a
# BaseModel result. The other terminal nodes (persist_total_df, convert_grid_png,
# persist_occupancy_df) return plain strings; if any finishes after
# mnc_events_dashboard the graph returns that string and model_dump() fails.
python3 - "$dags_dir" << 'PYEOF'
import sys
from pathlib import Path

dags = Path(sys.argv[1])
files = [dags / "run_async.py", dags / "run_async_mock_io.py"]

OLD = '"mnc_events_dashboard": ["workflow_details", "time_range", "groupers"],'
NEW = '"mnc_events_dashboard": ["workflow_details", "time_range", "groupers", "persist_total_df", "convert_grid_png", "persist_occupancy_df"],'

for f in files:
    if not f.exists():
        continue
    text = f.read_text()
    if NEW in text:
        print(f"{f.name}: mnc_events_dashboard already last, skipping")
    elif OLD in text:
        f.write_text(text.replace(OLD, NEW))
        print(f"{f.name}: mnc_events_dashboard now depends on all terminal tasks")
    else:
        print(f"Warning: {f.name}: expected dependency line not found, skipping")
PYEOF

# Copy dev scripts into the workflow package directory so they travel with
# the workflow when the desktop app deploys it to its own template location.
cp "$(dirname "$0")/parse-traces.py" "${GENERATED_DIR}/parse-traces.py"
echo "Copied parse-traces.py into ${GENERATED_DIR}/"
cp "$(dirname "$0")/resource-sampler.py" "${GENERATED_DIR}/resource-sampler.py"
echo "Copied resource-sampler.py into ${GENERATED_DIR}/"
cp "$(dirname "$0")/thread-executor.py" "${GENERATED_DIR}/thread-executor.py"
echo "Copied thread-executor.py into ${GENERATED_DIR}/"

# Generate run-with-traces.py using sys.executable so pixi's own Python is always
# used for subprocesses — bash scripts can't guarantee python3 resolves to the
# pixi Python on all platforms (e.g. Windows where WSL python3 != pixi python).
wrapper="${GENERATED_DIR}/run-with-traces.py"
cat > "$wrapper" << WRAPPER_EOF
#!/usr/bin/env python3
import os, subprocess, sys
from pathlib import Path

script_dir = Path(__file__).parent
workflow_module = "ecoscope_workflows_${WORKFLOW_UNDERSCORE}_workflow"


def _normalize_results_env(uri):
    if not uri.startswith("file://"):
        return uri
    path = uri[7:]
    if len(path) > 2 and path[0] == "/" and path[2] == ":":
        return "file://" + path[1:]
    return uri


results_env = os.environ.get("ECOSCOPE_WORKFLOWS_RESULTS", "")
normalized_env = _normalize_results_env(results_env) if results_env else results_env
rp = normalized_env[7:] if normalized_env.startswith("file://") else normalized_env

env = os.environ.copy()
if normalized_env != results_env:
    env["ECOSCOPE_WORKFLOWS_RESULTS"] = normalized_env

cmd = [sys.executable, str(script_dir / "thread-executor.py"), workflow_module] + sys.argv[1:]
if rp:
    cmd = [sys.executable, str(script_dir / "resource-sampler.py"), rp] + cmd
sys.exit(subprocess.call(cmd, env=env))
WRAPPER_EOF
echo "Generated ${wrapper}"

# Patch the pixi.toml task to call run-with-traces.py instead of the CLI directly.
# Handles both a fresh compile (original CLI entry) and a prior recompile (bash script).
pixi_toml="${GENERATED_DIR}/pixi.toml"
if [ -f "$pixi_toml" ]; then
  python3 - "$pixi_toml" "$WORKFLOW_UNDERSCORE" "$WORKFLOW_ID" << 'PYEOF'
import sys
path, workflow, workflow_hyphen = sys.argv[1], sys.argv[2], sys.argv[3]
new = f'ecoscope-workflows-{workflow_hyphen}-workflow = "python run-with-traces.py"'
old_cli  = f'ecoscope-workflows-{workflow_hyphen}-workflow = "python -m ecoscope_workflows_{workflow}_workflow.cli"'
old_bash = f'ecoscope-workflows-{workflow_hyphen}-workflow = "bash run-with-traces.sh"'
content = open(path).read()
if new in content:
    print(f"{path}: already using run-with-traces.py, skipping")
elif old_cli in content:
    open(path, "w").write(content.replace(old_cli, new))
    print(f"Patched {path}: task now calls run-with-traces.py")
elif old_bash in content:
    open(path, "w").write(content.replace(old_bash, new))
    print(f"Patched {path}: task updated from bash to run-with-traces.py")
else:
    print(f"Warning: expected task line not found in {path}, skipping pixi.toml patch")
PYEOF
fi
