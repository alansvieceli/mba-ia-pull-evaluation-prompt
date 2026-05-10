"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"
PROMPT_NAME = "bug_to_user_story_v2"

def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

class TestPrompts:
    @pytest.fixture
    def prompt_data(self):
        """Retorna os dados do prompt principal."""
        prompts = load_prompts(PROMPT_FILE)
        assert PROMPT_NAME in prompts
        return prompts[PROMPT_NAME]

    def test_prompt_has_system_prompt(self):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        prompt_data = load_prompts(PROMPT_FILE)[PROMPT_NAME]

        assert "system_prompt" in prompt_data
        assert prompt_data["system_prompt"].strip()

    def test_prompt_has_role_definition(self, prompt_data):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        system_prompt = prompt_data["system_prompt"]

        assert "Você é" in system_prompt
        assert "Product Manager" in system_prompt

    def test_prompt_mentions_format(self, prompt_data):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        prompt_text = (
            prompt_data.get("system_prompt", "")
            + "\n"
            + prompt_data.get("user_prompt", "")
        )

        assert "Markdown" in prompt_text
        assert "Como [tipo de usuário], eu quero [objetivo], para que [benefício]." in prompt_text

    def test_prompt_has_few_shot_examples(self, prompt_data):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        system_prompt = prompt_data["system_prompt"]

        assert "FEW-SHOT LEARNING" in system_prompt
        assert "Entrada:" in system_prompt
        assert "Saída:" in system_prompt

    def test_prompt_no_todos(self, prompt_data):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        prompt_text = yaml.safe_dump(prompt_data, allow_unicode=True)

        assert "[TODO]" not in prompt_text
        assert "TODO" not in prompt_text

    def test_minimum_techniques(self, prompt_data):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = prompt_data.get("techniques", [])

        assert isinstance(techniques, list)
        assert len(techniques) >= 2

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
