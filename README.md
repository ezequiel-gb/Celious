<p align="center"><img src="assets/celious-logo.png" width="220" alt="Celious logo"></p>

# Celious

Celious is a local digital second brain that connects documents, project knowledge and file operations to AI assistants through MCP.

The knowledge base is stored on your computer in Markdown, JSON and ordinary document formats.

**[Explore Celious in English](https://ezequiel-gb.github.io/Celious/?lang=en)** · **[Explorar en español](https://ezequiel-gb.github.io/Celious/?lang=es)** · **[Windows downloads](https://github.com/ezequiel-gb/Celious/releases)**

## Capabilities

- **Project memory:** preserve decisions, requirements, source references and progress for later conversations.
- **Files and documents:** find, read, create and organise files; extract information from supported PDFs and Word documents.
- **Spreadsheets:** inspect workbooks, read ranges, update cells and convert supported tabular formats without Microsoft Excel.
- **Recovery:** retain operation records, overwrite backups and recoverably deleted files.
- **Celious Switch:** start and stop the connection from the Windows tray.

For example: ask a compatible assistant to find a project brief, inspect the related spreadsheet and prepare an updated local summary. Celious supplies the authorised tools and durable context; the assistant coordinates the request.

## Local knowledge

Through the Model Context Protocol (MCP), compatible AI assistants retrieve relevant information and perform operations in configured folders. The original knowledge base remains on your computer.

Celious currently integrates with ChatGPT. MCP provides the interface for additional compatible AI clients. Access from a phone uses the connected assistant and the running Windows installation.

Project memory uses portable Markdown and JSON alongside ordinary documents. The assistant retrieves project context through Celious's tools.

## Explore the architecture

The **[interactive architecture explorer](https://ezequiel-gb.github.io/Celious/)** explains the connection from GPT and MCP to local files, spreadsheets, project memory, permissions and recovery.

Select components, orbit, zoom and pan through the 3D-style scene, or choose the accessible 2D view. Guided workflows explain practical uses. English and Spanish are available throughout the explorer.

Celious is primarily a backend system. The explorer explains how its components work together.

## Install on Windows

Use the installation distribution from **[Releases](https://github.com/ezequiel-gb/Celious/releases)** and follow **[the installation guide](INSTALLATION.md)**. The package includes Celious Switch, the local service, a dedicated Python runtime and pinned dependencies. A separate Python installation, Microsoft Office and Seelen UI are not required.

During setup, select your folders and configure your ChatGPT tunnel connection.

The public repository contains the product presentation, explorer and user documentation. Application implementation and build tooling are maintained separately.

[Installation and configuration](INSTALLATION.md) · [License](LICENSE)
