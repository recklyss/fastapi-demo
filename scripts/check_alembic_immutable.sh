#!/usr/bin/env bash
# Fail if any Alembic revision that already exists on the base branch is
# modified, deleted, or renamed. New migration files are allowed.
set -euo pipefail

BASE_REF="${1:-origin/main}"
HEAD_REF="${2:-HEAD}"

if ! git rev-parse --verify "$BASE_REF" >/dev/null 2>&1; then
  if git rev-parse --verify origin/master >/dev/null 2>&1; then
    BASE_REF="origin/master"
  else
    echo "Base ref '$BASE_REF' not found. Fetch the default branch first."
    exit 1
  fi
fi

failed=0
echo "Alembic version changes vs ${BASE_REF}:"

while IFS=$'\t' read -r change_type path extra; do
  [[ -z "${change_type}" ]] && continue

  if [[ -n "${extra}" ]]; then
    echo "  ${change_type} ${path} -> ${extra}"
    display="${path} -> ${extra}"
  else
    echo "  ${change_type} ${path}"
    display="${path}"
  fi

  case "${change_type}" in
    A)
      # New revision file — allowed.
      ;;
    *)
      echo "ERROR: existing Alembic migrations must not be edited, deleted, or renamed."
      echo "       Add a new revision instead of changing '${display}'."
      failed=1
      ;;
  esac
done < <(git diff --name-status "${BASE_REF}...${HEAD_REF}" -- alembic/versions/)

if [[ "${failed}" -ne 0 ]]; then
  exit 1
fi

echo "Alembic immutability check passed."
