from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from mcp.server.mcpserver import MCPServer
from pydantic import BaseModel, Field, ValidationError


# ============================================================
# 1. PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
LOG_DIR = PROJECT_ROOT / "logs"

ROOMS_FILE = DATA_DIR / "rooms.json"
DEVICES_FILE = DATA_DIR / "devices.json"
LOG_FILE = LOG_DIR / "mcp_server.log"

LOG_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2. LOGGING
# ============================================================

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8",
)

logger = logging.getLogger("smart-campus-mcp")


# ============================================================
# 3. CREATE MCP SERVER
# ============================================================

mcp = MCPServer(
    "Smart Campus MCP Server"
)


# ============================================================
# 4. VALIDATION MODELS
# ============================================================

class RoomSearchInput(BaseModel):
    room_id: str = Field(
        min_length=1,
        max_length=20,
        description="Room ID, for example A203",
    )


class DeviceSearchInput(BaseModel):
    room_id: str = Field(
        min_length=1,
        max_length=20,
        description="Room ID used to search devices",
    )


class RoomAllocationInput(BaseModel):
    capacity: int = Field(
        ge=1,
        le=1000,
        description="Minimum room capacity required",
    )

    building: str | None = Field(
        default=None,
        max_length=20,
        description="Optional preferred building",
    )

    require_projector: bool = Field(
        default=False,
        description="Whether a working projector is required",
    )


# ============================================================
# 5. HELPER FUNCTIONS
# ============================================================

def normalize_room_id(room_id: str) -> str:
    """
    Normalize room ID.
    Example:
        ' a203 ' -> 'A203'
    """
    return room_id.strip().upper()


def load_json_file(path: Path) -> list[dict[str, Any]]:
    """
    Load JSON data safely.
    The JSON file must contain a list.
    """

    if not path.exists():
        logger.error("File not found: %s", path)
        raise FileNotFoundError(
            f"Data file not found: {path.name}"
        )

    try:
        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

    except json.JSONDecodeError as exc:
        logger.exception(
            "Invalid JSON file: %s",
            path,
        )

        raise ValueError(
            f"Invalid JSON format in {path.name}"
        ) from exc

    if not isinstance(data, list):
        raise ValueError(
            f"{path.name} must contain a JSON list."
        )

    return data


def get_rooms() -> list[dict[str, Any]]:
    """
    Load rooms.json.
    """
    return load_json_file(
        ROOMS_FILE
    )


def get_devices() -> list[dict[str, Any]]:
    """
    Load devices.json.
    """
    return load_json_file(
        DEVICES_FILE
    )


# ============================================================
# 6. MCP RESOURCES
# ============================================================

@mcp.resource("campus://info")
def campus_info() -> str:
    """
    Return general Smart Campus information.
    """

    logger.info(
        "Resource requested: campus://info"
    )

    return (
        "SMART CAMPUS AI SYSTEM\n"
        "\n"
        "Services:\n"
        "- Room lookup\n"
        "- Room allocation\n"
        "- Device management\n"
        "\n"
        "Data sources:\n"
        "- rooms.json\n"
        "- devices.json\n"
    )


@mcp.resource("campus://rooms")
def rooms_resource() -> str:
    """
    Return all Smart Campus rooms.
    """

    logger.info(
        "Resource requested: campus://rooms"
    )

    try:
        rooms = get_rooms()

        return json.dumps(
            rooms,
            ensure_ascii=False,
            indent=2,
        )

    except Exception as exc:
        logger.exception(
            "Failed to load rooms resource"
        )

        return json.dumps(
            {
                "success": False,
                "error": type(exc).__name__,
                "message": str(exc),
            },
            ensure_ascii=False,
            indent=2,
        )


@mcp.resource("campus://devices")
def devices_resource() -> str:
    """
    Return all Smart Campus devices.
    """

    logger.info(
        "Resource requested: campus://devices"
    )

    try:
        devices = get_devices()

        return json.dumps(
            devices,
            ensure_ascii=False,
            indent=2,
        )

    except Exception as exc:
        logger.exception(
            "Failed to load devices resource"
        )

        return json.dumps(
            {
                "success": False,
                "error": type(exc).__name__,
                "message": str(exc),
            },
            ensure_ascii=False,
            indent=2,
        )


