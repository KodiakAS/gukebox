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


def test_infolist(bash):
    bash.send("source ./gukebox.sh")
    ret = bash.send("gb::log::infolist title line1 line2")
    assert re.fullmatch(
        r'\[(\d){4} ([0-1][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])\] title\n    line1\n    line2',
        ret)


def test_raise(bash):
    bash.send("source ./gukebox.sh")
    ret = bash.send("gb::log::raise noo || echo $?")
    assert re.fullmatch(
        r'\[(\d){4} ([0-1][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])\]\[ERROR\] noo\n1',
        ret)


def test_stack(bash):
    case_file = "tests/test_stack.sh"
    case = """source "gukebox.sh"

func3() {
    gb::log::stack
}

func2() {
    func3
}

func1() {
    func2
}

func1
"""
    with open(case_file, "w") as f:
        f.write(case)

    ret = bash.send(f"bash {case_file}")
    assert ret == f"""Call stack:
  1: {case_file}:4 func3(...)
  2: {case_file}:8 func2(...)
  3: {case_file}:12 func1(...)
  4: {case_file}:15 main(...)"""
    os.remove(case_file)


def test_stack_skip2(bash):
    case_file = "tests/test_stack.sh"
    case = """source "gukebox.sh"

func3() {
    gb::log::stack 2
}

func2() {
    func3
}

func1() {
    func2
}

func1
"""
    with open(case_file, "w") as f:
        f.write(case)

    ret = bash.send(f"bash {case_file}")
    assert ret == f"""Call stack:
  1: {case_file}:12 func1(...)
  2: {case_file}:15 main(...)"""
    os.remove(case_file)


def test_error_handler_errexit(bash):
    bash.auto_return_code_error = False
    case_file = "tests/test_error_handler_errexit.sh"
    case = """source "gukebox.sh"

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
    assert f"1: {case_file}:4 retuen_error(...)" in ret
    assert f"2: {case_file}:8 hello(...)" in ret
    assert f"3: {case_file}:11 main(...)" in ret
    os.remove(case_file)


def test_error_handler_cmdexit(bash):
    case_file = "tests/test_error_handler_cmdexit.sh"
    bash.auto_return_code_error = False
    case = """source "gukebox.sh"

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
    assert f"2: {case_file}:8 hello(...)" in ret
    assert f"3: {case_file}:11 main(...)" in ret
    os.remove(case_file)
