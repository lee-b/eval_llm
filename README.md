# eval-llm

An LLM evaluation tool for running datasets against language models and generating human-readable reports.

## Description

`eval-llm` is a Python tool designed to automate the evaluation of language models (LLMs) using custom datasets. It sends prompts to a test LLM, collects the responses, and then evaluates those responses using an evaluation LLM based on specified criteria. The results are compiled into a human-readable HTML report.

## Features

- **Multiple Datasets:** Supports processing multiple datasets specified in JSONL format.
- **Custom Evaluation Criteria:** Allows specifying evaluation criteria per dataset or globally.
- **JSON Schema Enforcement:** Utilizes JSON schema constraints to ensure valid output from the evaluation LLM.
- **HTML Reporting:** Generates an HTML report summarizing the evaluations.
- **Configurable:** Easily configurable via a YAML configuration file.
- **Poetry Integration:** Simple installation and execution using Poetry.

## Installation

### Prerequisites

- **Python 3.7+**
- **Poetry** for dependency management and packaging.

#### Installing Poetry

If you don't have Poetry installed, you can install it using the following command:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Alternatively, refer to the [official Poetry installation guide](https://python-poetry.org/docs/#installation) for more options.

### Clone the Repository

```bash
git clone https://github.com/lee-b/eval-llm.git
cd eval-llm
```

### Install Dependencies

Install the dependencies using Poetry:

```bash
poetry install
```

## Usage

### Starting the LLM Servers

Ensure that you have both the test LLM and evaluation LLM servers running and accessible at the URLs specified in your configuration file.

#### Test LLM Server

This is the LLM being tested.

Start your test LLM server (adjust the command according to your setup):

```bash
./llama.cpp --server --host 0.0.0.0 --port 8000 your_test_llm.gguf
```

#### Evaluation LLM Server

This is the LLM that will do the evaluation of the test LLM.

Start your evaluation LLM server with support for JSON schema constraints:

```bash
./llama.cpp --server --host 0.0.0.0 --port 8001 --endpoint your_evaluation_llm.gguf
```

**Note:** Ensure your `llama.cpp` version supports the `response_format` parameter with JSON schemas.

### Prepare Your Configuration and Dataset Files

Create a YAML configuration file (e.g., `config.yaml`) in your working directory:

```yaml
TEST_LLM_BASE_URL: "http://localhost:8000/test_llm"
EVALUATION_LLM_BASE_URL: "http://localhost:8001/evaluation_llm"

datasets:
  - name: "General Knowledge Questions"
    file: "general_knowledge.jsonl"
    criteria:
      - "Correctness"
      - "Relevance"
      - "Clarity"
  - name: "Math Problems"
    file: "math_problems.jsonl"
    criteria:
      - "Accuracy"
      - "Clarity"

global_criteria:
  - "Correctness"
  - "Relevance"
```

Prepare your datasets in JSONL format (e.g., `general_knowledge.jsonl`):

```json
{"id": 1, "question": "What is the tallest mountain in the world?"}
{"id": 2, "question": "Who painted the Mona Lisa?"}
{"id": 3, "question": "What is the chemical symbol for water?"}
```

### Running the Evaluation

Run the `eval-llm` command using Poetry:

```bash
poetry run eval-llm config.yaml -o report.html
```

- Replace `config.yaml` with the path to your configuration file.
- The `-o` or `--output` option specifies the output HTML file. If not provided, it defaults to `report.html`.

### Viewing the Report

Open `report.html` in a web browser to view the evaluation results.

## Configuration File (`config.yaml`)

The configuration file is a YAML file that specifies:

- **Test LLM Base URL:** The endpoint for the test LLM.
- **Evaluation LLM Base URL:** The endpoint for the evaluation LLM.
- **Datasets:** A list of datasets to process.
  - **name:** A descriptive name for the dataset.
  - **file:** Path to the JSONL file containing the dataset.
  - **criteria:** (Optional) List of evaluation criteria specific to the dataset.
- **Global Criteria:** (Optional) Criteria to use if not specified per dataset.

### Example

```yaml
TEST_LLM_BASE_URL: "http://localhost:8000/test_llm"
EVALUATION_LLM_BASE_URL: "http://localhost:8000/evaluation_llm"

datasets:
  - name: "General Knowledge Questions"
    file: "general_knowledge.jsonl"
    criteria:
      - "Correctness"
      - "Relevance"
      - "Clarity"

global_criteria:
  - "Correctness"
  - "Relevance"
```

## Dataset Format

Datasets are provided as JSONL (JSON Lines) files, where each line is a JSON object representing a question.

### Example (`general_knowledge.jsonl`)

```json
{"id": 1, "question": "What is the tallest mountain in the world?"}
{"id": 2, "question": "Who painted the Mona Lisa?"}
{"id": 3, "question": "What is the chemical symbol for water?"}
```

- **Fields:**
  - `id`: (Optional) Identifier for the question.
  - `question`: The question prompt.

## Dependencies

The project depends on the following Python packages:

- `requests` - For making HTTP requests to the LLM servers.
- `PyYAML` - For parsing the YAML configuration file.
- `jinja2` - For generating the HTML report from templates.

These dependencies are managed by Poetry and will be installed when you run `poetry install`.

## Project Structure

```
eval-llm/
├── pyproject.toml
├── README.md
├── src/
│   └── eval_llm/
│       ├── __init__.py
│       └── __main__.py
```

- **`pyproject.toml`**: Configuration file for Poetry.
- **`README.md`**: This file.
- **`src/eval_llm/__main__.py`**: The main script containing the `main()` function.
- **`src/eval_llm/__init__.py`**: An empty file to make `eval_llm` a Python package.

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.

## Author

[Lee Braiden](lee.braiden@pm.me)

## Acknowledgments

- Inspired by the need to evaluate local LLMs efficiently.
- Utilizes `llama.cpp` for running language models locally.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

## Issues

If you encounter any problems or have suggestions, please open an issue on GitHub.
