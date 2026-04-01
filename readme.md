# Prototype server re-implementation for TES: Blades

This is a prototype-level reimplementation of TES: Blades

You will need to:
1. run generate_download_from_dump to extract a dump (or download the data folder from https://cloud.mariusdavid.fr/s/8cGpkqpd6jCFp8s . Make it so you have a folder data/bundles.blades.bgs.services)
2. have your client configured with mitm (https://cloud.mariusdavid.fr/s/86mbGEPYa8TxCkK) with the script "mitmproxy_script.py" running (by adding the CLI argument -s ./mitmproxy_script.py from the project folder)
3. run server.py
Make to start from a fresh save. You won’t go far, but you will pass the early tutorial and download the data.

The actually interesting code is in dispatch.py
