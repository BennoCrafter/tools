"""
Text OpenAi ollama integration by clarifying if products include pineapple
"""

from typing import Optional

from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)
model = "llama3.2"


def predict_pineapple(dish: str) -> Optional[bool]:
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Think about the ingredients usually found in the given dish. "
                        "Determine if pineapple is commonly included. "
                        "Reply only with '1' if yes, or '0' if no — no words, no punctuation, just the number."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Does the dish '{dish}' contain pineapple?",
                },
            ],
        )

        reply = response.choices[0].message.content.strip()

        return True if "1" in reply else False if "2" in reply else None

    except Exception as e:
        print(f"❌ Error processing '{dish}': {e}")
        return None


if __name__ == "__main__":
    dishes = [
        "Fruit Salad",
        # "Pizza",
        "Hamburger",
        "Tacos",
        "Pizza Hawaii",
        "Pina Colada",
        "chicken salad",
    ]
    import colorama
    from colorama import Fore, Style

    colorama.init()

    for dish in dishes:
        result = predict_pineapple(dish)
        if result is True:
            print(
                f"Does '{dish}' contain pineapple? → {Fore.GREEN}{result}{Style.RESET_ALL}"
            )
        elif result is False:
            print(
                f"Does '{dish}' contain pineapple? → {Fore.RED}{result}{Style.RESET_ALL}"
            )
        else:
            print(
                f"Does '{dish}' contain pineapple? → {Fore.YELLOW}{result}{Style.RESET_ALL}"
            )
