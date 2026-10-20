#!/bin/sh
# Maven wrapper script for LegalSense
DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$DIR/.tools/apache-maven-3.9.6/bin/mvn" ]; then
    exec "$DIR/.tools/apache-maven-3.9.6/bin/mvn" "$@"
elif command -v mvn >/dev/null 2>&1; then
    exec mvn "$@"
else
    echo "Error: Maven not found." >&2
    exit 1
fi
