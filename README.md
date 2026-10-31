<p align="center"><img src="assets/celious-logo.png" width="220" alt="Celious logo"></p>

# Your knowledge. Your control. Your choice of AI.

Celious is a local digital second brain that connects your knowledge, documents and projects to AI assistants, transforming information into useful context and practical actions.

Your knowledge base is stored locally in portable formats, rather than being locked into a particular AI provider's memory system.

**[Explore Celious in English](https://ezequiel-gb.github.io/Celious/?lang=en)** · **[Explorar en español](https://ezequiel-gb.github.io/Celious/?lang=es)** · **[Windows downloads](https://github.com/ezequiel-gb/Celious/releases)**

## Put your information to work

- **Continue a project with context.** Preserve decisions, requirements, source references and progress in project memory that can be retrieved in another conversation.
- **Work with your documents.** Find, read, create and organise authorised files. Extract information from supported PDFs and Word documents.
- **Use your spreadsheets.** Inspect workbooks, read ranges, update cells and convert supported tabular formats. Excel is not required for these operations.
- **Keep changes recoverable.** Review knowledge updates, keep operation records and use overwrite backups or recoverable deletion where supported.
- **Stay in control of the connection.** Celious Switch is a Windows tray application included with the software. Turn the connection on when needed and off when finished.

For example: ask a compatible assistant to find a project brief, inspect the related spreadsheet and prepare an updated local summary. Celious supplies the authorised tools and durable context; the assistant coordinates the request.

## Local knowledge, connected by choice

Through the Model Context Protocol (MCP), compatible AI assistants can access relevant information and perform authorised operations. Information shared with an AI assistant may be processed by its provider, but your original knowledge base remains on your computer.

Celious currently integrates with ChatGPT and is designed to support other compatible AI clients, subject to integration testing. Access from a phone uses the connected assistant; the Windows computer and Celious connection must remain online.

Project memory uses portable Markdown and JSON alongside ordinary documents. Continuity depends on the assistant invoking the appropriate context tools; Celious does not silently read every conversation or guarantee automatic invocation by an AI provider.

## Explore the architecture

The **[interactive architecture explorer](https://ezequiel-gb.github.io/Celious/)** explains the connection from GPT and MCP to local files, spreadsheets, project memory, permissions and recovery.

Select components, orbit, zoom and pan through the 3D-style scene, or choose the accessible 2D view. Guided workflows explain practical uses. English and Spanish are available throughout the explorer.

Celious is primarily a backend system. The explorer explains its architecture; it does not connect to your account or expose local files.

## Install on Windows

Use the installation distribution from **[Releases](https://github.com/ezequiel-gb/Celious/releases)** and follow **[the installation guide](INSTALLATION.md)**. The package includes Celious Switch, the local service, a dedicated Python runtime and pinned dependencies. A separate Python installation, Microsoft Office and Seelen UI are not required.

Supply your own authorised folders and supported ChatGPT tunnel connection. No account credentials or personal configuration are included. The AI provider's account, client and tunnel availability requirements apply.

The public repository contains the product presentation, explorer and user documentation. Application implementation and build tooling are maintained separately.

## Scope and practical limits

Access is limited to configured roots. Approval policy is selected during setup; recoverable deletion, conflict checks, format limits and access boundaries still apply. A direct policy lets a trusted client request supported changes within those roots without an additional local approval prompt.

Document conversion is format-specific. Spreadsheet tools do not run macros or provide Excel's calculation engine. Workflow execution supports the operations exposed by Celious; external research or coding tools remain capabilities of the connected assistant.

## Rights

Copyright © 2026. All rights reserved. The rights holder retains all rights, subject to applicable law and third-party licences. See [LICENSE](LICENSE) and the notices accompanying each distribution.
