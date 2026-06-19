import os
import sys
import pytest
import tempfile

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "scripts"))
from delivery_helper import html_escape, get_component_layer, parse_summary_findings, lookup_metadata

def test_html_escape():
    assert html_escape("hello") == "hello"
    assert html_escape("hello <world>") == "hello &lt;world&gt;"
    assert html_escape("foo & bar") == "foo &amp; bar"
    assert html_escape("") == ""
    assert html_escape(None) == ""

def test_get_component_layer():
    assert get_component_layer("Claude Code CLI") == 1
    assert get_component_layer("Obsidian Notes") == 2
    assert get_component_layer("Mem0 database") == 3
    assert get_component_layer("random component") == 4

def test_parse_summary_findings_log_additions():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a dummy log-additions.md
        log_file = os.path.join(tmpdir, "log-additions.md")
        with open(log_file, "w", encoding="utf-8") as f:
            f.write("| test-slug-1 | do now | high | test-touches | 2026-06-19 | url1 |\n")
            f.write("| test-slug-2 | experiment | medium | test-touches | 2026-06-19 | url2 |\n")
            f.write("| test-slug-3 | parking lot | low | test-touches | 2026-06-19 | url3 |\n")
            
        # Create external-research detailed files
        research_dir = os.path.join(tmpdir, "external-research")
        os.makedirs(research_dir, exist_ok=True)
        
        with open(os.path.join(research_dir, "test-slug-1.md"), "w", encoding="utf-8") as f:
            f.write("# Finding Title One\n**Verdict:** do now\n")
            
        with open(os.path.join(research_dir, "test-slug-2.md"), "w", encoding="utf-8") as f:
            f.write("# Finding Title Two\\n**Verdict:** experiment\n")  # Literal \n
            
        with open(os.path.join(research_dir, "test-slug-3.md"), "w", encoding="utf-8") as f:
            f.write("# Finding Title Three\n")
            
        summary_file = os.path.join(tmpdir, "summary.md")
        
        res_do_now = parse_summary_findings(summary_file, "Do now (high confidence)")
        assert len(res_do_now) == 1
        assert res_do_now[0] == ("test-slug-1", "Finding Title One")
        
        res_exp = parse_summary_findings(summary_file, "Experiment")
        assert len(res_exp) == 1
        assert res_exp[0] == ("test-slug-2", "Finding Title Two")
        
        res_park = parse_summary_findings(summary_file, "Parking")
        assert len(res_park) == 1
        assert res_park[0] == ("test-slug-3", "Finding Title Three")

def test_parse_summary_findings_fallback():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a dummy summary.md in the old format
        summary_file = os.path.join(tmpdir, "summary.md")
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write("# Stack Watch\n\n")
            f.write("## Do now (high confidence)\n")
            f.write("- test-slug-1 — Finding Title One\n\n")
            f.write("## Experiment\n")
            f.write("- test-slug-2 — Finding Title Two\n\n")
            
        res_do_now = parse_summary_findings(summary_file, "Do now (high confidence)")
        assert len(res_do_now) == 1
        assert res_do_now[0] == ("test-slug-1", "Finding Title One")

def test_lookup_metadata():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Test file with literal \n
        fpath = os.path.join(tmpdir, "test-slug.md")
        with open(fpath, "w", encoding="utf-8") as f:
            f.write("# Title\\n**Original URL:** https://example.com\\n**Touches:** TouchComp\\n**Severity:** breaking/security\\n**Что это такое:** This is desc")
            
        meta = lookup_metadata(tmpdir, "test-slug")
        assert meta["url"] == "https://example.com"
        assert meta["touches"] == "TouchComp"
        assert meta["severity"] == "breaking/security"
        assert meta["description"] == "This is desc"
