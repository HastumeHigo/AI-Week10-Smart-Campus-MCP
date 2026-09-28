from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters


PROJECT_ROOT = Path(__file__).resolve().parent

SERVER_FILE = (
    PROJECT_ROOT
    / "src"
    / "server"
    / "smart_campus_server.py"
)


def print_title(title: str) -> None:
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def print_result(result) -> None:
    if getattr(result, "structured_content", None) is not None:
        print(
            json.dumps(
                result.structured_content,
                ensure_ascii=False,
                indent=2,
                default=str,
            )
        )
        return

    content = getattr(
        result,
        "content",
        None,
    )

    if content is None:
        print(result)
        return

    for item in content:
        if hasattr(item, "text"):
            print(item.text)
        else:
            print(item)


async def main() -> None:

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[
            str(SERVER_FILE)
        ],
        cwd=str(PROJECT_ROOT),
    )

    async with Client(
        server_params
    ) as client:

        while True:

            print_title(
                "SMART CAMPUS MCP APPLICATION"
            )

            print(
                "1. Health Check"
            )

            print(
                "2. Search Room"
            )

            print(
                "3. Get Device Status"
            )

            print(
                "4. Find Available Room"
            )

            print(
                "5. List MCP Tools"
            )

            print(
                "6. List MCP Resources"
            )

            print(
                "7. Exit"
            )

            choice = input(
                "\nChoose an option: "
            ).strip()

            # =================================================
            # OPTION 1
            # =================================================

            if choice == "1":

                result = await client.call_tool(
                    "health_check",
                    {},
                )

                print_result(
                    result
                )

            # =================================================
            # OPTION 2
            # =================================================

            elif choice == "2":

                room_id = input(
                    "Room ID: "
                ).strip()

                result = await client.call_tool(
                    "search_room",
                    {
                        "room_id": room_id
                    },
                )

                print_result(
                    result
                )

            # =================================================
            # OPTION 3
            # =================================================

            elif choice == "3":

                room_id = input(
                    "Room ID: "
                ).strip()

                result = await client.call_tool(
                    "get_device_status",
                    {
                        "room_id": room_id
                    },
                )

                print_result(
                    result
                )

            # =================================================
            # OPTION 4
            # =================================================

            elif choice == "4":

                try:

                    capacity = int(
                        input(
                            "Minimum capacity: "
                        )
                    )

                except ValueError:

                    print(
                        "Capacity must be an integer."
                    )

                    input(
                        "\nPress Enter to continue..."
                    )

                    continue

                building = input(
                    "Building "
                    "(leave blank for any): "
                ).strip()

                projector_input = input(
                    "Require working projector? "
                    "(y/n): "
                ).strip().lower()

                require_projector = (
                    projector_input == "y"
                )

                arguments = {
                    "capacity": capacity,
                    "building": (
                        building
                        if building
                        else None
                    ),
                    "require_projector": (
                        require_projector
                    ),
                }

                result = await client.call_tool(
                    "find_available_room",
                    arguments,
                )

                print_result(
                    result
                )

            # =================================================
            # OPTION 5
            # =================================================

            elif choice == "5":

                tools_result = (
                    await client.list_tools()
                )

                print_title(
                    "AVAILABLE MCP TOOLS"
                )

                for tool in (
                    tools_result.tools
                ):

                    print(
                        f"- {tool.name}"
                    )

                    if tool.description:
                        print(
                            f"  {tool.description}"
                        )

            # =================================================
            # OPTION 6
            # =================================================

            elif choice == "6":

                resources_result = (
                    await client.list_resources()
                )

                print_title(
                    "AVAILABLE MCP RESOURCES"
                )

                for resource in (
                    resources_result.resources
                ):
                    print(
                        f"- {resource.uri}"
                    )

            # =================================================
            # OPTION 7
            # =================================================

            elif choice == "7":

                print(
                    "\nExiting Smart Campus MCP Application."
                )

                break

            else:

                print(
                    "Invalid option."
                )

            input(
                "\nPress Enter to continue..."
            )


if __name__ == "__main__":
    asyncio.run(
        main()
    )