#!/bin/bash
rp="${ECOSCOPE_WORKFLOWS_RESULTS#file://}"
if [ -n "$rp" ]; then
    python "$PIXI_PROJECT_ROOT/resource-sampler.py" "$rp" python -m ecoscope_workflows_mnc_patrol_effort_workflow.cli "$@"
else
    python -m ecoscope_workflows_mnc_patrol_effort_workflow.cli "$@"
fi
ec=$?
traces="$rp/otel_traces.jsonl"
if [ -f "$traces" ]; then
    python "$PIXI_PROJECT_ROOT/parse-traces.py" "$traces"
fi
exit $ec
