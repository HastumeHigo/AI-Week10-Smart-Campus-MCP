from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters


# ============================================================
# 1. PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SERVER_FILE = (
    PROJECT_ROOT
    / "src"
    / "server"
    / "smart_campus_server.py"
)


# ============================================================
# 2. PRINT HELPERS
# ============================================================

def print_title(title: str) -> None:
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def print_json(data) -> None:
    print(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2,
            default=str,
        )
    )


def print_tool_result(result) -> None:
    """
    Print MCP tool result safely.
    """

    if getattr(result, "structured_content", None) is not None:
        print_json(
            result.structured_content
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

    for block in content:
        if hasattr(block, "text"):
            print(block.text)
        else:
            print(block)


# ============================================================
# 3. MAIN MCP CLIENT
# ============================================================

async def main() -> None:

    # --------------------------------------------------------
    # Create stdio server configuration
    # --------------------------------------------------------

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[
            str(SERVER_FILE)
        ],
        cwd=str(PROJECT_ROOT),
    )

    print_title(
        "SMART CAMPUS MCP CLIENT"
    )

    print(
        "Server file:",
        SERVER_FILE,
    )

    print(
        "Python executable:",
        sys.executable,
    )

    print(
        "\nConnecting to MCP Server..."
    )

    # --------------------------------------------------------
    # MCP v2 Client
    # Entering async with automatically connects.
    # --------------------------------------------------------

    async with Client(
        server_params
    ) as client:

        print(
            "CONNECTED TO MCP SERVER"
        )

        # ====================================================
        # 4. CONNECTION INFORMATION
        # ====================================================

        print_title(
            "1. CONNECTION / CAPABILITY NEGOTIATION"
        )

        print(
            "Protocol version:"
        )
        print(
            client.protocol_version
        )

        print(
            "\nServer info:"
        )
        print(
            client.server_info
        )

        print(
            "\nServer capabilities:"
        )
        print(
            client.server_capabilities
        )

        print(
            "\nServer instructions:"
        )
        print(
            client.instructions
        )

        # ====================================================
        # 5. LIST TOOLS
        # ====================================================

        print_title(
            "2. LIST MCP TOOLS"
        )

        tools_result = (
            await client.list_tools()
        )

        for tool in tools_result.tools:

            print()
            print(
                f"Tool name: {tool.name}"
            )

            print(
                f"Description: {tool.description}"
            )

            print(
                "Input schema:"
            )

            print_json(
                tool.input_schema
            )

        # ====================================================
        # 6. LIST RESOURCES
        # ====================================================

        print_title(
            "3. LIST MCP RESOURCES"
        )

        resources_result = (
            await client.list_resources()
        )

        for resource in (
            resources_result.resources
        ):
            print(
                f"- {resource.uri}"
            )

        # ====================================================
        # 7. LIST PROMPTS
        # ====================================================

        print_title(
            "4. LIST MCP PROMPTS"
        )

        prompts_result = (
            await client.list_prompts()
        )

        for prompt in (
            prompts_result.prompts
        ):
            print(
                f"- {prompt.name}"
            )

        # ====================================================
        # 8. READ RESOURCE
        # ====================================================

        print_title(
            "5. READ RESOURCE: campus://rooms"
        )

        room_resource = (
            await client.read_resource(
                "campus://rooms"
            )
        )

        for item in (
            room_resource.contents
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

        # ====================================================
        # 9. HEALTH CHECK
        # ====================================================

        print_title(
            "6. CALL TOOL: health_check"
        )

        result = (
            await client.call_tool(
                "health_check",
                {},
            )
        )

        print_tool_result(
            result
        )

        # ====================================================
        # 10. SEARCH ROOM
        # ====================================================

        print_title(
            "7. CALL TOOL: search_room"
        )

        result = (
            await client.call_tool(
                "search_room",
                {
                    "room_id": "A203"
                },
            )
        )

        print_tool_result(
            result
        )

        # ====================================================
        # 11. DEVICE STATUS
        # ====================================================

        print_title(
            "8. CALL TOOL: get_device_status"
        )

        result = (
            await client.call_tool(
                "get_device_status",
                {
                    "room_id": "A203"
                },
            )
        )

        print_tool_result(
            result
        )

        # ====================================================
        # 12. FIND AVAILABLE ROOM
        # ====================================================

        print_title(
            "9. CALL TOOL: find_available_room"
        )

        result = (
            await client.call_tool(
                "find_available_room",
                {
                    "capacity": 40,
                    "building": "A",
                    "require_projector": True,
                },
            )
        )

        print_tool_result(
            result
        )

        # ====================================================
        # 13. GET PROMPT
        # ====================================================

        print_title(
            "10. GET MCP PROMPT"
        )

        prompt_result = (
            await client.get_prompt(
                "smart_campus_assistant",
                {
                    "question": (
                        "Tìm phòng cho 40 sinh viên "
                        "và cần máy chiếu."
                    )
                },
            )
        )

        for message in (
            prompt_result.messages
        ):

            print(
                message
            )

    # ========================================================
    # 14. COMPLETED
    # ========================================================

    print_title(
        "SMART CAMPUS MCP CLIENT COMPLETED"
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    asyncio.run(
        main()
    )