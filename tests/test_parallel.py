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
