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
            time.sleep(3)
           
            #print(queue.get())
            myCrawler = MyCrawler("https://www.aitaotu.com/tag/chizuzhe.html")
            myCrawler.test1()
            queue.task_done()

class MyCrawler:
    def __init__(self,seeds):
        print(seeds)
        
    def main_function(self):
        threads_num = 4
        put_data_in_queue()
        while True:
            for i in range(threads_num):
                myThread = MyThread()
                myThread.setDaemon(True)
                myThread.start()
            queue.join()
            time.sleep(3)
            
    def test1(self):
        print("1112121")

if __name__=="__main__":
    myCrawler = MyCrawler("https://www.aitaotu.com/tag/chizuzhe.html")
    myCrawler.main_function()
    print('over')
