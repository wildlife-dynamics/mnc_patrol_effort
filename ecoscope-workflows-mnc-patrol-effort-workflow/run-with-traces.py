#!/usr/bin/env python3
import os, subprocess, sys
from pathlib import Path

script_dir = Path(__file__).parent
workflow_module = "ecoscope_workflows_mnc_patrol_effort_workflow"


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
