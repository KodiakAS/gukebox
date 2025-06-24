def test_find_all_dir(bash, tmp_path):
    src = tmp_path / "src"
    (src / "a/b").mkdir(parents=True)
    (src / ".hidden").mkdir()
    bash.send("source ./gukebox.sh")
    res_all = bash.send(f"gb::find_all_dir {src} no").splitlines()
    res_no_hidden = bash.send(f"gb::find_all_dir {src} yes").splitlines()
    assert any(str(src / ".hidden") == p for p in res_all)
    assert all(".hidden" not in p for p in res_no_hidden)


def test_copy_tree_struct_and_fast_delete(bash, tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    (src / "a/b").mkdir(parents=True)
    (src / ".hidden/d").mkdir(parents=True)
    dst.mkdir()
    bash.send("source ./gukebox.sh")
    bash.send(f"gb::copy_tree_struct {src} {dst} yes")
    assert (dst / "src/a/b").is_dir()
    assert not (dst / ".hidden").exists()

    # create files and then fast delete
    (dst / "src" / "file1").write_text("x")
    (dst / "src" / "a" / "file2").write_text("y")
    bash.send(f"gb::fast_delete {dst}")
    assert list(dst.rglob("*")) == []


def test_system_utils(bash):
    bash.send("source ./gukebox.sh")
    version = bash.send("gb::get_bash_version")
    assert version
    ret = bash.send(f"gb::check_bash_version {version} && echo ok")
    assert ret == "ok"
    core = int(bash.send("gb::get_core_num"))
    assert core >= 1

