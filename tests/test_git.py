import os
import re


def test_show_root(bash):
    bash.send("source ./gukebox.sh")
    assert bash.send('gb::git::show_root') == os.getcwd()


def test_get_last_tag(bash):
    bash.send("source ./gukebox.sh")
    ret = bash.send("gb::git::get_last_tag")
    assert re.fullmatch(r'\d\.\d\.\d', ret)


def test_count_commits_ahead_last_tag(bash):
    bash.send("source ./gukebox.sh")
    ret = bash.send("gb::git::count_commits_ahead_last_tag")
    assert re.fullmatch(r'\d', ret)
