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
            