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
fi

# Copy dev scripts into the workflow package directory so they travel with
# the workflow when the desktop app deploys it to its own template location.
cp "$(dirname "$0")/parse-traces.py" "${GENERATED_DIR}/parse-traces.py"
echo "Copied parse-traces.py into ${GENERATED_DIR}/"
cp "$(dirname "$0")/resource-sampler.py" "${GENERATED_DIR}/resource-sampler.py"
echo "Copied resource-sampler.py into ${GENERATED_DIR}/"

# Generate run-with-traces.sh referencing co-located scripts via
# PIXI_PROJECT_ROOT (set by pixi to the workflow package directory at runtime).
wrapper="${GENERATED_DIR}/run-with-traces.sh"
cat > "$wrapper" << WRAPPER_EOF
#!/bin/bash
rp="\${ECOSCOPE_WORKFLOWS_RESULTS#file://}"
if [ -n "\$rp" ]; then
    python "\$PIXI_PROJECT_ROOT/resource-sampler.py" "\$rp" python -m ecoscope_workflows_${WORKFLOW_UNDERSCORE}_workflow.cli "\$@"
else
    python -m ecoscope_workflows_${WORKFLOW_UNDERSCORE}_workflow.cli "\$@"
fi
ec=\$?
traces="\$rp/otel_traces.jsonl"
if [ -f "\$traces" ]; then
    python "\$PIXI_PROJECT_ROOT/parse-traces.py" "\$traces"
fi
exit \$ec
WRAPPER_EOF
chmod +x "$wrapper"
echo "Generated ${wrapper}"

# Patch the pixi.toml task to call run-with-traces.sh instead of the CLI directly.
pixi_toml="${GENERATED_DIR}/pixi.toml"
if [ -f "$pixi_toml" ]; then
  python3 - "$pixi_toml" "$WORKFLOW_UNDERSCORE" "$WORKFLOW_ID" << 'PYEOF'
import sys
path, workflow, workflow_hyphen = sys.argv[1], sys.argv[2], sys.argv[3]
old = f'ecoscope-workflows-{workflow_hyphen}-workflow = "python -m ecoscope_workflows_{workflow}_workflow.cli"'
new = f'ecoscope-workflows-{workflow_hyphen}-workflow = "bash run-with-traces.sh"'
content = open(path).read()
if old in content:
    open(path, "w").write(content.replace(old, new))
    print(f"Patched {path}: task now calls run-with-traces.sh")
else:
    print(f"Warning: expected task line not found in {path}, skipping pixi.toml patch")
PYEOF
fi
