# SuperClaude Framework

## Project Overview

SuperClaude is a meta-programming configuration framework that transforms Claude Code into a structured development platform. It is not a standalone application, but rather a collection of context files that enhance the capabilities of the Claude Code application.

The framework provides systematic workflow automation through a system of commands, intelligent agents, and behavioral modes. The project is a command-line tool written in Python, with a Node.js wrapper for cross-platform installation. The core logic for the installer and command-line tool is located in the `SuperClaude` and `setup` directories.

## Core Concepts

SuperClaude is a **Context-Oriented Configuration Framework**. It works by installing a set of Markdown files into the `~/.claude/` directory. These files contain behavioral instructions that Claude Code reads to modify its behavior. The framework itself does not have an execution engine; it simply provides the context for Claude Code to act upon.

The framework is composed of several types of context files:

*   **Commands:** These define workflow patterns that can be activated with a `/sc:[command]` trigger. They provide step-by-step guidance for common development tasks.
*   **Agents:** These provide domain-specific expertise. They can be activated manually with `@agent-[name]` or automatically based on the context of the conversation.
*   **Modes:** These modify Claude's interaction style. They can be activated by flags or keywords to adapt the AI's behavior to different situations.
*   **Core Files:** These set the fundamental rules and principles that guide the AI's behavior. They are always active.

## Building and Running

The project uses `setuptools` for packaging the Python application and `npm` for the Node.js wrapper.

### Installation

The recommended way to install SuperClaude is using `pipx`:

```bash
pipx install SuperClaude && pipx upgrade SuperClaude && SuperClaude install
```

Alternatively, you can use `pip` or `npm`:

```bash
# Using pip
pip install SuperClaude && pip upgrade SuperClaude && SuperClaude install

# Using npm
npm install -g @bifrost_inc/superclaude && superclaude install
```

### Running the application

Once installed, the main command is `SuperClaude`. The available operations are:

*   `SuperClaude install`: Install the framework components.
*   `SuperClaude update`: Update an existing installation.
*   `SuperClaude uninstall`: Remove the installation.
*   `SuperClaude backup`: Backup and restore operations.

### Testing

The project uses `pytest` for testing. To run the tests, you first need to install the development dependencies:

```bash
pip install -e .[dev]
```

Then, you can run the tests using `pytest`:

```bash
pytest
```

## Development Conventions

The project follows standard Python development conventions.

*   **Formatting:** The code is formatted using `black`.
*   **Type Checking:** The code is type-checked using `mypy`.
*   **Linting:** The project uses `flake8` for linting.
*   **Contributing:** Contributions are welcome. Please refer to the `CONTRIBUTING.md` file for more details.

## Extending the Framework

The SuperClaude framework is designed to be easily extensible. You can add new commands, agents, and modes by creating new Markdown files in the `~/.claude/` directory.

*   **Adding a new command:** Create a new `.md` file in the `~/.claude/commands/sc/` directory.
*   **Adding a new agent:** Create a new `.md` file in the `~/.claude/agents/` directory.
*   **Adding a new mode:** Create a new `.md` file in the `~/.claude/` directory with the prefix `MODE_`.

For more details on how to extend the framework, please refer to the [Technical Architecture Guide](Docs/Developer-Guide/technical-architecture.md).