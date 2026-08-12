"""Interactive NEO console.

Plain messages go straight to the chat model. Prefix a message with `@think` to
route it through the ReAct agent, which can search the web and call Wolfram Alpha.
Type `@bye` to quit.
"""

from groq import Groq

from neo.agent import DEFAULT_MODEL, _make_client, agent_loop


class ChatApplication:
    def __init__(self, client: Groq | None = None, model: str = DEFAULT_MODEL):
        self.client = client or _make_client()
        self.model = model
        self.chat_history: list[dict[str, str]] = []

    def run(self):
        while True:
            try:
                user_input = input(">>> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break

            if user_input.lower() == "@bye":
                break

            if not user_input:
                continue

            self.process_input(user_input)

    def process_input(self, user_input: str):
        if "@think" in user_input.lower():
            cleaned_input = user_input.replace("@think", "").strip()
            response = agent_loop(
                query=cleaned_input,
                verbose=True,
                history=self.chat_history,
                client=self.client,
            )
        else:
            # The user turn is appended once, here, so the model sees it in this
            # request; the shared append below covers the agent branch too.
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.chat_history + [{"role": "user", "content": user_input}],
                max_tokens=1500,
                temperature=1.2,
            )
            response = response.choices[0].message.content

        self.chat_history.append({"role": "user", "content": user_input})
        self.chat_history.append({"role": "assistant", "content": response})
        print("NEO:", response)


def main():
    ChatApplication().run()


if __name__ == "__main__":
    main()
