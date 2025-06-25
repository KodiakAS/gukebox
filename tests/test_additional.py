import re
import time


def test_get_self_fd(bash):
    bash.send("source ./gukebox.sh")
    ret = bash.send("gb::get_self_fd | head -n 1")
    assert ret.isdigit()


def test_mkpipe(bash):
    bash.send("source ./gukebox.sh")
    bash.send("gb::mkpipe")
    res = bash.send("echo hi >&${GB_FREE_FD}; read line <&${GB_FREE_FD}; echo $line")
    bash.send("exec {GB_FREE_FD}<&-")
    assert res == "hi"


def test_run_command_file_parallel(bash, tmp_path):
    job_file = tmp_path / "jobs.txt"
    job_file.write_text("sleep 1\nsleep 1\nsleep 1\n")
    bash.send("source ./gukebox.sh")
    start = time.time()
    out = bash.send(f"gb::run_command_file_parallel 2 {job_file}")
    duration = time.time() - start
    assert len(out.strip().split("\n")) == 3
    assert int(round(duration)) == 2


def test_find_all_dir(bash, tmp_path):
    base = tmp_path / "base"
    (base / "sub").mkdir(parents=True)
    (base / ".hidden").mkdir()
    bash.send("source ./gukebox.sh")
    ret = bash.send(f"gb::find_all_dir {base} no | sort")
    lines = ret.splitlines()
    assert str(base / ".hidden") in lines
    ret = bash.send(f"gb::find_all_dir {base} yes | sort")
    lines = ret.splitlines()
    assert str(base / ".hidden") not in lines


def test_copy_tree_struct(bash, tmp_path):
    src = tmp_path / "srcdir"
    dst = tmp_path / "dstdir"
    (src / "a").mkdir(parents=True)
    (src / ".hidden").mkdir()
    bash.send("source ./gukebox.sh")
    bash.send(f"gb::copy_tree_struct {src} {dst} yes")
    assert (dst / src.name / "a").is_dir()
    assert not (dst / src.name / ".hidden").exists()


def test_fast_delete(bash, tmp_path):
    target = tmp_path / "todel"
    target.mkdir()
    (target / "a").write_text("")
    (target / "b").write_text("")
    bash.send("source ./gukebox.sh")
    bash.send(f"gb::fast_delete {target}")
    assert not any(target.iterdir())


def test_get_bash_version(bash):
    bash.send("source ./gukebox.sh")
    ret = bash.send("gb::get_bash_version")
    assert re.fullmatch(r"\d+\.\d+\.\d+", ret)


def test_check_bash_version(bash):
    bash.send("source ./gukebox.sh")
    assert bash.send("gb::check_bash_version 4.0.0 && echo ok") == "ok"
    out = bash.send("gb::check_bash_version 99.0.0 && echo ok || echo fail")
    assert out.splitlines()[-1] == "fail"


def test_get_core_num(bash):
    bash.send("source ./gukebox.sh")
    ret = int(bash.send("gb::get_core_num"))
    assert ret >= 1


def test_retry_with_constant(bash):
    bash.send("source ./gukebox.sh")
    bash.send("i=0")
    bash.send(
        "fail_or_success(){ i=$((i+1)); if [[ $i -ge 2 ]]; then return 0; else return 1; fi }"
    )
    ret = bash.send("gb::retry_with_constant 3 1 fail_or_success && echo ok")
    assert ret.splitlines()[-1] == "ok"
    bash.send("always_fail(){ return 1; }")
    ret = bash.send("gb::retry_with_constant 1 1 always_fail && echo ok || echo fail")
    assert ret.splitlines()[-1] == "fail"
