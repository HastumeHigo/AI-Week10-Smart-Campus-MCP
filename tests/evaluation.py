from __future__ import annotations

import asyncio
import csv
import json
import sys
import time
from pathlib import Path

from mcp import Client, StdioServerParameters


PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]

SERVER_FILE = (
    PROJECT_ROOT
    / "src"
    / "server"
    / "smart_campus_server.py"
)

RESULTS_DIR = (
    PROJECT_ROOT
    / "results"
)

RESULTS_FILE = (
    RESULTS_DIR
    / "mcp_test_results.csv"
)

RESULTS_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


TEST_CASES = [
    {
        "id": 1,
        "name": "Health Check",
        "tool": "health_check",
        "arguments": {},
    },
    {
        "id": 2,
        "name": "Search A203",
        "tool": "search_room",
        "arguments": {
            "room_id": "A203"
        },
    },
    {
        "id": 3,
        "name": "Unknown Room",
        "tool": "search_room",
        "arguments": {
            "room_id": "XYZ999"
        },
    },
    {
        "id": 4,
        "name": "Device Status A203",
        "tool": "get_device_status",
        "arguments": {
            "room_id": "A203"
        },
    },
    {
        "id": 5,
        "name": "Find Room 40 A Projector",
        "tool": "find_available_room",
        "arguments": {
            "capacity": 40,
            "building": "A",
            "require_projector": True,
        },
    },
    {
        "id": 6,
        "name": "Impossible Capacity",
        "tool": "find_available_room",
        "arguments": {
            "capacity": 500,
            "building": "A",
            "require_projector": True,
        },
    },
]


def extract_result(result):

    structured = getattr(
        result,
        "structured_content",
        None,
    )

    if structured is not None:
        return structured

    content = getattr(
        result,
        "content",
        None,
    )

    texts = []

    if content:

        for item in content:

            if hasattr(
                item,
                "text",
            ):
                texts.append(
                    item.text
                )

    return {
        "content": texts
    }


async def main():

    server_params = (
        StdioServerParameters(
            command=sys.executable,
            args=[
                str(SERVER_FILE)
            ],
            cwd=str(PROJECT_ROOT),
        )
    )

    rows = []

    async with Client(
        server_params
    ) as client:

        for test in TEST_CASES:

            print(
                f"Running: {test['name']}"
            )

            started = (
                time.perf_counter()
            )

            try:

                result = (
                    await client.call_tool(
                        test["tool"],
                        test["arguments"],
                    )
                )

                elapsed_ms = (
                    time.perf_counter()
                    - started
                ) * 1000

                result_data = (
                    extract_result(
                        result
                    )
                )

                rows.append(
                    {
                        "test_id": (
                            test["id"]
                        ),
                        "test_name": (
                            test["name"]
                        ),
                        "tool": (
                            test["tool"]
                        ),
                        "status": "executed",
                        "mcp_is_error": (
                            getattr(
                                result,
                                "is_error",
                                False,
                            )
                        ),
                        "latency_ms": round(
                            elapsed_ms,
                            3,
                        ),
                        "arguments": (
                            json.dumps(
                                test[
                                    "arguments"
                                ],
                                ensure_ascii=False,
                            )
                        ),
                        "result": (
                            json.dumps(
                                result_data,
                                ensure_ascii=False,
                                default=str,
                            )
                        ),
                    }
                )

            except Exception as exc:

                elapsed_ms = (
                    time.perf_counter()
                    - started
                ) * 1000

                rows.append(
                    {
                        "test_id": (
                            test["id"]
                        ),
                        "test_name": (
                            test["name"]
                        ),
                        "tool": (
                            test["tool"]
                        ),
                        "status": "exception",
                        "mcp_is_error": True,
                        "latency_ms": round(
                            elapsed_ms,
                            3,
                        ),
                        "arguments": (
                            json.dumps(
                                test[
                                    "arguments"
                                ],
                                ensure_ascii=False,
                            )
                        ),
                        "result": (
                            f"{type(exc).__name__}: "
                            f"{exc}"
                        ),
                    }
                )

    with RESULTS_FILE.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "test_id",
                "test_name",
                "tool",
                "status",
                "mcp_is_error",
                "latency_ms",
                "arguments",
                "result",
            ],
        )

        writer.writeheader()
        writer.writerows(
            rows
        )

    print()
    print(
        "=" * 70
    )

    print(
        "EVALUATION COMPLETED"
    )

    print(
        f"Results: {RESULTS_FILE}"
    )

    print(
        f"Total tests: {len(rows)}"
    )

    print(
        "=" * 70
    )


if __name__ == "__main__":
    asyncio.run(
        main()
    )