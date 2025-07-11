from pathlib import Path

import os
import shutil


def test_not_empty(bash):
    with bash(envvars={"EMPTY": "", "NOT": "a"}):
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
    bash.send("ARR=(one two three)")

    ret = bash.send('gb::in_array one "${ARR[@]}" && echo yes || echo no')
    assert ret == "yes"
    ret = bash.send('gb::in_array four "${ARR[@]}" && echo yes || echo no')
    assert ret == "no"
    ret = bash.send('gb::in_array e "${ARR[@]}" && echo yes || echo no')
    assert ret == "no"


def test_join(bash):
    bash.send("source ./gukebox.sh")
    assert bash.send("gb::join , a b c") == "a,b,c"
    assert bash.send("gb::join - asd sd sss") == "asd-sd-sss"


def test_upper(bash):
    bash.send("source ./gukebox.sh")
    assert bash.send("gb::upper up") == "UP"
    assert bash.send("gb::upper Up") == "UP"


def test_lower(bash):
    bash.send("source ./gukebox.sh")
    assert bash.send("gb::lower UP") == "up"
    assert bash.send("gb::lower Up") == "up"


def test_isdigit(bash):
    bash.send("source ./gukebox.sh")
    ret = bash.send("gb::isdigit 123 && echo 0 || echo $?")
    assert ret == "0"
    ret = bash.send("gb::isdigit 12_3 && echo 0 || echo $?")
    assert ret == "1"


def test_compare_version(bash):
    bash.send("source ./gukebox.sh")
    bash.send("MIN=1.2.4")

    ret = bash.send('gb::compare_version 1.2.4 "${MIN}" && echo $? || echo $?')
    assert ret == "0"
    ret = bash.send('gb::compare_version 1.2.4. "${MIN}" && echo $? || echo $?')
    assert ret == "0"
    ret = bash.send('gb::compare_version 1.2.4.rc "${MIN}" && echo $? || echo $?')
    assert ret == "0"

    ret = bash.send('gb::compare_version 1.2.4-patch1 "${MIN}" && echo $? || echo $?')
    assert ret == "1"
    ret = bash.send('gb::compare_version 1.2.5 "${MIN}" && echo $? || echo $?')
    assert ret == "1"
    ret = bash.send('gb::compare_version 1.11.5 "${MIN}" && echo $? || echo $?')
    assert ret == "1"
    ret = bash.send('gb::compare_version "${MIN}" 1.0.324 && echo $? || echo $?')
    assert ret == "1"
    ret = bash.send('gb::compare_version 1.2.4.13 "${MIN}" && echo $? || echo $?')
    assert ret == "1"

    ret = bash.send('gb::compare_version 1.2 "${MIN}" && echo $? || echo $?')
    assert ret == "2"
    ret = bash.send('gb::compare_version 1.1.99 "${MIN}" && echo $? || echo $?')
    assert ret == "2"
    ret = bash.send('gb::compare_version 1.2.. "${MIN}" && echo $? || echo $?')
    assert ret == "2"


def test_copy_tree_mod(bash):
    src = "tests/test_copy_tree_mod_src"
    dst = "tests/test_copy_tree_mod_dst"

    shutil.rmtree(src, ignore_errors=True)
    shutil.rmtree(dst, ignore_errors=True)
    os.mkdir(src, 0o755)
    os.mkdir(f"{src}/sub", 0o755)
    Path(f"{src}/file1").touch(0o644)
    Path(f"{src}/file 2").touch(0o644)
    Path(f"{src}/file99").touch(0o644)
    Path(f"{src}/sub/file1").touch(0o644)

    os.mkdir(dst, 0o755)
    os.mkdir(f"{dst}/sub", 0o755)
    Path(f"{dst}/file1").touch(0o755)
    Path(f"{dst}/file 2").touch(0o755)
    Path(f"{dst}/file3").touch(0o755)
    Path(f"{dst}/sub/file1").touch(0o755)

    bash.send("source ./gukebox.sh")
    bash.send(f"gb::copy_tree_mod {src} {dst}")
    assert oct(Path(f"{src}/file1").stat().st_mode) == "0o100644"
    assert oct(Path(f"{src}/file 2").stat().st_mode) == "0o100644"
    assert oct(Path(f"{src}/file99").stat().st_mode) == "0o100644"
    assert oct(Path(f"{src}/sub/file1").stat().st_mode) == "0o100644"
    assert oct(Path(f"{dst}/file1").stat().st_mode) == "0o100644"
    assert oct(Path(f"{dst}/file 2").stat().st_mode) == "0o100644"
    assert oct(Path(f"{dst}/file3").stat().st_mode) == "0o100755"
    assert oct(Path(f"{dst}/sub/file1").stat().st_mode) == "0o100644"
    shutil.rmtree(src, ignore_errors=True)
    shutil.rmtree(dst, ignore_errors=True)


def test_iam_root(bash):
    bash.send("source ./gukebox.sh")
    if os.geteuid() == 0:
        assert bash.send("gb::iam_root && echo yes || echo no") == "yes"
    else:
        assert bash.send("gb::iam_root && echo yes || echo no") == "no"


def test_iam_normal_user(bash):
    bash.send("source ./gukebox.sh")
    if os.geteuid() == 0:
        assert bash.send("gb::iam_normal_user && echo yes || echo no") == "no"
    else:
        assert bash.send("gb::iam_normal_user && echo yes || echo no") == "yes"


def test_get_flag_value(bash):
    bash.send("source ./gukebox.sh")
    cases = ["--te2st=1", "--test2=char", "--test3=char/-*1"]
    res = []
    for c in cases:
        res.append(bash.send(f"gb::get_flag_value {c}"))
    assert res == ["1", "char", "char/-*1"]


def test_cmd_exists(bash):
    bash.send("source ./gukebox.sh")
    assert bash.send("gb::cmd_exists asd2 && echo yes || echo no") == "no"
    assert bash.send("gb::cmd_exists ls && echo yes || echo no") == "yes"
