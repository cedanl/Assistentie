# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "anthropic",
#     "pydantic",
# ]
# ///

# -----------------------------------------------------------------------------
# Organization: CEDA
# Original Authors: Ed. de Feber, Edwin Lieftink
# -----------------------------------------------------------------------------

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Any

from anthropic import Anthropic  # type: ignore
from pydantic import BaseModel  # type: ignore

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    handlers=[logging.FileHandler("agent.log")],
)

# Suppress verbose HTTP logs
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)


class Tool(BaseModel):
    name: str
    description: str
    input_schema: dict[str, Any]


MODEL = "claude-sonnet-4-5-20250929"
MAX_AGENT_ITERATIONS = 25


class AIAgent:
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.messages: list[dict[str, Any]] = []
        self.tools: list[Tool] = []
        # Beperk tools tot het huidige werk-directory om path-traversal te voorkomen.
        # Een door het model voorgesteld pad wordt resolved binnen deze root.
        self.workspace = Path.cwd().resolve()
        self._setup_tools()

    def _safe_path(self, user_path: str) -> Path:
        """Resolveer een door het model aangegeven pad binnen self.workspace.

        Voorkomt dat het model bestanden buiten de werkmap leest of schrijft via
        absolute paden (/etc/passwd) of '..'-traversal.
        """
        candidate = (self.workspace / user_path).resolve()
        if not candidate.is_relative_to(self.workspace):
            raise PermissionError(f"Pad buiten workspace ({self.workspace}): {user_path}")
        return candidate

    def _setup_tools(self):
        self.tools = [
            Tool(
                name="read_file",
                description="Read the contents of a file at the specified path",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "The path to the file to read",
                        }
                    },
                    "required": ["path"],
                },
            ),
            Tool(
                name="list_files",
                description="List all files and directories in the specified path",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "The directory path to list (defaults to current directory)",
                        }
                    },
                    "required": [],
                },
            ),
            Tool(
                name="edit_file",
                description="Edit a file by replacing old_text with new_text. Creates the file if it doesn't exist.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "The path to the file to edit",
                        },
                        "old_text": {
                            "type": "string",
                            "description": "The text to search for and replace (leave empty to create new file)",
                        },
                        "new_text": {
                            "type": "string",
                            "description": "The text to replace old_text with",
                        },
                    },
                    "required": ["path", "new_text"],
                },
            ),
        ]

    def _execute_tool(self, tool_name: str, tool_input: dict[str, Any]) -> str:
        logging.info(f"Executing tool: {tool_name} with input: {tool_input}")
        try:
            if tool_name == "read_file":
                return self._read_file(tool_input["path"])
            elif tool_name == "list_files":
                return self._list_files(tool_input.get("path", "."))
            elif tool_name == "edit_file":
                return self._edit_file(
                    tool_input["path"],
                    tool_input.get("old_text", ""),
                    tool_input["new_text"],
                )
            else:
                return f"Unknown tool: {tool_name}"
        except Exception as e:
            logging.error(f"Error executing {tool_name}: {str(e)}")
            return f"Error executing {tool_name}: {str(e)}"

    def _read_file(self, path: str) -> str:
        try:
            p = self._safe_path(path)
            content = p.read_text(encoding="utf-8")
            return f"File contents of {path}:\n{content}"
        except PermissionError as e:
            return f"Access denied: {e}"
        except FileNotFoundError:
            return f"File not found: {path}"
        except OSError as e:
            return f"Error reading file: {e}"

    def _list_files(self, path: str) -> str:
        try:
            p = self._safe_path(path)
            if not p.exists():
                return f"Path not found: {path}"

            items = []
            for entry in sorted(p.iterdir(), key=lambda x: x.name):
                marker = "[DIR] " if entry.is_dir() else "[FILE]"
                suffix = "/" if entry.is_dir() else ""
                items.append(f"{marker} {entry.name}{suffix}")

            if not items:
                return f"Empty directory: {path}"

            return f"Contents of {path}:\n" + "\n".join(items)
        except PermissionError as e:
            return f"Access denied: {e}"
        except OSError as e:
            return f"Error listing files: {e}"

    def _edit_file(self, path: str, old_text: str, new_text: str) -> str:
        try:
            p = self._safe_path(path)
            if p.exists() and old_text:
                content = p.read_text(encoding="utf-8")
                if old_text not in content:
                    return f"Text not found in file: {old_text}"
                p.write_text(content.replace(old_text, new_text), encoding="utf-8")
                return f"Successfully edited {path}"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(new_text, encoding="utf-8")
            return f"Successfully created {path}"
        except PermissionError as e:
            return f"Access denied: {e}"
        except OSError as e:
            return f"Error editing file: {e}"

    def chat(self, user_input: str) -> str:
        logging.info(f"User input: {user_input}")
        self.messages.append({"role": "user", "content": user_input})

        tool_schemas = [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema,
            }
            for tool in self.tools
        ]

        for _ in range(MAX_AGENT_ITERATIONS):
            try:
                response = self.client.messages.create(
                    model=MODEL,
                    max_tokens=4096,
                    system="You are a helpful coding assistant operating in a terminal environment. Output only plain text without markdown formatting, as your responses appear directly in the terminal. Be concise but thorough, providing clear and practical advice with a friendly tone. Don't use any asterisk characters in your responses.",
                    messages=self.messages,
                    tools=tool_schemas,
                )
            except Exception as e:
                return f"Error: {str(e)}"

            assistant_message = {"role": "assistant", "content": []}
            for content in response.content:
                if content.type == "text":
                    assistant_message["content"].append({"type": "text", "text": content.text})
                elif content.type == "tool_use":
                    assistant_message["content"].append(
                        {
                            "type": "tool_use",
                            "id": content.id,
                            "name": content.name,
                            "input": content.input,
                        }
                    )
            self.messages.append(assistant_message)

            tool_results = []
            for content in response.content:
                if content.type == "tool_use":
                    result = self._execute_tool(content.name, content.input)
                    logging.info(f"Tool result: {result[:500]}...")
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": content.id,
                            "content": result,
                        }
                    )

            if not tool_results:
                # Geen tool-call meer: pak alle text-blocks van het assistant antwoord.
                return "".join(b.text for b in response.content if b.type == "text")
            self.messages.append({"role": "user", "content": tool_results})

        return f"[Agent stopte na {MAX_AGENT_ITERATIONS} iteraties zonder eindantwoord.]"


def main():
    parser = argparse.ArgumentParser(
        description="AI Code Assistant - A conversational AI agent with file editing capabilities"
    )
    parser.add_argument("--api-key", help="Anthropic API key (or set ANTHROPIC_API_KEY env var)")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: Please provide an API key via --api-key or ANTHROPIC_API_KEY environment variable")
        sys.exit(1)

    agent = AIAgent(api_key)

    print("AI Code Assistant")
    print("================")
    print("A conversational AI agent that can read, list, and edit files.")
    print("Type 'exit' or 'quit' to end the conversation.")
    print()

    while True:
        try:
            user_input = input("You: ").strip()

            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break

            if not user_input:
                continue

            print("\nAssistant: ", end="", flush=True)
            response = agent.chat(user_input)
            print(response)
            print()

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            print()


if __name__ == "__main__":
    main()
