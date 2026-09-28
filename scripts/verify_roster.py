"""Independent real smoke runs; one failing runtime cannot hide the rest."""
import asyncio
import sys
from scripts.verify_models import run

async def main():
    for model in sys.argv[1:]:
        try:
            await run([model])
        except Exception as error:
            print(model, type(error).__name__, str(error), flush=True)

if __name__ == '__main__':
    asyncio.run(main())
