import pytest_shell
import re
import os


def test_info(bash):
    bash.send("source ./gukebox.sh")
    ret = bash.send("gb::log::info info")
    assert re.fullmatch(
        r'\[(\d){4} ([0-1][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])\] info', ret)


def test_info_loggername(bash):
    with bash(envvars={'LOGGER_NAME': 'test'}):
        bash.send("source ./gukebox.sh")
        ret = bash.send("gb::log::info info")
        assert re.fullmatch(
            r'\[(\d){4} ([0-1][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])\]\[test\] info',
            ret)


def test_error(bash):
    bash.send("source ./gukebox.sh")
    ret = bash.send("gb::log::error info")
    assert re.fullmatch(
        r'\[(\d){4} ([0-1][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])\]\[ERROR\] info',
        ret)


def test_error_loggername(bash):
    with bash(envvars={'LOGGER_NAME': 'test'}):
        bash.send("source ./gukebox.sh")
        ret = bash.send("gb::log::error info")
        assert re.fullmatch(
            r'\[(\d){4} ([0-1][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])\]\[test\]\[ERROR\] info',
            ret)


def test_error_handler_errexit(bash):
    bash.auto_return_code_error = False
    case_file = "tests/test_error_handler_errexit.sh"
    case = """#!/usr/bin/env bash

# shellcheck disable=SC1091

CUR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"

source "${CUR_DIR}/../gukebox.sh"

retuen_error() {
    gb::err 127
}

hello() {
    retuen_error
}

hello
"""
    with open(case_file, "w") as f:
        f.write(case)

    ret = bash.send(f"bash {case_file}")
    assert "exited with status 127" in ret
    assert f"1: {case_file}:10 retuen_error(...)" in ret
    assert f"2: {case_file}:14 hello(...)" in ret
    assert f"3: {case_file}:17 main(...)" in ret
    os.remove(case_file)


def test_error_handler_cmdexit(bash):
    case_file = "tests/test_error_handler_cmdexit.sh"
    bash.auto_return_code_error = False
    case = """#!/usr/bin/env bash

# shellcheck disable=SC1091

CUR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"

source "${CUR_DIR}/../gukebox.sh"

retuen_error() {
    exit 255
}

hello() {
    retuen_error
}

hello
"""
    with open(case_file, "w") as f:
        f.write(case)

    ret = bash.send(f"bash {case_file}")
    assert "Exit by command 'exit 255'" in ret
    assert f"1: {case_file}:1 retuen_error(...)" in ret
    assert f"2: {case_file}:14 hello(...)" in ret
    assert f"3: {case_file}:17 main(...)" in ret
    os.remove(case_file)
