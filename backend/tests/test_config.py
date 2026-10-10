from app.config import get_config


def test_config_yaml_loads():
    cfg = get_config()
    assert cfg.brief.top_repos > 0
    assert cfg.llm.model
    assert cfg.llm.max_output_tokens > 0


def test_card_prompt_file_exists():
    assert get_config().llm.prompt_path.is_file()
