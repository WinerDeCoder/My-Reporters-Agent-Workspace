from app.config import get_config


def test_config_yaml_loads():
    cfg = get_config()
    assert cfg.brief.top_repos > 0
    assert cfg.llm.model.startswith("claude-")