# ============================================================
# 7. MCP TOOL - HEALTH CHECK
# ============================================================

@mcp.tool()
def health_check() -> dict[str, Any]:
    """
    Check whether the Smart Campus MCP server is running.
    """

    logger.info(
        "Tool called: health_check"
    )

    return {
        "success": True,
        "server": "Smart Campus MCP Server",
        "status": "running",
    }


# ============================================================
# 8. MCP TOOL - SEARCH ROOM
# ============================================================

@mcp.tool()
def search_room(
    room_id: str,
) -> dict[str, Any]:
    """
    Search for a room by room ID.
    Example:
        search_room("A203")
    """

    try:
        validated = RoomSearchInput(
            room_id=room_id
        )

        target_room_id = normalize_room_id(
            validated.room_id
        )

        logger.info(
            "Tool called: search_room | room_id=%s",
            target_room_id,
        )

        rooms = get_rooms()

        for room in rooms:
            current_room_id = normalize_room_id(
                str(
                    room.get(
                        "room_id",
                        "",
                    )
                )
            )

            if current_room_id == target_room_id:

                return {
                    "success": True,
                    "room": room,
                }

        return {
            "success": False,
            "error": "ROOM_NOT_FOUND",
            "message": (
                f"Room {target_room_id} "
                "does not exist."
            ),
        }

    except ValidationError as exc:

        logger.warning(
            "Validation failed in search_room: %s",
            exc,
        )

        return {
            "success": False,
            "error": "VALIDATION_ERROR",
            "message": str(exc),
        }

    except Exception as exc:

        logger.exception(
            "Unexpected search_room error"
        )

        return {
            "success": False,
            "error": type(exc).__name__,
            "message": str(exc),
        }


# ============================================================
# 9. MCP TOOL - GET DEVICE STATUS
# ============================================================

@mcp.tool()
def get_device_status(
    room_id: str,
) -> dict[str, Any]:
    """
    Return devices installed in a room.
    """

    try:
        validated = DeviceSearchInput(
            room_id=room_id
        )

        target_room_id = normalize_room_id(
            validated.room_id
        )

        logger.info(
            (
                "Tool called: "
                "get_device_status | room_id=%s"
            ),
            target_room_id,
        )

        devices = get_devices()

        matches = []

        for device in devices:

            device_room_id = normalize_room_id(
                str(
                    device.get(
                        "room_id",
                        "",
                    )
                )
            )

            if device_room_id == target_room_id:
                matches.append(
                    device
                )

        if not matches:

            return {
                "success": False,
                "error": "DEVICE_NOT_FOUND",
                "message": (
                    "No devices found for room "
                    f"{target_room_id}."
                ),
            }

        return {
            "success": True,
            "room_id": target_room_id,
            "count": len(matches),
            "devices": matches,
        }

    except ValidationError as exc:

        logger.warning(
            (
                "Validation failed in "
                "get_device_status: %s"
            ),
            exc,
        )

        return {
            "success": False,
            "error": "VALIDATION_ERROR",
            "message": str(exc),
        }

    except Exception as exc:

        logger.exception(
            "Unexpected get_device_status error"
        )

        return {
            "success": False,
            "error": type(exc).__name__,
            "message": str(exc),
        }


# ============================================================
# 10. MCP TOOL - FIND AVAILABLE ROOM
# ============================================================

