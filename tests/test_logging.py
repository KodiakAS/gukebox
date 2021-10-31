import pytest_shell
import re


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
    ret = bash.send("bash tests/test_error_handler_errexit.sh")
    assert "exited with status 127" in ret
    assert "1: tests/test_error_handler_errexit.sh:10 retuen_error(...)" in ret
    assert "2: tests/test_error_handler_errexit.sh:14 hello(...)" in ret
    assert "3: tests/test_error_handler_errexit.sh:17 main(...)" in ret


def test_error_handler_cmdexit(bash):
    bash.auto_return_code_error = False
    ret = bash.send("bash tests/test_error_handler_cmdexit.sh")
    assert "Exit by command 'exit 255'" in ret
    assert "1: tests/test_error_handler_cmdexit.sh:1 retuen_error(...)" in ret
    assert "2: tests/test_error_handler_cmdexit.sh:14 hello(...)" in ret
    assert "3: tests/test_error_handler_cmdexit.sh:17 main(...)" in ret
