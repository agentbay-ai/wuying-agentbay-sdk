import json
import os
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import asyncio
from ..api.models import (
    GetSkillMetaDataRequest,
    ListSkillMetaDataRequest,
    BindContextSkillAsyncRequest,
    BindContextSkillAsyncRequestContextSkillBindItems,
    UnbindContextSkillRequest,
    UnbindContextSkillRequestContextSkillUnbindItems,
)
from .._common.models.skill_info import SkillInfo, SkillsMetadataResult
from .._common.models.response import OperationResult, extract_request_id
from .._common.logger import get_logger, _log_api_call, _log_api_response

if TYPE_CHECKING:
    from .agentbay import AsyncAgentBay

_logger = get_logger("beta")

DEFAULT_OFFICIAL_SKILLS_ROOT = "/home/wuying/skills"


class AsyncBetaSkillsService:
    """
    Beta skills service.

    Capabilities:
    - Get skills metadata via POP Action `GetSkillMetaData` (supports filtering).
    - List official skills metadata via POP Action `ListSkillMetaData` (deprecated).
    """

    def __init__(self, agent_bay: "AsyncAgentBay", skills_root: Optional[str] = None):
        self._agent_bay = agent_bay
        root = (
            skills_root
            or os.environ.get("AGENTBAY_OFFICIAL_SKILLS_ROOT", "").strip()
            or DEFAULT_OFFICIAL_SKILLS_ROOT
        )
        self._skills_root = root.rstrip("/") or DEFAULT_OFFICIAL_SKILLS_ROOT

    def _build_skill_dir(self, name: str) -> str:
        n = (name or "").strip().lstrip("/")
        return f"{self._skills_root}/{n}" if n else self._skills_root

    async def get_metadata(
        self,
        image_id: Optional[str] = None,
        skill_names: Optional[List[str]] = None,
        skill_ids: Optional[List[str]] = None,
    ) -> SkillsMetadataResult:
        """Get skills metadata without starting a sandbox.

        When ``skill_ids`` is provided the request is routed through the
        ``ListSkillMetaData`` action which supports filtering by skill ID.
        Otherwise the legacy ``GetSkillMetaData`` action is used.

        Args:
            image_id: Image ID to determine the skills root path (GetSkillMetaData only).
            skill_names: Filter by skill group names (GetSkillMetaData only).
            skill_ids: Filter by skill IDs (e.g. ``["builtin:web_search", "sk_xxx"]``).
                When provided, ``image_id`` and ``skill_names`` are ignored.

        Returns:
            SkillsMetadataResult with skills list and skills_root_path.

        Raises:
            RuntimeError: If the API call fails.
        """
        if skill_ids is not None:
            return await self._get_metadata_by_skill_ids(skill_ids)
        return await self._get_metadata_legacy(
            image_id=image_id, skill_names=skill_names
        )

    async def _get_metadata_by_skill_ids(
        self,
        skill_ids: List[str],
    ) -> SkillsMetadataResult:
        request = ListSkillMetaDataRequest(
            authorization=f"Bearer {self._agent_bay.api_key}",
            skill_id_list=skill_ids,
        )

        max_attempts = 3
        delay_s = 0.2
        last_err: Optional[BaseException] = None
        resp = None
        for attempt in range(1, max_attempts + 1):
            try:
                resp = await self._agent_bay.client.list_skill_meta_data_async(request)
                last_err = None
                break
            except Exception as e:
                last_err = e
                msg = str(e)
                if attempt < max_attempts and (
                    "ServiceUnavailable" in msg
                    or "statusCode': 503" in msg
                    or "code: 503" in msg
                ):
                    await asyncio.sleep(delay_s)
                    delay_s *= 2
                    continue
                raise

        if last_err is not None:
            raise RuntimeError(f"ListSkillMetaData failed: {last_err}") from last_err

        body = getattr(resp, "body", None)
        if body is None:
            raise RuntimeError("ListSkillMetaData failed: missing response body")

        if getattr(body, "success", None) is None or not body.success:
            code = str(getattr(body, "code", "") or "")
            msg = str(getattr(body, "message", "") or "")
            if code:
                raise RuntimeError(f"ListSkillMetaData failed: [{code}] {msg}")
            raise RuntimeError(f"ListSkillMetaData failed: {msg or 'Unknown error'}")

        data = getattr(body, "data", None) or []
        if not isinstance(data, list):
            raise RuntimeError("ListSkillMetaData failed: invalid Data field")

        skills: List[SkillInfo] = []
        for raw in data:
            name = str(getattr(raw, "name", "") or "").strip()
            if not name:
                continue
            description = str(getattr(raw, "description", "") or "")
            skill_id = str(getattr(raw, "skill_id", "") or "")
            skills.append(
                SkillInfo(name=name, description=description, skill_id=skill_id)
            )

        return SkillsMetadataResult(
            skills=skills,
            skills_root_path=self._skills_root,
        )

    async def _get_metadata_legacy(
        self,
        image_id: Optional[str] = None,
        skill_names: Optional[List[str]] = None,
    ) -> SkillsMetadataResult:
        request = GetSkillMetaDataRequest(
            authorization=f"Bearer {self._agent_bay.api_key}",
            image_id=image_id,
            skill_group_ids=skill_names,
        )

        max_attempts = 3
        delay_s = 0.2
        last_err: Optional[BaseException] = None
        resp = None
        for attempt in range(1, max_attempts + 1):
            try:
                resp = await self._agent_bay.client.get_skill_meta_data_async(request)
                last_err = None
                break
            except Exception as e:
                last_err = e
                msg = str(e)
                if attempt < max_attempts and (
                    "ServiceUnavailable" in msg
                    or "statusCode': 503" in msg
                    or "code: 503" in msg
                ):
                    await asyncio.sleep(delay_s)
                    delay_s *= 2
                    continue
                raise

        if last_err is not None:
            raise RuntimeError(f"GetSkillMetaData failed: {last_err}") from last_err

        body = getattr(resp, "body", None)
        if body is None:
            raise RuntimeError("GetSkillMetaData failed: missing response body")

        if getattr(body, "success", None) is None or not body.success:
            code = str(getattr(body, "code", "") or "")
            msg = str(getattr(body, "message", "") or "")
            if code:
                raise RuntimeError(f"GetSkillMetaData failed: [{code}] {msg}")
            raise RuntimeError(f"GetSkillMetaData failed: {msg or 'Unknown error'}")

        data = getattr(body, "data", None)
        if data is None:
            raise RuntimeError("GetSkillMetaData failed: missing Data field")

        skill_path = str(getattr(data, "skill_path", "") or "")
        meta_data_list = getattr(data, "meta_data_list", None) or []

        skills: List[SkillInfo] = []
        for raw in meta_data_list:
            name = str(getattr(raw, "name", "") or "").strip()
            if not name:
                continue
            description = str(getattr(raw, "description", "") or "")
            skill_id = str(getattr(raw, "skill_id", "") or "")
            skills.append(
                SkillInfo(name=name, description=description, skill_id=skill_id)
            )

        return SkillsMetadataResult(
            skills=skills,
            skills_root_path=skill_path,
        )

    async def bind_context(
        self,
        items: List[Dict[str, Any]],
    ) -> OperationResult:
        """Bind skills to contexts.

        Args:
            items: List of dicts, each with keys:
                - context_id (str): Target context ID.
                - skill_ids (List[str]): Skill IDs to bind.
                - path (str): Target path in context.

        Returns:
            OperationResult: Result object containing success status and request ID.
        """
        try:
            bind_items = []
            for item in items:
                bind_items.append(
                    BindContextSkillAsyncRequestContextSkillBindItems(
                        context_id=item.get("context_id"),
                        skill_ids=item.get("skill_ids"),
                        path=item.get("path"),
                    )
                )
            request = BindContextSkillAsyncRequest(
                authorization=f"Bearer {self._agent_bay.api_key}",
                context_skill_bind_items=bind_items,
                login_region_id=self._agent_bay.region_id or None,
            )

            _log_api_call("BindContextSkillAsync", f"items_count={len(bind_items)}")

            max_attempts = 3
            delay_s = 0.2
            last_err: Optional[BaseException] = None
            resp = None
            for attempt in range(1, max_attempts + 1):
                try:
                    resp = await self._agent_bay.client.bind_context_skill_async_async(
                        request
                    )
                    last_err = None
                    break
                except Exception as e:
                    last_err = e
                    msg = str(e)
                    if attempt < max_attempts and (
                        "ServiceUnavailable" in msg
                        or "statusCode': 503" in msg
                        or "code: 503" in msg
                    ):
                        await asyncio.sleep(delay_s)
                        delay_s *= 2
                        continue
                    raise

            if last_err is not None:
                return OperationResult(
                    success=False,
                    error_message=f"BindContextSkillAsync failed: {last_err}",
                )

            try:
                response_body = json.dumps(
                    resp.to_map().get("body", {}), ensure_ascii=False, indent=2
                )
                _log_api_response(response_body)
            except Exception:
                _logger.debug(f"Response: {resp}")

            request_id = extract_request_id(resp)

            try:
                response_map = resp.to_map() if hasattr(resp, "to_map") else {}
                if not isinstance(response_map, dict) or not isinstance(
                    response_map.get("body", {}), dict
                ):
                    return OperationResult(
                        request_id=request_id,
                        success=False,
                        error_message="Invalid response format",
                    )
                body = response_map.get("body", {})
                success = body.get("Success", False)
                error_message = (
                    ""
                    if success
                    else f"[{body.get('Code', 'Unknown')}] {body.get('Message', 'Unknown error')}"
                )
                return OperationResult(
                    request_id=request_id,
                    success=success,
                    data=True if success else False,
                    error_message=error_message,
                )
            except Exception as e:
                _logger.exception(f"Error parsing BindContextSkillAsync response: {e}")
                return OperationResult(
                    request_id=request_id,
                    success=False,
                    error_message=f"Failed to parse response: {str(e)}",
                )
        except Exception as e:
            _logger.exception(f"Error calling BindContextSkillAsync: {e}")
            return OperationResult(
                success=False,
                error_message=f"BindContextSkillAsync failed: {e}",
            )

    async def unbind_context(
        self,
        items: List[Dict[str, Any]],
    ) -> OperationResult:
        """Unbind skills from contexts.

        Args:
            items: List of dicts, each with keys:
                - context_id (str): Target context ID.
                - skill_ids (List[str]): Skill IDs to unbind.
                - path (str): Target path in context.

        Returns:
            OperationResult: Result object containing success status and request ID.
        """
        try:
            unbind_items = []
            for item in items:
                unbind_items.append(
                    UnbindContextSkillRequestContextSkillUnbindItems(
                        context_id=item.get("context_id"),
                        skill_ids=item.get("skill_ids"),
                        path=item.get("path"),
                    )
                )
            request = UnbindContextSkillRequest(
                authorization=f"Bearer {self._agent_bay.api_key}",
                context_skill_unbind_items=unbind_items,
                login_region_id=self._agent_bay.region_id or None,
            )

            _log_api_call("UnbindContextSkill", f"items_count={len(unbind_items)}")

            max_attempts = 3
            delay_s = 0.2
            last_err: Optional[BaseException] = None
            resp = None
            for attempt in range(1, max_attempts + 1):
                try:
                    resp = await self._agent_bay.client.unbind_context_skill_async(
                        request
                    )
                    last_err = None
                    break
                except Exception as e:
                    last_err = e
                    msg = str(e)
                    if attempt < max_attempts and (
                        "ServiceUnavailable" in msg
                        or "statusCode': 503" in msg
                        or "code: 503" in msg
                    ):
                        await asyncio.sleep(delay_s)
                        delay_s *= 2
                        continue
                    raise

            if last_err is not None:
                return OperationResult(
                    success=False,
                    error_message=f"UnbindContextSkill failed: {last_err}",
                )

            try:
                response_body = json.dumps(
                    resp.to_map().get("body", {}), ensure_ascii=False, indent=2
                )
                _log_api_response(response_body)
            except Exception:
                _logger.debug(f"Response: {resp}")

            request_id = extract_request_id(resp)

            try:
                response_map = resp.to_map() if hasattr(resp, "to_map") else {}
                if not isinstance(response_map, dict) or not isinstance(
                    response_map.get("body", {}), dict
                ):
                    return OperationResult(
                        request_id=request_id,
                        success=False,
                        error_message="Invalid response format",
                    )
                body = response_map.get("body", {})
                success = body.get("Success", False)
                error_message = (
                    ""
                    if success
                    else f"[{body.get('Code', 'Unknown')}] {body.get('Message', 'Unknown error')}"
                )
                return OperationResult(
                    request_id=request_id,
                    success=success,
                    data=True if success else False,
                    error_message=error_message,
                )
            except Exception as e:
                _logger.exception(f"Error parsing UnbindContextSkill response: {e}")
                return OperationResult(
                    request_id=request_id,
                    success=False,
                    error_message=f"Failed to parse response: {str(e)}",
                )
        except Exception as e:
            _logger.exception(f"Error calling UnbindContextSkill: {e}")
            return OperationResult(
                success=False,
                error_message=f"UnbindContextSkill failed: {e}",
            )


class AsyncBetaNamespace:
    """Beta namespace container for experimental features."""

    def __init__(self, agent_bay: "AsyncAgentBay"):
        self.skills = AsyncBetaSkillsService(agent_bay)
