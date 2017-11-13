import threading
import time
import queue

queue = queue.Queue()

def put_data_in_queue():
    for i in range(100):
        queue.put(i)

class MyThread(threading.Thread):
    def run(self):
        while not queue.empty():
            #sleep_times = queue.get()
            time.sleep(5)
           
            print(queue.get())
            queue.task_done()

def main_function():
    threads_num = 4
    put_data_in_queue()
    while True:

        for i in range(threads_num):
            myThread = MyThread()
            myThread.setDaemon(True)
            myThread.start()
        queue.join()
        time.sleep(3)

main_function()
print('over')
