import asyncio
from src.core import main
from src.utils.terminal_ui import show_welcome_screen

if __name__ == "__main__":
    try:
        show_welcome_screen()
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')