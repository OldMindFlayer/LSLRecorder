# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 09:38:51 2020

@author: dblok
"""
from lsl_stream_listener import LSL_Listener
from config import config_init
import time
from queue import Queue
#from pathlib import Path
from sys import argv
from threading import Thread

def start():
    
    # create config dict
    config = config_init(argv)
    q_from_main_to_listener = Queue()
    
    # Debug mode uses LSL_Generator for debuging
    if config['general'].getboolean('debug_mode'):
        print('Debug Mode!!!')
        debug_time = config['general'].getint('debug_time')
        lsl_stream_generator_path = config['paths']['lsl_stream_generator_path']
        import importlib.util
        spec = importlib.util.spec_from_file_location("lsl_stream_generator", lsl_stream_generator_path)
        lsl_stream_generator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lsl_stream_generator)
        lsl_stream_debug = lsl_stream_generator.LSL_Generator(debug_time, 69, 2048, q_from_main_to_listener)
        lsl_stream_debug.start()
        time.sleep(2)
    
    
    # Queue is used to pass arguments from display thread to main thread (to LSL_Listener)
    q_from_main_to_listener.put(('lsl_stream_listener_state', True))
    q_from_main_to_listener.put(('patient_state', 1))
    
    lsl_listener = LSL_Listener(config, 2048, q_from_main_to_listener)
    time.sleep(0.5)
    record_time = 20
    
    # initialise thread for display
    thread = Thread(target=update, args=(q_from_main_to_listener, record_time))
    thread.start()
    lsl_listener.record_using_buffer()


def update(q_from_main_to_listener, record_time):
    time.sleep(record_time)
    q_from_main_to_listener.put((('lsl_stream_listener_state', False)))


if __name__ == '__main__':
    start()