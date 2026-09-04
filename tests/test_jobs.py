from wmbench.runner.jobs import load_done, run_items, tmux_command


def test_run_items_skips_finished(tmp_path):
    path = tmp_path / "out.jsonl"
    calls = []

    def work(i):
        calls.append(i)
        return {"value": i * 2}

    finished, skipped = run_items([1, 2, 3], lambda i: f"k{i}", work, path)
    assert (finished, skipped) == (3, 0)
    finished, skipped = run_items([1, 2, 3, 4], lambda i: f"k{i}", work, path)
    assert (finished, skipped) == (1, 3)
    assert calls == [1, 2, 3, 4]
    assert load_done(path) == {"k1", "k2", "k3", "k4"}


def test_load_done_missing(tmp_path):
    assert load_done(tmp_path / "none.jsonl") == set()


def test_tmux_command_redirects_log():
    cmd = tmux_command("job", "python run.py", "/tmp/job.log")
    assert cmd[:5] == ["tmux", "new-session", "-d", "-s", "job"]
    assert cmd[5] == "python run.py > /tmp/job.log 2>&1"
