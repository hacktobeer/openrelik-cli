import json
from pathlib import Path
import logging
import os
import typer
from typing_extensions import Annotated
from rich.pretty import pprint


from openrelik_api_client.api_client import APIClient
import openrelik_api_client.workflows as workflowapi

logger = logging.getLogger(__name__)

OPENRELIK_API_URL = os.environ.get("OPENRELIK_API_URL", "http://localhost:8710")
OPENRELIK_API_KEY = os.environ.get("OPENRELIK_API_KEY", None)

if OPENRELIK_API_KEY is None:
    raise RuntimeError("No OPENRELIK_API_KEY set!")

api_client = APIClient(OPENRELIK_API_URL, OPENRELIK_API_KEY)

app = typer.Typer()
template_app = typer.Typer()
app.add_typer(template_app, name="template")
workflow_app = typer.Typer()
app.add_typer(workflow_app, name="workflow")


@workflow_app.command("create")
def create(
    file_id: Annotated[int, typer.Option(help="File ID.")],
) -> str | None:
    # Get folder_id from 1st source_id
    response = api_client.get(f"/files/{file_id}")
    file = json.loads(response.content)
    folder_id = int(file["folder"]["id"])

    # Create a workflow in a folder for a file.
    workflow_id = workflowapi.WorkflowsAPI(api_client).create_workflow(
        folder_id, [file_id]
    )
    print(f"Workflow ID: {workflow_id} in folder {folder_id}")


@workflow_app.command("get")
def get_workflow(
    workflow_id: Annotated[int, typer.Option(help="Workflow ID.")],
    folder_id: Annotated[int, typer.Option(help="Folder ID.")],
) -> str | None:
    # Get a workflow in a folder.
    workflow = workflowapi.WorkflowsAPI(api_client).get_workflow(folder_id, workflow_id)

    print(f"Workflow ID: {workflow_id}\n")
    print(workflow)


@workflow_app.command("update")
def update_workflow_spec(
    workflow_id: Annotated[int, typer.Option(help="Workflow ID.")],
    folder_id: Annotated[int, typer.Option(help="Folder ID.")],
    file: Annotated[str, typer.Option(help="Filepath to workflow JSON spec.")],
) -> str | None:
    # Update a workflow in a folder with a new JSON spec.
    workflow = workflowapi.WorkflowsAPI(api_client).get_workflow(folder_id, workflow_id)
    folder_id = workflow["folder"]["id"]
    spec = Path(file).read_text()
    try:
        json.loads(spec)
    except Exception as e:
        raise e
    workflow["spec_json"] = spec
    workflowapi.WorkflowsAPI(api_client).update_workflow(
        folder_id, workflow_id, workflow
    )


@template_app.command("get")
def get_template(
    id: Annotated[int | None, typer.Option(help="Template ID.")] = None,
    nice: Annotated[bool, typer.Option(help="Output pretty JSON format.")] = False,
) -> str | None:
    # Get all templates or a specific template json spec by id
    response = api_client.get("/workflows/templates/")
    templates = json.loads(response.text)

    result = ""
    if id:
        for template in templates:
            if template.get("id") == id:
                result = template["spec_json"]
    else:
        data = []
        # Only return IDs and names of workflows
        for template in templates:
            data.append(
                {
                    "id": template.get("id"),
                    "display_name": template.get("display_name"),
                }
            )
        result = json.dumps(data)

    if nice:
        pprint(json.loads(result))
    else:
        print(result)


@template_app.command("delete")
def delete(template_id) -> int | None:
    # Delete template with
    # Does not exist
    print("delete - Not implemented yet server side!")
    pass


@template_app.command("update")
def update(template_id, file_path) -> int | None:
    # Update template with spec from file_path and return template id
    # Does not exist
    print("update - Not implemented yet server side!")
    pass


if __name__ == "__main__":
    app()
