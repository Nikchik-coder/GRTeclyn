"""The pack scrubber removes a machine name it could not have derived."""

from __future__ import annotations

from pathlib import Path

from grteclyn_wrapper.packaging.scrub_paths import scrub


def test_backtrace_host_name_of_another_node_is_redacted(tmp_path: Path) -> None:
    # A crash report written on a node that is not the one packing it: nothing in
    # the environment names that node, so only the field itself can catch it.
    bt = tmp_path / "backtrace.txt"
    bt.write_text(
        "=== If no file names and line numbers are shown below, one can run\n"
        "Host Name: node-a17-rack4-gpu-3-1-0\n"
        "=== Please note that the line number reported by addr2line may not be accurate.\n",
        encoding="utf-8",
    )
    scrub(bt)
    text = bt.read_text(encoding="utf-8")
    assert "Host Name: <redacted>\n" in text
    assert "node-a17" not in text
    assert "addr2line may not be accurate" in text


def test_prose_mentioning_host_name_is_left_alone(tmp_path: Path) -> None:
    note = tmp_path / "NOTES.md"
    note.write_text("the Host Name: field is scrubbed at pack time\n", encoding="utf-8")
    scrub(note)
    assert note.read_text(encoding="utf-8") == "the Host Name: field is scrubbed at pack time\n"
