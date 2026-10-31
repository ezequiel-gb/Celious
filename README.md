<p align="center"><img src="assets/celious-logo.png" width="220" alt="Celious logo"></p>

# Celious | Your Local Digital Second Brain

Celious is a local digital second brain I developed to connect AI assistants with documents, spreadsheets and persistent project knowledge.

It demonstrates how information can be organised, retrieved and used across conversations, turning existing knowledge into practical actions. Its architecture combines local information management, persistent memory, controlled file operations and AI integration through the Model Context Protocol (MCP).

## What Celious demonstrates

- **Local knowledge:** original documents and project information are kept in ordinary local folders.
- **Project memory:** decisions, requirements, findings, source references and progress can carry across conversations.
- **Documents and spreadsheets:** connected tools can find and process supported files within authorised folders.
- **Workflows and recovery:** multi-step work records progress and supports reviewed recovery of supported file changes.
- **AI integration:** ChatGPT communicates with the local service through MCP tools.

## Architecture explorer

Explore the interactive, bilingual architecture:

- [Explore Celious in English](https://ezequiel-gb.github.io/Celious/?lang=en)
- [Explorar Celious en español](https://ezequiel-gb.github.io/Celious/?lang=es)

The explorer presents the 3D component view, accessible 2D view and guided workflows. It runs independently of a Celious service.

## Local knowledge and AI

Celious keeps the original knowledge base on the user's computer in portable formats. Through MCP, a compatible assistant can retrieve information and request operations within the configured access boundaries. Information returned to an assistant may be processed by its provider; the local originals remain stored on the computer.

Celious currently integrates with ChatGPT. Its MCP architecture can support additional compatible clients, subject to integration work and testing.

## What this means in practice

An assistant can find a project document, check a related spreadsheet and prepare an update to an authorised file. You can review that change and save an important decision to project memory for a later conversation.

## Commercial context

Celious is a working system and an example of the digital systems I design and develop. Similar solutions can be adapted to an organisation's specific requirements, processes and operational challenges.

[Let's talk](https://ezequielgomez.net/index-en.html#contacto) · [Hablemos](https://ezequielgomez.net/index-es.html#contacto)

The public repository contains the project presentation and interactive explorer. The application implementation remains private and is not publicly distributed as a free product.

[Project overview](PROJECT-OVERVIEW.md) · [License](LICENSE)
