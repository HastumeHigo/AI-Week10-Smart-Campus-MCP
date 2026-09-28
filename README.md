# Week 10 - Smart Campus MCP Server

## 1. Overview

This project demonstrates the Model Context Protocol (MCP)
using a Smart Campus use case.

The system provides:

- MCP Server
- MCP Client
- MCP Resources
- MCP Tools
- MCP Prompt
- JSON Schema based tool inputs
- Input validation
- Logging
- Error handling
- stdio transport
- Automated evaluation

---

## 2. Project Structure

```text
ai_lab10/
├── data/
│   ├── rooms.json
│   └── devices.json
├── logs/
├── results/
│   └── mcp_test_results.csv
├── src/
│   ├── client/
│   │   └── smart_campus_client.py
│   └── server/
│       └── smart_campus_server.py
├── tests/
│   ├── test_mcp.py
│   └── evaluation.py
├── app.py
├── README.md
├── requirements.txt
└── .gitignore