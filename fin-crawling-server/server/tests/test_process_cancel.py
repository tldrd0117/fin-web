import asyncio
from concurrent.futures import ProcessPoolExecutor
import traceback


async def retried(data: str) -> None:
    try:
        await asyncio.sleep(3)
        print(data)
    except Exception as e:
        print(e)


async def runTest(loop: asyncio.AbstractEventLoop) -> None:
    pool = ProcessPoolExecutor()
    try:
        task = loop.run_in_executor(pool, retried, "runTest")
        await task
    except asyncio.CancelledError:
        print(traceback.format_exc())
        print("cancel")
    except Exception as e:
        print("error!")
        print(e)
    finally:
        pool.shutdown()


# pytest -s test_process_cancel.py
def test() -> None:
    print("run test")
    loop = asyncio.get_event_loop()
    loop.create_task(runTest(loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.close()