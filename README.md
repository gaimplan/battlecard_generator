## Overview
Battlecard Generator is a Python-based tool designed to generate comprehensive battlecards for competitive analysis. It aggregates insights from multiple scripts to provide strategic overviews, actionable plans, and competitive assessments.

## Setup
1. Clone the repository to your local machine.
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   ```
3. Activate the virtual environment:
   - On macOS/Linux: `source venv/bin/activate`
   - On Windows: `venv\Scripts\activate`
4. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Configure the product settings in `run.py` by defining the following variables:
    ```python
    # Product configuration
    PRODUCT_NAME = "ENTER THE PRODUCT NAME"
    COMPETITOR1 = "ENTER THE COMPETITOR1 NAME"
    COMPETITOR2 = "ENTER THE COMPETITOR2 NAME"
    ```
6. Run the application using:
   ```bash
   python run.py
   ```

## Application Flow
1. The application is initiated via `run.py`.
2. `run.py` orchestrates the execution of various scripts in the `scripts` directory, which perform specialized tasks including:
   - `combine_json.py`: Combines multiple JSON sources.
   - `json_to_markdown.py`: Converts JSON data to Markdown format.
   - `rag-actionplan.py`: Generates the actionable plan section.
   - `rag-competitive.py`: Produces competitive analysis.
   - `rag-objection.py`: Handles potential objections.
   - `rag-qualifying.py`: Provides qualifying data.
   - `rag-strategicoverview.py`: Generates a strategic overview.
   - `rag-usecases.py`: Describes use cases.
   - `rag-valueprop.py`: Details the value proposition.
   - `search-benefits.py`: Searches for benefits data.
   - `search-competitor1.py`: Searches competitor 1 data.
   - `search-competitor2.py`: Searches competitor 2 data.
3. Output from these scripts is consolidated into `output/battlecard.md`.

## Tech Stack
- **Python 3.x**: Main programming language for the project.
- **Virtual Environment**: Managed with `venv` for isolated dependency management.
- **Standard Libraries**: Utilizes Python's built-in libraries such as `os`, `sys`, etc.
- **Dependencies**:
    - `python-dotenv`: Manages environment variables.
    - `langchain-google-genai`: Integrates Google GenAI for LangChain-based workflows.
    - `langchain`: Framework for building language model applications.
    - `langchain_community`: Provides community-driven modules and utilities for LangChain.
    - `tavily-python`: internet research API extended functionalities.


## File Structure
```
README.md              # Project overview and documentation
clean.py               # Script for cleaning operations
logs                   # Directory containing log files
output                 # Directory where the final battlecard markdown file is saved
requirements.txt       # List of dependencies
run.py                 # Main application entry point
scripts                # Collection of scripts for generating battlecard sections
├── combine_json.py    # Combines multiple JSON sources
├── json_to_markdown.py # Converts JSON to Markdown
├── rag-actionplan.py  # Generates the action plan section
├── rag-competitive.py # Produces competitive analysis
├── rag-objection.py    # Handles objections section
├── rag-qualifying.py   # Provides qualifying data
├── rag-strategicoverview.py # Generates strategic overview
├── rag-usecases.py    # Describes use cases
├── rag-valueprop.py   # Details the value proposition
├── search-benefits.py # Searches for benefits data
├── search-competitor1.py # Searches competitor 1 data
└── search-competitor2.py # Searches competitor 2 data
temp_files             # Temporary files storage
