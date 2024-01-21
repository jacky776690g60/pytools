import threading, math, time, random
import unittest, warnings
from unittest import skipIf

from ..progressbar import *

class NoDotTestResult(unittest.TextTestResult):
    def addSuccess(self, test):
        pass  # Override to do nothing on success

class NoDotTestRunner(unittest.TextTestRunner):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, resultclass=NoDotTestResult)

class TestProgress(unittest.TestCase):
    
    # ◼︎ Change this to bypass some test cases
    TEST_SYNC              = True
    TEST_BKPT              = True
    TEST_ASYNC             = True
    
    def setUp(self):
        # warnings.simplefilter("ignore", category=ResourceWarning)
        pass
    
    # =========================================================================
    # Test cases
    # =========================================================================
    @skipIf(not TEST_SYNC, "")
    def test_SYNC(self):
        def on_completion():
            print("Process completed!")

        numbers = [x * 5 for x in range(2000, 2399)]

        results = []
        pbar = ProgressBar(len(numbers), completion_callback=on_completion)
        pbar.use_interval_time = True

        for i, x in enumerate(numbers):
            results.append(math.factorial(x))
            pbar.draw(i, pre_str=i)


    @skipIf(not TEST_BKPT, "")
    def test_BKPT(self):
        def on_completion():
            print("Process completed!")

        numbers = [x * 5 for x in range(2000, 2300)]

        results = []
        pbar = ProgressBar(len(numbers), completion_callback=on_completion)
        pbar.perc_bkpt = 10
        pbar.use_interval_time = True

        for i, x in enumerate(numbers):
            results.append(math.factorial(x))
            pbar.draw(i, pre_str=i)
        
    
    @skipIf(not TEST_ASYNC, "")
    def test_ASYNC(self):
        def task(multi_progress_bar, start, end, bar_index):
            for i in range(start, end):
                time.sleep(random.uniform(0.01, 0.05)) # Simulating work
                multi_progress_bar.update(bar_index, i - start)

        num_threads = 3   # Number of threads to create
        total_work  = 100  # Total units of work per thread

        multi_progress_bar = MultiLineProgressBar(num_threads, total_work)

        # Clear screen and move cursor to top
        print("\033[2J\033[H", end="")

        # Creating and starting threads
        threads = []
        for n in range(num_threads):
            thread = threading.Thread(target=task, args=(multi_progress_bar, 0, total_work, n))
            threads.append(thread)
            thread.start()

        # Waiting for all threads to complete
        for thread in threads:
            thread.join()
        
        print("\nAll tasks completed.")

if __name__ == '__main__':
    unittest.main(testRunner=NoDotTestRunner())

