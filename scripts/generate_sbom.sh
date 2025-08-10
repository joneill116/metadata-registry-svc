#!/bin/bash
# Generate a Software Bill of Materials (SBOM) for the project
poetry export -f requirements.txt --output requirements.txt --without-hashes
cyclonedx-py requirements.txt --output sbom.xml
