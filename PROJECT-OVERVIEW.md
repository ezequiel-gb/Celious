# Celious project overview

Celious is a local digital second brain that connects AI assistants with documents, spreadsheets and persistent project knowledge. This overview describes the public architecture showcase; it does not expose the private application implementation.

## Practical purpose

Project knowledge often sits across documents, spreadsheets and separate conversations. Celious demonstrates a way to keep the source information in local folders while making relevant context and bounded file operations available to a connected AI assistant.

The design can support work such as finding project material, retrieving reviewed project context, inspecting a supported workbook and creating a local result. Similar digital systems can be adapted to an organisation's requirements, processes and operational challenges.

## Architecture

The interactive explorer presents these parts:

- **AI assistant and MCP:** a compatible assistant selects tools and exchanges structured requests and results with the local Celious service through the Model Context Protocol.
- **Local service and access boundaries:** the service provides filesystem, document, spreadsheet, memory and workflow tools. Operations are limited to configured folders and their access settings.
- **Files and spreadsheets:** the architecture covers supported document and tabular formats, including inspection, controlled edits and recoverable file changes.
- **Second Brain and portable storage:** project knowledge is represented in local Markdown and JSON records alongside ordinary documents. Project-scoped retrieval keeps separate collections distinct.
- **Workflows and recovery:** supported multi-step tasks track progress and outcomes; checkpoints and operation records support reviewed recovery.
- **Celious Switch:** the Windows tray client provides visible connection controls and service diagnostics.

The Windows integration currently demonstrated is ChatGPT through an MCP connection. Other compatible clients require their own integration and testing. Information shared with an assistant may be processed by that provider, while the original local knowledge base remains on the computer.

## Interactive explorer

The [English explorer](https://ezequiel-gb.github.io/Celious/?lang=en) and [explorador en español](https://ezequiel-gb.github.io/Celious/?lang=es) provide a selectable 3D-style architecture, an accessible 2D view and guided workflows. The explorer is a standalone presentation and works without a running Celious service.

## Discuss a solution

Celious is an example of the digital systems I design and develop. Similar solutions can be adapted to an organisation's specific requirements, processes and operational challenges.

- [Discuss a solution](https://ezequielgomez.net/index-en.html#contacto)
- [Hablemos de una solución](https://ezequielgomez.net/index-es.html#contacto)
