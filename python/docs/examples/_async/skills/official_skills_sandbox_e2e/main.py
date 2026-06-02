"""
Official skills sandbox E2E smoke test (no mocks).

This example validates:
- A custom image that contains official skills under /home/wuying/skills
- Reading one skill's SKILL.md from inside the sandbox
- Writing and reading a report file under /tmp
- (Optional) Calling POP Action GetSkillMetaData via AsyncAgentBay.beta.skills.get_metadata()
"""

import asyncio
import os
from typing import Any, Dict, List, Optional

from agentbay import AsyncAgentBay
from agentbay._common.models.skill_info import SkillsMetadataResult
from agentbay._common.params.session_params import CreateSessionParams


DEFAULT_IMAGE_ID = "linux_latest"
SKILLS_ROOT = "/home/wuying/skills"


def _preview(text: str, limit: int = 800) -> str:
    t = (text or "").strip()
    if len(t) <= limit:
        return t
    return t[: limit - 3] + "..."


async def _safe_get_metadata(agent_bay: AsyncAgentBay) -> Optional[SkillsMetadataResult]:
    try:
        return await agent_bay.beta.skills.get_metadata()
    except Exception as e:
        print("[warn] GetSkillMetaData failed, will continue without backend metadata.")
        print(f"[warn] error={e}")
        return None


def _pick_skill_name(entries: List[Dict[str, Any]]) -> str:
    forced = os.environ.get("AGENTBAY_E2E_SKILL_NAME", "").strip()
    if forced:
        return forced
    dirs = [e.get("name") for e in entries if e.get("isDirectory") is True and e.get("name")]
    if not dirs:
        raise RuntimeError(f"No skill directories found under {SKILLS_ROOT}")
    return str(dirs[0])


async def main() -> None:
    api_key = os.environ.get("AGENTBAY_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("AGENTBAY_API_KEY is required")

    image_id = os.environ.get("AGENTBAY_SKILLS_IMAGE_ID", "").strip() or DEFAULT_IMAGE_ID

    agent_bay = AsyncAgentBay(api_key=api_key)
    metadata_result = await _safe_get_metadata(agent_bay)
    if metadata_result is not None:
        print(f"[backend] skills_count={len(metadata_result.skills)}")

    create_res = await agent_bay.create(params=CreateSessionParams(image_id=image_id))
    if not create_res.success or not create_res.session:
        raise RuntimeError(create_res.error_message or "Failed to create session")

    session = create_res.session
    try:
        list_res = await session.file_system.list_directory(SKILLS_ROOT)
        if not list_res.success:
            raise RuntimeError(list_res.error_message or f"Failed to list {SKILLS_ROOT}")

        skill_name = _pick_skill_name(list_res.entries or [])
        skill_dir = f"{SKILLS_ROOT}/{skill_name}"
        skill_md_path = f"{skill_dir}/SKILL.md"
        print(f"[sandbox] selected_skill={skill_name}")
        print(f"[sandbox] skill_md={skill_md_path}")

        md_res = await session.file_system.read_file(skill_md_path, format="text")
        if not md_res.success:
            raise RuntimeError(md_res.error_message or f"Failed to read {skill_md_path}")
        skill_md = md_res.content or ""
        if not skill_md.strip():
            raise RuntimeError(f"SKILL.md is empty: {skill_md_path}")

        print("========== [SKILL.md preview] ==========")
        print(_preview(skill_md))
        print("=======================================")

        if metadata_result is not None:
            backend_names = {s.name for s in metadata_result.skills}
            if skill_name not in backend_names:
                print("[warn] Selected skill is not present in backend metadata list.")

        out_path = "/tmp/official_skill_e2e_report.md"
        report = (
            "# Official Skill E2E Report\n\n"
            f"- image_id: {image_id}\n"
            f"- skills_root: {SKILLS_ROOT}\n"
            f"- selected_skill: {skill_name}\n"
            f"- skill_md: {skill_md_path}\n\n"
            "## SKILL.md Preview\n\n"
            "```text\n"
            f"{_preview(skill_md, limit=1200)}\n"
            "```\n"
        )

        w = await session.file_system.write_file(out_path, report, mode="overwrite")
        if not w.success:
            raise RuntimeError(w.error_message or f"Failed to write {out_path}")

        v = await session.file_system.read_file(out_path, format="text")
        if not v.success or not (v.content or "").strip():
            raise RuntimeError(v.error_message or f"Failed to verify {out_path}")

        print(f"[sandbox] report_ok path={out_path} chars={len(v.content or '')}")
    finally:
        await session.delete()


if __name__ == "__main__":
    asyncio.run(main())
