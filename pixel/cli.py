from .brain import PixelBrain


HELP = """Commands:
  /learn TEXT                  Store a memory
  /memory                      List recent memories
  /search TEXT                 Semantic memory search
  /forget ID                   Delete a memory
  /clear                       Clear current conversation
  /session NAME                Switch conversation session
  /model                       Show model/device status
  /help                        Show this help
  /quit                        Exit PIXEL
"""


def main():
    brain = PixelBrain()
    session = "default"
    print("=" * 58)
    print("PIXEL AI 2.0")
    print("Type /help for commands.")
    print("=" * 58)
    while True:
        try:
            text = input(f"\nYou [{session}]: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBye!")
            break
        if not text:
            continue
        if text == "/quit":
            break
        if text == "/help":
            print(HELP)
            continue
        if text == "/memory":
            for item in brain.memories():
                print(f"[{item['id']}] ({item['category']}) {item['text']}")
            continue
        if text.startswith("/search "):
            for item in brain.search(text[8:].strip()):
                print(f"[{item['id']}] score={item['score']:.2f} {item['text']}")
            continue
        if text.startswith("/learn "):
            try:
                print(brain.learn(text[7:].strip()))
            except Exception as exc:
                print("Error:", exc)
            continue
        if text.startswith("/forget "):
            try:
                print(brain.forget(int(text[8:].strip())))
            except ValueError:
                print("Error: memory ID must be a number.")
            continue
        if text == "/clear":
            print(brain.clear_chat(session))
            continue
        if text.startswith("/session "):
            session = text[9:].strip() or "default"
            print(f"Session: {session}")
            continue
        if text == "/model":
            print(brain.health())
            continue
        try:
            print("PIXEL:", brain.ask(text, session)["answer"])
        except Exception as exc:
            print("Error:", exc)


if __name__ == "__main__":
    main()
