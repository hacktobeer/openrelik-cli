#!/usr/bin/env -S uv run --script

import json
import logging
import os
import sys
import typer

from pathlib import Path
from rich.console import Console
from rich.pretty import pprint
from rich.table import Table
from typing_extensions import Annotated


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
folder_app = typer.Typer()
app.add_typer(folder_app, name="folder")
files_app = typer.Typer()
app.add_typer(files_app, name="files")


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
    folder_id: Annotated[int | None, typer.Option(help="Folder ID.")] = None,
    workflow_id: Annotated[int | None, typer.Option(help="Workflow ID.")] = None,
) -> str | None:
    # Get a workflows in a folder or a specific workflow by id.
    if workflow_id:
        workflow = api_client.get(f"/folders/0/workflows/{workflow_id}")
    elif folder_id:
        workflow = api_client.get(f"/folders/{folder_id}/workflows/workflows")
    else:
        print("Error: workflow-id or folder-id needed.")
        return

    pprint(json.loads(workflow.text))


@workflow_app.command("status")
def status_workflow(
    workflow_id: Annotated[int, typer.Option(help="Workflow ID.")],
    raw: Annotated[bool, typer.Option(help="Output raw json API reply.")] = False,
) -> str | None:
    # Get the status of a workflow in a folder.
    workflow = api_client.get(f"/folders/0/workflows/{workflow_id}")
    workflow = json.loads(workflow.text)
    print(f"Name: {workflow.get('display_name')}")
    if raw:
        pprint(workflow)
    else:
        table = Table()
        table.add_column("Task ID")
        table.add_column("Name")
        table.add_column("Status")
        for task in workflow.get("tasks"):
            table.add_row(
                str(task.get("id")), task.get("display_name"), task.get("status_short")
            )
        console = Console()
        console.print(table)


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
                result = json.dumps(template)
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
        pprint(result)
    else:
        print(result)


@template_app.command("delete")
def delete_template(
    template_id: Annotated[int, typer.Option(help="Template ID.")],
) -> str | None:
    if template_id:
        template = api_client.delete(f"/workflows/templates/{template_id}")
    else:
        print("Error: template-id needed.")
        return

    print("Template succesfully deleted.")


@template_app.command("update")
def update_template(
    template_id: Annotated[int, typer.Option(help="Template ID.")],
    file_path: Annotated[str, typer.Option(help="Filepath with new template data.")],
) -> str | None:
    # Update template with spec from file_path and return template id
    # Does not exist
    with open(file_path, "r") as f:
        jsonstr = f.read()
        print(jsonstr)
        r = api_client.patch(f"/workflows/templates/{template_id}", data=jsonstr)
        print(r.text)


@folder_app.command("get")
def get_folder(
    folder_id: Annotated[int | None, typer.Option(help="Folder ID.")] = None,
    raw: Annotated[bool, typer.Option(help="Output raw json API reply.")] = False,
) -> str | None:
    if folder_id:
        result = api_client.get(f"/folders/{folder_id}")
        subfolders = api_client.get(f"/folders/{folder_id}/folders/")
    else:
        result = api_client.get("/folders/")
        subfolders = None

    result = [json.loads(result.text)]
    if raw:
        pprint(result)
    else:
        table = Table()
        table.add_column("ID")
        table.add_column("Name")
        for folder in result:
            table.add_row(str(folder.get("id")), folder.get("display_name"))

        console = Console()
        console.print(table)

        if subfolders:
            table = Table(title="Subfolders")
            table.add_column("ID")
            table.add_column("Name")
            for folder in json.loads(subfolders.text):
                table.add_row(str(folder.get("id")), folder.get("display_name"))
            console = Console()
            console.print(table)

        for folder in result:
            table = Table(title=f"Workflows for folder {folder_id}")
            table.add_column("ID")
            table.add_column("Name")
            for workflow in folder.get("workflows"):
                table.add_row(str(workflow.get("id")), workflow.get("display_name"))
            console = Console()
            console.print(table)


@files_app.command("get")
def get_files(
    folder_id: Annotated[int | None, typer.Option(help="Folder ID.")] = None,
    raw: Annotated[bool, typer.Option(help="Output raw json API reply.")] = False,
) -> str | None:
    if folder_id:
        result = api_client.get(f"/folders/{folder_id}/files/")
        result = json.loads(result.text)
        if raw:
            pprint(result)
        else:
            table = Table()
            table.add_column("ID")
            table.add_column("Filename")
            table.add_column("Size")
            table.add_column("Datatype")
            table.add_column("Mimetype")
            for f in result:
                table.add_row(
                    str(f.get("id")),
                    f.get("display_name"),
                    str(f.get("filesize")),
                    f.get("data_type"),
                    f.get("magic_mime"),
                )
            console = Console()
            console.print(table)


@files_app.command("download")
def download_file(
    file_id: Annotated[int, typer.Option(help="File ID.")],
) -> str | None:
    r = api_client.get(f"/files/{file_id}/download").content
    sys.stdout.buffer.write(r)


@files_app.command("upload")
def upload_file(
    file_path: Annotated[str, typer.Option(help="File path.")],
    folder_id: Annotated[int, typer.Option(help="Folder ID.")],
) -> int | None:
    r = api_client.upload_file(file_path, folder_id)
    print(f"File ID: {r}")


if __name__ == "__main__":
    app()
