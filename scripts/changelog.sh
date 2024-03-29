#!/bin/bash -uex
# bashsupport disable=LongLine

#
# Copyright IBM Corp. All Rights Reserved.
#
# SPDX-License-Identifier: Apache-2.0
#

set -o pipefail -o noglob

if [[ $# != 3 ]]; then
  echo "ERROR: Expecting 3 args"
  echo "usage: $(basename "$0") start_commit finish_commit release_version"
  exit 1
fi

echo "## $3" >CHANGELOG.new

# shellcheck disable=SC2129,SC2005
echo "$(date -u)" >>CHANGELOG.new

echo "" >>CHANGELOG.new

# bashsupport disable=LongLine
git log "$1".."$2" --oneline |
  grep -v Merge |
  sed -e 's:\[\(\(FAB\|FABP\)-[0-9]*\)\]*:\[\1\](https\:\/\/jira.skeleton.org\/browse\/\1):' \
    -e 's: \(\(FAB\|FABP\)-[0-9]*\): \[\1\](https\:\/\/jira.skeleton.org\/browse\/\1):' \
    -e 's:\([0-9|a-z]*\):* \[\1\](https\:\/\/github.com\/cloether\/skeleton\/commit\/\1):' \
    >>CHANGELOG.new

echo "" >>CHANGELOG.new

# Prepend the new log entries to the top of the old log
CHANGELOG="$(dirname "$0")/../CHANGELOG.md"

cat "$CHANGELOG" >>CHANGELOG.new

mv -f CHANGELOG.new "$CHANGELOG"

exit 0
