import json
from pathlib import Path

import pytest

from chekhov import checks, impact, metrics
from chekhov.checks.rules import parse_chapters
from chekhov.cli import main
from chekhov.manuscript import Manuscript, split_sentences
from chekhov.model import Graph

FIX = Path(__file__).parent / "fixtures"


@pytest.fixture
def graph():
    return Graph.load(FIX / "graph.json")


@pytest.fixture
def ms():
    return Manuscript.load(FIX / "story.md")


def codes(issues, level=None):
    return [i.code for i in issues if level is None or i.level == level]


def test_manuscript_splits_chapters(ms):
    assert ms.chapter_numbers() == [1, 2, 3]
    assert ms.chapters[0] == ["The Lantern"]
    assert "She does not light it." in ms.text(1)


def test_split_sentences():
    assert split_sentences('He said "no." Then he left. Why?') == ['He said "no."', "Then he left.", "Why?"]


def test_clean_manuscript_has_no_errors(graph, ms):
    issues = checks.run_all(graph, ms)
    assert codes(issues, "error") == []
    # the question in chapter 1 is a warning for a person to judge
    assert "I-1" in codes(issues, "warning")


def test_changed_and_missing_evidence(graph):
    edited = Manuscript([
        "[1] Spring", "A girl hangs a lantern. She does not light the lantern.",
        "[2] Summer", "Nothing happens.",
        "[3] Winter", "I light it for the first time.",
    ])
    issues = checks.run_all(graph, edited)
    by_node = {i.node: i.code for i in issues if i.node}
    assert by_node["E1"] == "evidence-changed"
    assert by_node["E2"] == "evidence-missing"


def test_similarity_separates_edits_from_strangers():
    from chekhov.checks.evidence import similarity
    assert similarity("발소리도 멀어지지 않는다.", "발소리는 멀어지지 않는다.") >= 0.7      # a real edit
    assert similarity("할아버지가 그러셨다고 한다.",
                      "아버지가 신문을 내려놓고 이름을 부르시면 그제야 울면서 한 숟가락을 삼킨다.") < 0.7  # unrelated
    assert similarity("나는 숨을 고르게 쉰다.", "나는 밥을 잘 먹고 가리는 것도 없다.") < 0.7


def test_exclusions_skip_cut_scenes(graph):
    edited = Manuscript(["[1] Spring", "She does not light it.", "[2] Summer", "x", "[3] Winter",
                         "I light it for the first time."])
    issues = checks.run_all(graph, edited, excluded={"E2"})
    assert "evidence-missing" not in codes(issues)
    assert "excluded" in codes(issues)


def test_impact_reports_partner_left_behind(graph):
    broken = impact.broken_links(graph, {"E2"})
    kept = sorted(b.kept for b in broken)
    assert kept == ["E1", "E3"]


def test_setup_after_payoff(graph):
    graph.edges.append({"source": "E3", "relation": "SETS_UP", "target": "E1"})
    assert "setup-after-payoff" in codes(checks.structure.setup_order(graph))
    graph.edges[-1]["reverse"] = True
    assert checks.structure.setup_order(graph) == []


def test_dangling_edge_and_ungrounded(graph):
    graph.edges.append({"source": "E1", "relation": "SETS_UP", "target": "NOPE"})
    graph.nodes["T9"] = {"id": "T9", "type": "Theme", "label": "orphan theme"}
    issues = graph.validate() + checks.structure.coverage(graph)
    assert "dangling-edge" in codes(issues)
    assert "ungrounded" in codes(issues)


def test_forbidden_terms(graph):
    edited = Manuscript(["[1] Spring", "Suddenly, suddenly she does not light it."])
    assert "I-2" in codes(checks.rules.check_invariants(graph, edited), "error")


def test_parse_chapters():
    assert parse_chapters("1-3,5", [1, 2, 3, 4, 5, 6]) == [1, 2, 3, 5]
    assert parse_chapters(None, [1, 2]) == [1, 2]


def test_korean_pack():
    ms = Manuscript(["[1] 봄", "나는 세 시에 일어났다. 방은 삼 평이다. 그는 슬프다고 했다.", "\"좋다.\""])
    issues = checks.rules.check_packs(Graph({"meta": {}}), ms, ["ko"])
    msgs = " ".join(i.message for i in issues)
    assert "세 시" in msgs and "삼 평" in msgs and "슬프" in msgs
    assert not any("좋다" in i.message for i in issues if i.code == "ko/emotion-words")  # dialogue is skipped


def test_count_and_audit(ms):
    c = metrics.count(ms)
    assert c.chars_with_spaces > 0 and c.manuscript_pages_by_lines >= c.manuscript_pages_by_chars
    assert [r.chapter for r in metrics.audit(ms)] == [1, 2, 3]


def test_cli_check_exit_code(capsys):
    assert main(["check", str(FIX / "graph.json"), str(FIX / "story.md"), "--json"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert any(i["code"] == "I-1" for i in out)


def test_cli_init(tmp_path):
    assert main(["init", str(tmp_path / "work"), "--title", "Test", "--language", "en"]) == 0
    g = json.loads((tmp_path / "work" / "graph.json").read_text(encoding="utf-8"))
    assert g["meta"]["title"] == "Test"
    assert (tmp_path / "work" / "AGENT_RULES.md").exists()


def _project(tmp_path):
    import shutil
    shutil.copy(FIX / "graph.json", tmp_path / "graph.json")
    shutil.copy(FIX / "story.md", tmp_path / "story.md")
    (tmp_path / ".chekhov.json").write_text(
        json.dumps({"graph": "graph.json", "manuscript": "story.md"}), encoding="utf-8")
    return tmp_path


def test_check_reads_config(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(_project(tmp_path))
    assert main(["check", "--json"]) == 0


def test_hook_runs_only_on_change_and_blocks_on_errors(tmp_path, capsys):
    from chekhov import hook
    root = _project(tmp_path)
    event = json.dumps({"cwd": str(root), "tool_name": "Edit"})
    assert hook.run(event) == 0                      # clean
    story = root / "story.md"
    story.write_text(story.read_text(encoding="utf-8").replace("She does not light it.", "She lights it."),
                     encoding="utf-8")
    assert hook.run(event) == 2                      # evidence for E1 is gone
    assert "E1" in capsys.readouterr().err
    assert hook.run(event) == 0                      # nothing changed since the last run


def test_hook_without_project_is_silent(tmp_path):
    from chekhov import hook
    assert hook.run(json.dumps({"cwd": str(tmp_path)})) == 0
