from app.rag_pipeline import RAGPipeline


class Chatbot:
    """Provide an interactive command-line chatbot."""

    EXIT_COMMANDS = {
        "exit",
        "quit",
        "q",
    }

    def __init__(self) -> None:
        self.pipeline = RAGPipeline()

    def start(self) -> None:
        """Start the interactive chat session."""

        print("=" * 80)
        print("LOCAL RAG CHATBOT")
        print("=" * 80)
        print("Type 'exit' to end the conversation.\n")

        try:
            while True:
                question = input("You: ").strip()

                if not question:
                    print("Assistant: Please enter a question.\n")
                    continue

                if question.lower() in self.EXIT_COMMANDS:
                    print("\nAssistant: Goodbye!")
                    break

                response = self.pipeline.ask(question)

                print("\nAssistant:")
                print(response["answer"])
                print()

        finally:
            self.pipeline.close()


def main() -> None:
    """Run the chatbot."""

    chatbot = Chatbot()
    chatbot.start()


if __name__ == "__main__":
    main()