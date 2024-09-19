#!/usr/bin/env bash
set -eo pipefail

# Generate example usage section of README.md

./lint_and_test.sh

function comment {
    echo "<!-- ${1} -->"
}

function echo_and_run {
    command=${1}
    lines=${2}

    echo '```'
    echo "$ ${command}"

    if [ ${lines} ]; then
        ${command} | head -n ${lines}
        echo '--snip--'
    else
        ${command}
    fi

    echo '```'
}

echo_and_run 'ascents -h' 1

echo 'Initialize ascent database:'
echo_and_run 'ascents init ascent.db'

echo 'Log an ascent:'
comment 'Slither 5.7 at Reimers Ranch on 2022-06-27'
echo_and_run 'ascents log ascent.db'

echo 'Search the database:'
comment 'grade: 5.7, date: 2022*, accept default order'
echo_and_run 'ascents search ascent.db'

echo 'Analyze the database:'
echo_and_run 'ascents analyze ascent.db' 13
