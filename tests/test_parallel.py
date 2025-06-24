import time


def test_run_command_parallel(bash):
    running_time = 4
    bash.send("source ./gukebox.sh")

    # dop = 3
    start_time = time.time()
    res = bash.send(f"gb::run_command_parallel 3 {running_time} sleep 2").strip(
    ).split("\n")
    end_time = time.time()
    duration = end_time - start_time
    assert len(res) == 7
    assert int(duration) == running_time

    # dop = 8
    start_time = time.time()
    res = bash.send(f"gb::run_command_parallel 8 {running_time} sleep 2").strip(
    ).split("\n")
    end_time = time.time()
    duration = end_time - start_time
    assert len(res) == 17
    assert int(duration) == running_time


def test_run_command_file_parallel(bash, tmp_path):
    job_file = tmp_path / "jobs.txt"
    job_file.write_text("echo one\necho two\necho three\n")
    bash.send("source ./gukebox.sh")
    output = bash.send(f"gb::run_command_file_parallel 2 {job_file}")
    assert 'START: echo one' in output
    assert 'START: echo two' in output
    assert 'START: echo three' in output


def test_get_self_fd_and_mkpipe(bash):
    bash.send("source ./gukebox.sh")
    fd_list = bash.send("gb::get_self_fd | head -n 3").splitlines()
    assert '0' in fd_list and '1' in fd_list and '2' in fd_list
    output = bash.send(
        "gb::mkpipe; echo $GB_FREE_FD; ls /proc/$$/fd/$GB_FREE_FD; exec {GB_FREE_FD}<&-"
    ).splitlines()
    assert output[0].isdigit()
    assert "/proc/" in output[1]