@mcp.tool()
def find_available_room(
    capacity: int,
    building: str | None = None,
    require_projector: bool = False,
) -> dict[str, Any]:
    """
    Find available rooms based on:

    - minimum capacity
    - optional building
    - optional working projector
    """

    try:
        validated = RoomAllocationInput(
            capacity=capacity,
            building=building,
            require_projector=require_projector,
        )

        logger.info(
            (
                "Tool called: find_available_room | "
                "capacity=%s | "
                "building=%s | "
                "require_projector=%s"
            ),
            validated.capacity,
            validated.building,
            validated.require_projector,
        )

        rooms = get_rooms()
        devices = get_devices()

        candidates: list[
            dict[str, Any]
        ] = []

        for room in rooms:

            # ----------------------------------------------
            # Check room status
            # ----------------------------------------------

            room_status = str(
                room.get(
                    "status",
                    "",
                )
            ).strip().lower()

            if room_status != "available":
                continue

            # ----------------------------------------------
            # Check capacity
            # ----------------------------------------------

            room_capacity = int(
                room.get(
                    "capacity",
                    0,
                )
            )

            if (
                room_capacity
                < validated.capacity
            ):
                continue

            # ----------------------------------------------
            # Check building
            # ----------------------------------------------

            if validated.building:

                requested_building = (
                    validated.building
                    .strip()
                    .upper()
                )

                room_building = str(
                    room.get(
                        "building",
                        "",
                    )
                ).strip().upper()

                if (
                    room_building
                    != requested_building
                ):
                    continue

            # ----------------------------------------------
            # Check projector requirement
            # ----------------------------------------------

            if validated.require_projector:

                room_id = normalize_room_id(
                    str(
                        room.get(
                            "room_id",
                            "",
                        )
                    )
                )

                has_working_projector = False

                for device in devices:

                    device_room_id = (
                        normalize_room_id(
                            str(
                                device.get(
                                    "room_id",
                                    "",
                                )
                            )
                        )
                    )

                    device_type = str(
                        device.get(
                            "device_type",
                            "",
                        )
                    ).strip().lower()

                    device_status = str(
                        device.get(
                            "status",
                            "",
                        )
                    ).strip().lower()

                    if (
                        device_room_id
                        == room_id
                        and device_type
                        == "projector"
                        and device_status
                        == "working"
                    ):
                        has_working_projector = True
                        break

                if not has_working_projector:
                    continue

            candidates.append(
                room
            )

        # ----------------------------------------------
        # Sort: smallest suitable room first
        # ----------------------------------------------

        candidates.sort(
            key=lambda item: int(
                item.get(
                    "capacity",
                    0,
                )
            )
        )

        if not candidates:

            return {
                "success": False,
                "error": "NO_SUITABLE_ROOM",
                "message": (
                    "No available room satisfies "
                    "all requested constraints."
                ),
                "constraints": {
                    "capacity": (
                        validated.capacity
                    ),
                    "building": (
                        validated.building
                    ),
                    "require_projector": (
                        validated
                        .require_projector
                    ),
                },
            }

        return {
            "success": True,
            "count": len(candidates),
            "recommended_room": (
                candidates[0]
            ),
            "candidates": candidates,
        }

    except ValidationError as exc:

        logger.warning(
            (
                "Validation failed in "
                "find_available_room: %s"
            ),
            exc,
        )

        return {
            "success": False,
            "error": "VALIDATION_ERROR",
            "message": str(exc),
        }

    except Exception as exc:

        logger.exception(
            (
                "Unexpected "
                "find_available_room error"
            )
        )

        return {
            "success": False,
            "error": type(exc).__name__,
            "message": str(exc),
        }


# ============================================================
# 11. MCP PROMPT
# ============================================================

@mcp.prompt()
def smart_campus_assistant(
    question: str,
) -> str:
    """
    Reusable Smart Campus assistant prompt.
    """

    return (
        "You are a Smart Campus AI assistant.\n"
        "\n"
        "Rules:\n"
        "1. Use MCP resources and tools "
        "when needed.\n"
        "2. Never invent room or device "
        "information.\n"
        "3. Respect room capacity.\n"
        "4. Respect device status.\n"
        "5. If no valid room exists, "
        "say so clearly.\n"
        "6. Prefer MCP evidence over "
        "assumptions.\n"
        "\n"
        f"User question:\n{question}"
    )


# ============================================================
# 12. RUN SERVER
# ============================================================

if __name__ == "__main__":

    logger.info(
        "Starting Smart Campus MCP Server"
    )

    # Default MCP transport:
    # stdio
    mcp.run()