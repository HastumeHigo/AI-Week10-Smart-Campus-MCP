from __future__ import annotations

import asyncio
import sys
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


async def main() -> None:

    server_params = (
        StdioServerParameters(
            command=sys.executable,
            args=[
                str(SERVER_FILE)
            ],
            cwd=str(PROJECT_ROOT),
        )
    )

    tests = [
        {
            "name": "Health Check",
            "tool": "health_check",
            "arguments": {},
        },
        {
            "name": "Search Existing Room",
            "tool": "search_room",
            "arguments": {
                "room_id": "A203"
            },
        },
        {
            "name": "Search Unknown Room",
            "tool": "search_room",
            "arguments": {
                "room_id": "XYZ999"
            },
        },
        {
            "name": "Device Status",
            "tool": "get_device_status",
            "arguments": {
                "room_id": "A203"
            },
        },
        {
            "name": "Find Valid Room",
            "tool": "find_available_room",
            "arguments": {
                "capacity": 40,
                "building": "A",
                "require_projector": True,
            },
        },
        {
            "name": "Impossible Capacity",
            "tool": "find_available_room",
            "arguments": {
                "capacity": 500,
                "building": "A",
                "require_projector": True,
            },
        },
    ]

    print(
        "=" * 70
    )

    print(
        "SMART CAMPUS MCP TEST"
    )

    print(
        "=" * 70
    )

    async with Client(
        server_params
    ) as client:

        print(
            "\nCONNECTED"
        )

        print(
            "Protocol:",
            client.protocol_version,
        )

        completed = 0

        for test in tests:

            print()
            print(
                "-" * 70
            )

            print(
                "TEST:",
                test["name"],
            )

            print(
                "Tool:",
                test["tool"],
            )

            print(
                "Arguments:",
                test["arguments"],
            )

            try:

                result = (
                    await client.call_tool(
                        test["tool"],
                        test[
                            "arguments"
                        ],
                    )
                )

                print(
                    "is_error:",
                    result.is_error,
                )

                if (
                    result.structured_content
                    is not None
                ):
                    print(
                        "Result:",
                        result.structured_content,
                    )

                else:

                    for item in (
                        result.content
                    ):

                        if hasattr(
                            item,
                            "text",
                        ):
                            print(
                                item.text
                            )

                        else:
                            print(
                                item
                            )

                completed += 1

            except Exception as exc:

                print(
                    "Exception:",
                    type(exc).__name__,
                )

                print(
                    str(exc)
                )

    print()
    print(
        "=" * 70
    )

    print(
        f"TESTS EXECUTED: "
        f"{completed}/{len(tests)}"
    )

    print(
        "=" * 70
    )


if __name__ == "__main__":
    asyncio.run(
        main()
    )