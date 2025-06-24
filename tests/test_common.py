def test_err_and_used(bash):
    bash.auto_return_code_error = False
    script = """source ./gukebox.sh
trap - ERR
set +e
f(){ gb::used VAR; gb::err 5; echo $?; }
f
"""
    ret = bash.send(script)
    assert ret.strip().splitlines()[-1] == "5"
