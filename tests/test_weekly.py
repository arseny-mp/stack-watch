import os
import sys
import pytest
import tempfile

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "scripts"))
from compile_weekly import parse_daily_summary_sections

def test_parse_daily_summary_sections_new_format():
    with tempfile.TemporaryDirectory() as tmpdir:
        fpath = os.path.join(tmpdir, "summary.md")
        with open(fpath, "w", encoding="utf-8") as f:
            f.write("# Обзор обновлений за 2026-06-19\n\n")
            f.write("## Выводы, требующие немедленных действий (Do Now)\n\n")
            f.write("### 1. HN: Test Title One\n\n")
            f.write("- Источник: url1\n")
            f.write("- Если do-now или experiment: Test Action Plan One (~1 час)\n\n")
            f.write("## Эксперименты (Experiment)\n\n")
            f.write("### 1. HN: Test Title Two\n\n")
            f.write("- Источник: url2\n")
            f.write("- Если do-now или experiment: Test Action Plan Two (~2 часа)\n\n")
            
        do_now, exp = parse_daily_summary_sections(fpath)
        assert "Test Title One — Test Action Plan One (~1 час)" in do_now
        assert "Test Title Two — Test Action Plan Two (~2 часа)" in exp

def test_parse_daily_summary_sections_old_format():
    with tempfile.TemporaryDirectory() as tmpdir:
        fpath = os.path.join(tmpdir, "summary.md")
        with open(fpath, "w", encoding="utf-8") as f:
            f.write("# Stack Watch\n\n")
            f.write("## Do now (high confidence)\n")
            f.write("- test-slug-1 — Title One\n")
            f.write("- test-slug-2 — Title Two\n\n")
            f.write("## Experiment\n")
            f.write("- test-slug-3 — Title Three\n\n")
            
        do_now, exp = parse_daily_summary_sections(fpath)
        assert "test-slug-1 — Title One" in do_now
        assert "test-slug-2 — Title Two" in do_now
        assert "test-slug-3 — Title Three" in exp
