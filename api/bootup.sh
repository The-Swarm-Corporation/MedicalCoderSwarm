#!/bin/bash
set -x
set -e
#pip3 install -r requirements.txt

#uvicorn main:app --host 0.0.0.0 --port 8000 --reload

#CMD ["/usr/bin/unbuffer", "/var/swarms/agent_workspace/.venv/bin/uvicorn", "--proxy-headers", "--forwarded-allow-ips='*'", "--workers=4", "--port=8000",    "--reload-delay=30",  "main:create_app"]
