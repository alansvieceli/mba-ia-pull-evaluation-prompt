"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)
"""

import sys

from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate

from utils import (
    check_env_vars,
    load_yaml,
    print_section_header,
)

load_dotenv(override=True)

PROMPT_FILE = "prompts/bug_to_user_story_v2.yml"


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica do prompt.
    """

    errors = []

    required_fields = [
        "system_prompt",
        "user_prompt",
        "description",
        "techniques",
        "tags",
    ]

    for field in required_fields:
        if field not in prompt_data:
            errors.append(
                f"Campo obrigatório ausente: {field}"
            )

    if "techniques" in prompt_data:

        if not isinstance(
            prompt_data["techniques"],
            list
        ):
            errors.append(
                "Campo 'techniques' deve ser uma lista"
            )

        elif len(prompt_data["techniques"]) < 2:
            errors.append(
                "Prompt deve possuir pelo menos 2 técnicas"
            )

    if "system_prompt" in prompt_data:
        if len(
            prompt_data["system_prompt"].strip()
        ) == 0:
            errors.append("System prompt vazio")

    if "user_prompt" in prompt_data:
        if len(
            prompt_data["user_prompt"].strip()
        ) == 0:
            errors.append("User prompt vazio")

    return len(errors) == 0, errors


def push_prompt_to_langsmith(
    prompt_name: str,
    prompt_data: dict
) -> bool:
    """
    Faz push do prompt para o LangSmith Hub.
    """

    try:

        print(
            f"\nPublicando prompt: {prompt_name}"
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    prompt_data["system_prompt"]
                ),
                (
                    "human",
                    prompt_data["user_prompt"]
                ),
            ]
        )

        full_prompt_name = (
            "bug_to_user_story_v2"
        )

        try:
            hub.push(
                full_prompt_name,
                prompt,
                description=prompt_data.get(
                    "description",
                    ""
                ),
            )

        except TypeError:
            # fallback para versões antigas
            hub.push(
                full_prompt_name,
                prompt,
            )

        print(
            "\nPrompt publicado com sucesso."
        )

        print(
            f"Nome: {full_prompt_name}"
        )

        print(
            f"Descrição: "
            f"{prompt_data.get('description', '')}"
        )

        print(
            "Técnicas: "
            + ", ".join(
                prompt_data.get(
                    "techniques",
                    []
                )
            )
        )

        print(
            "Tags: "
            + ", ".join(
                prompt_data.get(
                    "tags",
                    []
                )
            )
        )

        return True

    except Exception as e:

        print(
            f"Erro ao publicar prompt: {e}"
        )

        return False


def main():
    """
    Função principal.
    """

    print_section_header(
        "PUSH DOS PROMPTS OTIMIZADOS"
    )

    if not check_env_vars(
        ["LANGSMITH_API_KEY"]
    ):
        return 1

    try:

        prompts = load_yaml(
            PROMPT_FILE
        )

    except Exception as e:

        print(
            f"Erro ao carregar arquivo YAML: {e}"
        )

        return 1

    if not prompts:

        print(
            "Nenhum prompt encontrado."
        )

        return 1

    success_count = 0

    for (
        prompt_name,
        prompt_data
    ) in prompts.items():

        print(
            f"\nValidando: {prompt_name}"
        )

        is_valid, errors = validate_prompt(
            prompt_data
        )

        if not is_valid:

            print(
                "\nPrompt inválido:"
            )

            for error in errors:
                print(f"- {error}")

            continue

        print("Prompt válido.")

        success = push_prompt_to_langsmith(
            prompt_name,
            prompt_data
        )

        if success:
            success_count += 1

    print_section_header(
        "RESULTADO FINAL"
    )

    print(
        f"Prompts publicados com sucesso: "
        f"{success_count}"
    )

    return (
        0
        if success_count > 0
        else 1
    )


if __name__ == "__main__":
    sys.exit(main())
