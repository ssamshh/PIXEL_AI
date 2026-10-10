from .core.brain import PixelBrain

def main():
    brain=PixelBrain()
    session="default"
    print("PIXEL AI 3.0 — /help for commands, /quit to exit")
    while True:
        try: line=input(f"PIXEL[{session}]> ").strip()
        except (EOFError,KeyboardInterrupt): print(); break
        if not line: continue
        if line in {"/quit","/exit"}: break
        if line=="/help":
            print("/learn TEXT | /memory | /search TEXT | /forget ID | /session NAME | /clear | /tools | /model | /quit"); continue
        if line.startswith("/learn "):
            print(brain.learn(line[7:])); continue
        if line=="/memory": 
            [print(f"#{m['id']} [{m['category']}] {m['text']}") for m in brain.memories()]; continue
        if line.startswith("/search "):
            [print(m) for m in brain.search_memory(line[8:])]; continue
        if line.startswith("/forget "):
            try: print(brain.forget(int(line[8:])))
            except ValueError: print("ID must be a number.")
            continue
        if line.startswith("/session "):
            session=line[9:].strip() or "default"; print("Session:",session); continue
        if line=="/clear": print(brain.clear_chat(session)); continue
        if line=="/tools": print(brain.tools.list_tools()); continue
        if line=="/model": print(brain.model.info()); continue
        try: print(brain.ask(line,session)["answer"])
        except Exception as exc: print("Error:",exc)

if __name__=="__main__": main()
