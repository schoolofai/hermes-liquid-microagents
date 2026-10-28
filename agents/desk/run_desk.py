"""Desk microagent: LFM3-1.7B inside Hermes (AIAgent) against a local llama-server."""
import os, sys
from run_agent import AIAgent  # from an activated hermes-agent checkout
sandbox = os.path.abspath(sys.argv[1] if len(sys.argv)>1 else "sandbox"); os.chdir(sandbox)
agent = AIAgent(
    model=os.environ.get("DESK_MODEL","LFM3-1.7B"),
    base_url=os.environ.get("DESK_URL","http://127.0.0.1:8084/v1"),
    api_key="local", enabled_toolsets=["file"], skip_memory=True, skip_context_files=True,
    ephemeral_system_prompt=open(os.path.join(os.path.dirname(os.path.abspath(__file__)),"SOUL.md")).read(),
    max_iterations=int(os.environ.get("DESK_MAX_ITERS","40")), save_trajectories=True, quiet_mode=True)
print(agent.chat("Do jobs 1 to 5 now. Reply DONE with a one-line summary when finished."))
