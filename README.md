# Didactic AI-Powered IT Ticket Triage Workflow

This project serves as a demonstration of a simple, AI-powered workflow for triaging IT tickets. It is intended for educational purposes to showcase the integration of local and cloud-based AI models, such as Ollama and the Google Gemini API, in a practical application. Please note that this is not a production-ready system.

> **Note on Code Comments:** The Python scripts in this project are commented more extensively than is typical for a production codebase. This is done intentionally to make the code more accessible and understandable for developers who may be less familiar with the libraries and concepts used.

## Setup

1.  **Install Dependencies:**
    Install the required Python libraries from the `pyproject.toml` file using `uv sync`:

    ```bash
    uv sync
    ```

### Development Tooling

This project uses the following tools for code quality:

-   **`ruff`** for linting.
-   **`ty`** and **`mypy`** for type checking.

It is recommended to install `ruff` as a persistent tool using `uv`, as it is a general-purpose linter that can be used across multiple projects:

```bash
uv tool install ruff
```

> **Note:** After installing, you may need to add the tool's installation directory to your system's PATH. The `uv tool install` command will provide the necessary command to run, such as `export PATH="/Users/your-user/.local/bin:$PATH"`.

The type checkers, `ty` and `mypy`, are managed as project-specific development dependencies and can be installed with:

```bash
uv sync --extra dev
```

## How to Run

### 1. Triage Tickets

To process the tickets in the `tickets-original` directory, you can use either the `ollama` or `gemini` model.

**Using Ollama:**

```bash
python triage.py --model ollama
```

**Using Gemini:**

```bash
python triage.py --model gemini
```

You can also run the script without the `--model` argument, and it will default to using `ollama`.

### 2. Clean the Triaged Directory

To remove all the triaged tickets and reset the demo, run the following command:

```bash
python clean.py
```

### Help

To see the full documentation of the command-line options, run:

```bash
python triage.py --help
```

### Running Checks

-   **Ruff (Linting):**
    ```bash
    ruff check .
    ```

-   **Ty (Type Checking):**
    ```bash
    uv run ty check .
    ```

-   **Mypy (Type Checking):**
    ```bash
    uv run mypy .
