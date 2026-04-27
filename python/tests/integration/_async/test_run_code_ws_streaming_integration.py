# ci-stable
"""Integration tests for run_code WebSocket streaming."""

import time
import pytest

from agentbay import CreateSessionParams


@pytest.mark.integration
@pytest.mark.asyncio
async def test_run_code_ws_streaming_e2e(make_session):
    lc = await make_session()
    session = lc._result.session
    try:
        stdout_chunks: list[str] = []
        stdout_times: list[float] = []
        stderr_chunks: list[str] = []
        errors: list[object] = []

        def on_stdout(chunk: str) -> None:
            stdout_chunks.append(chunk)
            stdout_times.append(time.monotonic())

        def on_stderr(chunk: str) -> None:
            stderr_chunks.append(chunk)

        def on_error(err: object) -> None:
            errors.append(err)

        start_t = time.monotonic()
        r = await session.code.run_code(
            "import time\n"
            "print('hello', flush=True)\n"
            "time.sleep(1.0)\n"
            "print(2, flush=True)\n",
            "python",
            60,
            stream_beta=True,
            on_stdout=on_stdout,
            on_stderr=on_stderr,
            on_error=on_error,
        )
        end_t = time.monotonic()

        assert errors == [], f"errors={errors}, stdout={stdout_chunks}, stderr={stderr_chunks}"
        assert r.success is True, f"error_message={r.error_message}, stdout={stdout_chunks}, stderr={stderr_chunks}"
        assert len(stdout_chunks) >= 2, f"expected >=2 stdout events, got {len(stdout_chunks)}: {stdout_chunks!r}"
        assert end_t - start_t >= 1.0, f"expected run_code duration >=1.0s, got {end_t - start_t:.3f}s"

        joined = "".join(stdout_chunks)
        assert "hello" in joined
        assert "2" in joined

        hello_t = None
        two_t = None
        for t, chunk in zip(stdout_times, stdout_chunks):
            if hello_t is None and "hello" in chunk:
                hello_t = t
            if two_t is None and "2" in chunk:
                two_t = t
        assert hello_t is not None, f"hello not observed in stdout events: {stdout_chunks!r}"
        assert two_t is not None, f"2 not observed in stdout events: {stdout_chunks!r}"
        assert two_t - hello_t >= 0.8, (
            "stdout callbacks did not behave like streaming; "
            f"delta={two_t - hello_t:.3f}s, chunks={stdout_chunks!r}"
        )
    finally:
        pass

