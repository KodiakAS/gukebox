import os


def test_show_root(bash):
    bash.send("source ./gukebox.sh")
    assert bash.send('gb::git::show_root') == os.getcwd()
