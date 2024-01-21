import asyncio
import unittest, warnings
from unittest import skipIf

from ..logger import *

class TestLogger(unittest.TestCase):
    
    # ◼︎ Change this to bypass some test cases
    TEST_SYNC              = True
    TEST_ASYNC             = True
    
    def setUp(self):
        # warnings.simplefilter("ignore", category=ResourceWarning)
        pass
    
    # =========================================================================
    # Test cases
    # =========================================================================
    @skipIf(not TEST_SYNC, "")
    def test_SYNC(self):
        LOGGER = Logger(log_level=LogLevel.ALL, logfile_path="./logger_sync.log", overwrite=True)

        LOGGER.info("Info message.")
        LOGGER.warn("Warning message.")
        LOGGER.debug("Debugging message.")
        LOGGER.error("Error message.")
    
    
    @skipIf(not TEST_ASYNC, "")
    def test_ASYNC(self):
        LOGGER = Logger(log_level=LogLevel.ALL, logfile_path="./logger_async.log", overwrite=True)
        asyncio.run(LOGGER.info("Async Info message.", is_async=True))
        asyncio.run(LOGGER.warn("Async Warning message.", is_async=True))
        asyncio.run(LOGGER.debug("Async Debugging message.", is_async=True))
        asyncio.run(LOGGER.error("Async Error message.", is_async=True))
        
        async def test():
            await LOGGER.info("(Use await) Async Info message.", is_async=True)
            await LOGGER.warn("(Use await) Async Warning message.", is_async=True)
            await LOGGER.debug("(Use await) Async Debugging message.", is_async=True)
            await LOGGER.error("(Use await) Async Error message.", is_async=True)

        asyncio.run(test())

        

if __name__ == '__main__':
    unittest.main()
