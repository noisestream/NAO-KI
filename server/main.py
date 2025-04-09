from webserver import start_webserver, stop_webserver
from conversation_manager import conversation_manager

if __name__ == '__main__':
    start_webserver()
    conversation_manager()    
    stop_webserver()
