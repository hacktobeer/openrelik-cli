# openrelik-cli

## Features
* workflow
   * create
   * get
   * update
   * status
* templates
   * get
   * update
   * dalete

## Usage 
Create an `env` file with your API key:
````
OPENRELIK_API_KEY=<YOUR_OPENRELIK_API_KEY>
````

```
$ docker run -v -ti -env-file ./env ghcr.io/hacktobeer/openrelik-cli /bin/bash
/app# openrelik-cli --help

Usage: openrelik-cli [OPTIONS] COMMAND [ARGS]...

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.                                                                                                                  │
│ --show-completion             Show completion for the current shell, to copy it or customize the installation.                                                                           │
│ --help                        Show this message and exit.                                                                                                                                │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ template                                                                                                                                                                                 │
│ workflow                                                                                                                                                                                 │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯


```