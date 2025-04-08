from audio_utils import voice_input
from openai_utils import generate_command_from_prompt
from webserver import start_webserver
from command_utils import broadcast_command, calculate_delay
from dialog_loop import conversation_loop
from conversation_manager import conversation_manager

# --- Main Block: Webserver im Hintergrund ---
if __name__ == '__main__':
    start_webserver()
    conversation_manager()
    cherrypy.engine.stop()
