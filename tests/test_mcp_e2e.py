"""
End-to-end sanity checks using Hillary’s example clients exclusively.
"""

from __future__ import annotations
import json
import pytest

from .client_runner import call_client    # <= unchanged helper

pytestmark = pytest.mark.asyncio


# ---------- helpers ---------------------------------------------------------
def _extract_stdout(blob: str) -> str | None:
    """
    The example clients wrap results differently per transport:
      • HTTP/SSE: dict → content[0].text -> str(JSON)
      • STDIO:    same envelope
    This returns the inner 'stdout' value or None.
    """
    try:
        if not blob.lstrip().startswith("{"):
            # to remove INFO log lines
            blob = blob[blob.index("{") :]

        outer = json.loads(blob)
        if isinstance(outer, dict) and outer.get("content"):
            inner = json.loads(outer["content"][0]["text"])
        else:                       # older SSE client may skip envelope
            inner = outer
        return inner.get("stdout")
    except Exception:
        return None


async def _safe_call(ctx: dict, *cli_args) -> str:
    """
    Run the client but downgrade a remote 5xx into pytest.skip
    so CI stays green when the Heroku dyno is asleep.
    """
    try:
        return await call_client(ctx["client"], list(cli_args), ctx["extra_env"])
    except RuntimeError as exc:
        if "503" in str(exc) and ctx["client"].startswith("streamable_http"):
            pytest.skip("remote MCP server unavailable (503)")
        raise


# ---------- actual tests ----------------------------------------------------
async def test_list_tools(ctx):
    data = await _safe_call(ctx, "list_tools")
    assert "html_to_markdown" in data
    assert "pdf_to_markdown" in data


async def test_html_to_markdown(ctx):
    payload = json.dumps({
        "name": "html_to_markdown",
        "arguments": {"url": "https://example.com"}
    })
    data = await _safe_call(ctx, "call_tool", "--args", payload)
    assert "This domain is for use in documentation examples without needing permission" in data


async def test_pdf_to_markdown(ctx):
    payload = json.dumps({
        "name": "pdf_to_markdown",
        "arguments": {"url": "https://www.melbpc.org.au/wp-content/uploads/2017/10/small-example-pdf-file.pdf"}
    })
    data = await _safe_call(ctx, "call_tool", "--args", payload)
    assert "This is a small example PDF file" in data
