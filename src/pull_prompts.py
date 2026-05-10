"""
Script para fazer pull de prompts do LangSmith Prompt Hub.
"""

import sys

from dotenv import load_dotenv
from langchain import hub

from utils import check_env_vars, print_section_header, save_yaml

load_dotenv(override=True)

PROMPT_HUB_NAME = "leonanluppi/bug_to_user_story_v1:latest"
OUTPUT_FILE = "prompts/bug_to_user_story_v1.yml"


def pull_prompts_from_langsmith():
    print_section_header("PULL DO PROMPT INICIAL")

    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return False

    try:
        print(f"Puxando prompt do LangSmith Hub: {PROMPT_HUB_NAME}")

        prompt = hub.pull(
            PROMPT_HUB_NAME,
            include_model=False
        )

        messages = getattr(prompt, "messages", [])

        system_prompt = ""
        user_prompt = ""

        for message in messages:
            class_name = message.__class__.__name__

            if hasattr(message, "prompt") and hasattr(message.prompt, "template"):
                template = message.prompt.template

                if class_name == "SystemMessagePromptTemplate":
                    system_prompt = template

                elif class_name == "HumanMessagePromptTemplate":
                    user_prompt = template

        data = {
            "bug_to_user_story_v1": {
                "description": "Prompt inicial de baixa qualidade para conversão de bugs em user stories",
                "version": "v1",
                "source": PROMPT_HUB_NAME,
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "tags": [
                    "bug-analysis",
                    "user-story",
                    "product-management"
                ]
            }
        }

        if save_yaml(data, OUTPUT_FILE):
            print(f"Prompt salvo em: {OUTPUT_FILE}")
            return True

        return False

    except Exception as e:
        print(f"Erro ao fazer pull do prompt: {e}")
        return False


def main():
    success = pull_prompts_from_langsmith()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
