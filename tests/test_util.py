import pytest_shell
import re


def test_not_empty(bash):
    with bash(envvars={'EMPTY': '', "NOT": "a"}):
        bash.send("source ./gukebox.sh")

        ret = bash.send("gb::not_empty ${NOT} && echo yes || echo no")
        assert ret == "yes"
        ret = bash.send("gb::not_empty ${EMPTY} && echo yes || echo no")
        assert ret == "no"


def test_is_num(bash):
    bash.send("source ./gukebox.sh")

    ret = bash.send("gb::is_num 2a && echo yes || echo no")
    assert ret == "no"
    ret = bash.send("gb::is_num n && echo yes || echo no")
    assert ret == "no"
    ret = bash.send("gb::is_num 2 && echo yes || echo no")
    assert ret == "yes"


def test_in_array(bash):
    bash.send("source ./gukebox.sh")
    bash.send('ARR=(one two three)')

    ret = bash.send('gb::in_array one "${ARR[@]}" && echo yes || echo no')
    assert ret == "yes"
    ret = bash.send('gb::in_array four "${ARR[@]}" && echo yes || echo no')
    assert ret == "no"
    ret = bash.send('gb::in_array e "${ARR[@]}" && echo yes || echo no')
    assert ret == "no"


def test_join(bash):
    bash.send("source ./gukebox.sh")
    assert bash.send('gb::join , a b c') == "a,b,c"
    assert bash.send('gb::join - asd sd sss') == "asd-sd-sss"


def test_upper(bash):
    bash.send("source ./gukebox.sh")
    assert bash.send('gb::upper up') == "UP"
    assert bash.send('gb::upper Up') == "UP"


def test_lower(bash):
    bash.send("source ./gukebox.sh")
    assert bash.send('gb::lower UP') == "up"
    assert bash.send('gb::lower Up') == "up"


def test_in_array(bash):
    bash.send("source ./gukebox.sh")
    bash.send('MIN=1.2.4')

    ret = bash.send('gb::compare_version 1.2.4 "${MIN}" && echo $? || echo $?')
    assert ret == "0"

    ret = bash.send('gb::compare_version 1.2.5 "${MIN}" && echo $? || echo $?')
    assert ret == "1"
    ret = bash.send('gb::compare_version 1.11.5 "${MIN}" && echo $? || echo $?')
    assert ret == "1"

    ret = bash.send('gb::compare_version 1.2 "${MIN}" && echo $? || echo $?')
    assert ret == "2"
    ret = bash.send('gb::compare_version 1.1.99 "${MIN}" && echo $? || echo $?')
    assert ret == "2"