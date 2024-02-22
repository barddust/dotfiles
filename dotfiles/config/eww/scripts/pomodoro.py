#!/usr/bin/python
#
## Elivsh 不好做并发
import asyncio
import orjson

COUNT = 4
TIME = 60 * 25
BREAK = 60 * 5
REST = 60 * 15

# COUNT = 4
# TIME = 3
# BREAK = 1
# REST = 2

class Worker:
    def __init__(
            self,
            event: asyncio.Event,
            count: int,
            time: int,
            break_time: int,
            rest_time: int
    ):
        self._running = event
        self._time = time
        self._count = count
        self._rest_time = rest_time
        self._break_time = break_time
        self.reset()

    def show_time(self):
        h = int(self._current_timer/60)
        s = self._current_timer % 60
        ret = {"count": self._current_count, "time": "%02d:%02d" % (h,s), "working": self._working}
        print(orjson.dumps(ret).decode(), flush=True)

    def reset(self):
        self._current_count = 0
        self._current_timer = 0
        self._working = False
        self.show_time()
        self._current_timer = -1
        

    def is_done(self):
        return not self._running.is_set() and \
            self._current_count >= self._count

    async def run(self):
        while True:
            await self._running.wait()
            is_last = self._count == self._current_count
            if self._current_timer < 0:
                if self._working:
                    self._current_timer = self._rest_time if is_last\
                        else self._break_time
                    self._working = False
                else:
                    if is_last:
                        self._running.clear()
                    else:
                        self._current_count += 1
                        self._current_timer = self._time
                        self._working = True
            else:
                self.show_time()
                self._current_timer -= 1
                await asyncio.sleep(1)

async def counter(notify: asyncio.Event) -> None:
    count = 0
    timer = -1
    working = False
    # print("counter initialized")
    while True:
        await notify.wait()
        is_last = count == COUNT
        if timer < 0:
            if working:
                timer = REST if is_last else BREAK
                working = False            
            else:
                if is_last:
                    break
                else:
                    count += 1
                    timer = TIME
                working = True
        else:
            h = int(timer/60)
            s = timer % 60
            ret = {"count": count, "time": "%02d:%02d" % (h,s), "working": working}
            print(orjson.dumps(ret).decode(), flush=True)
            # print(working, count, timer)
            timer -= 1
            await asyncio.sleep(1)
    
    
class Server:
    def __init__(self):
        self.running = asyncio.Event()
        self.worker = Worker(
            self.running,
            COUNT,
            TIME,
            BREAK,
            REST
        )

    def start(self):
        if self.worker.is_done():
            self.reset()
        if not self.running.is_set():
            self.running.set()

    def stop(self):
        self.running.clear()

    def reset(self):
        self.running.clear()
        self.worker.reset()

    def toggle(self):
        if self.running.is_set():
            self.stop()
        else:
            self.start()

    async def handle(
            self,
            reader: asyncio.StreamReader,
            writer: asyncio.StreamWriter
    ):
        data = await reader.read()
        message = data.decode()
        # print("Message Received: %s" % message)
        func = getattr(self, message)
        func()
        writer.close()
        await writer.wait_closed()

    async def run(self):
        server = await asyncio.start_unix_server(
            self.handle,
            "/tmp/pomodoro.socket"
        )
        async with server:
            asyncio.create_task(self.worker.run())
            await server.serve_forever()

   
async def client_send(cmd: str, *args):
    reader, writer = await asyncio.open_unix_connection(
        "/tmp/pomodoro.socket"
    )
    message = cmd.encode()
    writer.write(message)
    await writer.drain()
    writer.close()
    await writer.wait_closed()


if __name__ == "__main__":
    import sys
    arg = sys.argv[1]
    if arg == "server":
        server = Server()
        asyncio.run(server.run())

    elif arg == "client":
        asyncio.run(client_send(sys.argv[2], *sys.argv[3:]))

    elif arg == "test":
        async def starter(notify, task):            
            await asyncio.sleep(1)
            notify.set()
            print("notify set.")
            await asyncio.sleep(2)
            notify.clear()
            print("notify cleared.")
            await asyncio.sleep(2)
            notify.set()
            print("notify resume.")
            await asyncio.sleep(2)
            task.cancel()
            print("task canceled.")
            print(task.done())
            

        async def main():
            notify = asyncio.Event()
            notify.clear()
            try:
                task = asyncio.create_task(counter(notify))
                st = asyncio.create_task(starter(notify,task))
                await task
                await st
            except asyncio.CancelledError:
                pass
        asyncio.run(main())
