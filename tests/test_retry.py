import re


def test_retry_with_constant(bash):
    bash.send("source ./gukebox.sh")
    bash.send("i=0")
    cmd = "if ((i==1)); then true; else i=$((i+1)); false; fi"
    output = bash.send(f"gb::retry_with_constant 2 0 '{cmd}' && echo done")
    assert output.endswith('done')
    assert re.search(r'Retry 1/2 exited 1, retrying in 0 seconds', output)


def test_retry(bash):
    bash.send("source ./gukebox.sh")
    bash.send("sleep() { :; }")
    bash.send("i=0")
    cmd = "if ((i==1)); then true; else i=$((i+1)); false; fi"
    output = bash.send(f"gb::retry 2 '{cmd}' && echo done")
    assert output.endswith('done')
    assert re.search(r'Retry 1/2 exited 1, retrying in [0-9]+ seconds', output)
