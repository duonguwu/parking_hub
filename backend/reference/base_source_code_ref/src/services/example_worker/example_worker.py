# -*- coding: utf-8 -*-
"""
Example Worker — Standalone background process.

Chay nhu process rieng biet, giao tiep voi API server qua Redis.
Quan ly lifecycle + graceful shutdown.

Pattern nay dung cho:
    - AI inference worker
    - Data processing pipeline
    - Scheduled batch jobs
    - Event consumer (Redis pub/sub)

Usage:
    python -m app.services.example_worker.example_worker
"""
import asyncio
import logging
import signal

from app.core.logging_config import setup_logging
from app.services.shared.redis_client import redis_client

# Optional nhung nen giu cho performance
try:
    import uvloop
    uvloop.install()
except ImportError:
    pass  # uvloop optional, fallback to default event loop

logger = logging.getLogger("example_worker")


class ExampleWorker:
    """
    Infrastructure layer cho background worker service.

    Quan ly:
        - Redis connection
        - Service lifecycle (start -> run -> shutdown)
        - Signal handling (SIGINT, SIGTERM)
        - Graceful shutdown
    """

    def __init__(self):
        self.should_stop = asyncio.Event()
        self.loop: asyncio.AbstractEventLoop | None = None
        # self.some_service = SomeService()  # Initialize your service here

    # ─── Lifecycle ───────────────────────────────────────────────

    async def start(self):
        """Khoi dong worker: connect Redis, init services."""
        logger.info("Example Worker starting...")

        # Connect Redis
        await redis_client.connect()
        logger.info("Redis connected")

        # Initialize your service
        # await self.some_service.start()

        logger.info("Example Worker started successfully")

    async def run(self):
        """
        Main loop cua worker.

        2 pattern chinh:

        Pattern 1: Polling loop (lay data tu Redis, xu ly, publish ket qua)
            while not self.should_stop.is_set():
                data = await redis_client.get_binary("queue:pending")
                if data:
                    result = await self.process(data)
                    await redis_client.publish("results:done", result)
                await asyncio.sleep(0.5)

        Pattern 2: Wait for signal (service co loop rieng)
            await self.should_stop.wait()
        """
        logger.info("Example Worker running — waiting for work...")

        # === Pattern 1: Polling loop ===
        while not self.should_stop.is_set():
            try:
                # 1. Read data from Redis
                # data = await redis_client.get_text("queue:pending")

                # 2. Process data
                # if data:
                #     result = await self.process(data)
                #     await redis_client.publish("results:done", result)
                #     logger.debug(f"Processed: {result}")

                # 3. Sleep between iterations
                await asyncio.sleep(0.5)  # Adjust interval as needed

            except Exception as e:
                logger.error(f"Error in worker loop: {e}", exc_info=True)
                await asyncio.sleep(1)  # Back off on error

        # === Pattern 2: Wait for signal (uncomment if service has own loop) ===
        # await self.should_stop.wait()

    async def shutdown(self):
        """Graceful shutdown: stop services, disconnect Redis."""
        logger.info("Example Worker shutting down...")

        # Stop your service
        # await self.some_service.stop()

        # Disconnect Redis
        await redis_client.disconnect()

        logger.info("Example Worker shutdown complete")

    # ─── Signal handling ─────────────────────────────────────────

    def _handle_signal(self, sig_name: str):
        """Handle OS signals (SIGINT, SIGTERM) cho graceful shutdown."""
        logger.info(f"Received signal {sig_name}, stopping...")
        self.should_stop.set()

    def _register_signals(self):
        """Register signal handlers."""
        for sig in ("SIGINT", "SIGTERM"):
            self.loop.add_signal_handler(
                getattr(signal, sig),
                lambda s=sig: self._handle_signal(s),
            )

    # ─── Entry point ─────────────────────────────────────────────

    async def _main(self):
        """Full lifecycle: start -> run -> shutdown."""
        await self.start()
        await self.run()
        await self.shutdown()

    def start_blocking(self):
        """
        Blocking entrypoint — goi tu CLI.
        Tao event loop moi, register signals, chay _main().
        """
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self._register_signals()

        try:
            self.loop.run_until_complete(self._main())
        finally:
            self.loop.close()


# ─── CLI Entry ───────────────────────────────────────────────────

def main():
    """Entry point khi chay: python -m app.services.example_worker.example_worker"""
    setup_logging(
        service="example_worker",
        console_level=logging.DEBUG,
        file_level=logging.DEBUG,
    )

    logger.info("Example Worker process starting...")

    worker = ExampleWorker()
    worker.start_blocking()


if __name__ == "__main__":
    main()
