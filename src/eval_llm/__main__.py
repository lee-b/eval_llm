import argparse
import yaml
import json
import requests
from jinja2 import Template


def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def load_jsonl(file_path):
    with open(file_path, 'r') as f:
        return [json.loads(line) for line in f]

def call_llm(base_url, prompt):
    response = requests.post(
        base_url,
        json={'prompt': prompt}
    )
    response.raise_for_status()
    return response.json()['output']

def evaluate_output(evaluator_url, question, model_output, criteria):
    # Define the JSON schema for the evaluation output
    properties = {}
    for criterion in criteria:
        properties[criterion] = {
            "type": "object",
            "properties": {
                "score": { "type": "integer", "minimum": 1, "maximum": 10 },
                "justification": { "type": "string" }
            },
            "required": ["score", "justification"]
        }

    json_schema = {
        "type": "object",
        "properties": properties,
        "required": criteria
    }

    evaluation_prompt = f"""
You are an expert evaluator. Assess the following answer based on the criteria provided.

Question:
{question}

Model's Answer:
{model_output}

For each criterion, provide:
- A score from 1 to 10 (integer).
- A brief justification (one or two sentences).

Output your response in JSON format that matches the provided schema.
"""

    # Send the prompt along with the response_format to the evaluation LLM
    response = requests.post(
        evaluator_url,
        json={
            'prompt': evaluation_prompt,
            'response_format': {
                'type': 'json_schema',
                'schema': json_schema
            }
        }
    )
    response.raise_for_status()
    output_text = response.json()['output']

    # Parse the JSON output
    try:
        evaluation = json.loads(output_text)
        return evaluation
    except json.JSONDecodeError as e:
        print(f"Error parsing evaluation output: {e}")
        # Handle invalid JSON output
        return {criterion: {'score': 0, 'justification': 'Invalid JSON output.'} for criterion in criteria}

def generate_html_report(results, output_path):
    template = Template("""
    <html>
    <head>
        <title>LLM Evaluation Report</title>
        <style>
            body { font-family: Arial, sans-serif; }
            h1 { text-align: center; }
            .question { margin-top: 20px; }
            .criteria { margin-left: 20px; }
            .criteria ul { list-style-type: none; padding-left: 0; }
            .criteria li { margin-bottom: 5px; }
            .output, .evaluation { margin-left: 20px; }
            pre { background-color: #f4f4f4; padding: 10px; }
        </style>
    </head>
    <body>
        <h1>LLM Evaluation Report</h1>
        {% for dataset_name, entries in results.items() %}
            <h2>Dataset: {{ dataset_name }}</h2>
            {% for entry in entries %}
                <div class="question">
                    <strong>Question {{ entry['id'] }}:</strong> {{ entry['question'] }}
                </div>
                <div class="output">
                    <strong>Model's Answer:</strong>
                    <pre>{{ entry['model_output'] }}</pre>
                </div>
                <div class="evaluation">
                    <strong>Evaluation:</strong>
                    <div class="criteria">
                        <ul>
                        {% for criterion, details in entry['evaluation'].items() %}
                            <li>
                                <strong>{{ criterion }} ({{ details['score'] }}/10):</strong> {{ details['justification'] }}
                            </li>
                        {% endfor %}
                        </ul>
                    </div>
                </div>
                <hr>
            {% endfor %}
        {% endfor %}
    </body>
    </html>
    """)
    html_content = template.render(results=results)
    with open(output_path, 'w') as f:
        f.write(html_content)

def main():
    parser = argparse.ArgumentParser(description='LLM Evaluation Script')
    parser.add_argument('config', help='Path to YAML configuration file')
    parser.add_argument('-o', '--output', help='Output HTML report file', default='report.html')
    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)

    test_llm_url = config['TEST_LLM_BASE_URL']
    evaluation_llm_url = config['EVALUATION_LLM_BASE_URL']
    datasets = config['datasets']
    global_criteria = config.get('global_criteria', [])

    results = {}

    for dataset in datasets:
        dataset_name = dataset['name']
        dataset_file = dataset['file']
        dataset_criteria = dataset.get('criteria', global_criteria)
        data_entries = load_jsonl(dataset_file)
        results[dataset_name] = []

        for entry in data_entries:
            question = entry['question']
            entry_id = entry.get('id', '')

            # Get model output
            try:
                model_output = call_llm(test_llm_url, question)
            except Exception as e:
                print(f"Error calling test LLM: {e}")
                model_output = "Error generating output."

            # Evaluate output
            try:
                evaluation = evaluate_output(
                    evaluation_llm_url,
                    question,
                    model_output,
                    dataset_criteria
                )
            except Exception as e:
                print(f"Error during evaluation: {e}")
                evaluation = {criterion: {'score': 0, 'justification': 'Error during evaluation.'} for criterion in dataset_criteria}

            # Append results
            results[dataset_name].append({
                'id': entry_id,
                'question': question,
                'model_output': model_output,
                'evaluation': evaluation
            })

    # Generate HTML report
    generate_html_report(results, args.output)
    print(f"Report generated at {args.output}")


if __name__ == '__main__':
    main()
