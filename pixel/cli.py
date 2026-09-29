from .brain import PixelBrain

def main():
    brain = PixelBrain()
    print("=" * 50)
    print("PIXEL AI")
    print("Commands: /learn TEXT | /quit")
    print("=" * 50)
    while True:
        try: text = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBye."); break
        if not text: continue
        if text == "/quit": break
        if text.startswith("/learn "):
            try: print("PIXEL:", brain.learn(text[7:].strip())["text"])
            except Exception as exc: print("Error:", exc)
            continue
        try: print("PIXEL:", brain.ask(text)["answer"])
        except Exception as exc: print("Error:", exc)

if __name__ == "__main__": main()
