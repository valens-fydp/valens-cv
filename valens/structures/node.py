from valens.structures.stream import InputStream, OutputStream
from abc import ABC, abstractmethod
import time
from torch.multiprocessing import Process

class Node(ABC, Process):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.input_streams = {}
        self.output_streams = {}
        self.stop_event = None
        self.max_fps = None
        self.total_time = 0
        self.iterations = 0

    def set_stop_event(self, stop_event):
        self.stop_event = stop_event
    
    def set_max_fps(self, max_fps):
        self.max_fps = max_fps
        
    def average_fps(self):
        return self.iterations / self.total_time

    def run(self):
        print("Running", self.name)
        for _, stream in self.input_streams.items(): stream.start()
        for _, stream in self.output_streams.items(): stream.start()
        self.prepare()
        if self.max_fps is not None:
            period = 1 / self.max_fps

        while self.stop_event is None or not self.stop_event.is_set():
            start = time.time()
            self.process()
            end = time.time()
            process_time = end - start
            if self.max_fps is not None:
                if process_time < period:
                    timeout = period - process_time
                    time.sleep(timeout)
                    process_time += timeout

            self.total_time += process_time
            self.iterations += 1
        print("Stopped", self.name, "with average fps of", self.average_fps())

    def prepare(self):
        pass

    @abstractmethod
    def process(self):
        pass
