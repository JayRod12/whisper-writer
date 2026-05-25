import subprocess
import os
import signal
import time
from pynput.keyboard import Controller as PynputController

from utils import ConfigManager

def _ydotool_socket():
    uid = os.getuid()
    return os.environ.get('YDOTOOL_SOCKET', f'/run/user/{uid}/.ydotool_socket')

def run_command_or_exit_on_failure(command):
    """
    Run a shell command and exit if it fails.

    Args:
        command (list): The command to run as a list of strings.
    """
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        exit(1)

class InputSimulator:
    """
    A class to simulate keyboard input using various methods.
    """

    def __init__(self):
        """
        Initialize the InputSimulator with the specified configuration.
        """
        self.input_method = ConfigManager.get_config_value('post_processing', 'input_method')
        self.dotool_process = None

        self.ydotoold_process = None
        if self.input_method == 'pynput':
            self.keyboard = PynputController()
        elif self.input_method == 'ydotool':
            self._ensure_ydotoold()
        elif self.input_method == 'dotool':
            self._initialize_dotool()
        # wtype needs no initialization

    def _ensure_ydotoold(self):
        socket = _ydotool_socket()
        if not os.path.exists(socket):
            self.ydotoold_process = subprocess.Popen(
                ['ydotoold', '--socket-path', socket],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            )
            time.sleep(0.5)

    def _initialize_dotool(self):
        """
        Initialize the dotool process for input simulation.
        """
        self.dotool_process = subprocess.Popen("dotool", stdin=subprocess.PIPE, text=True)
        assert self.dotool_process.stdin is not None

    def _terminate_dotool(self):
        """
        Terminate the dotool process if it's running.
        """
        if self.dotool_process:
            os.kill(self.dotool_process.pid, signal.SIGINT)
            self.dotool_process = None

    def typewrite(self, text):
        """
        Simulate typing the given text with the specified interval between keystrokes.

        Args:
            text (str): The text to type.
        """
        interval = ConfigManager.get_config_value('post_processing', 'writing_key_press_delay')
        if self.input_method == 'pynput':
            self._typewrite_pynput(text, interval)
        elif self.input_method == 'ydotool':
            self._typewrite_ydotool(text, interval)
        elif self.input_method == 'dotool':
            self._typewrite_dotool(text, interval)
        elif self.input_method == 'wtype':
            self._typewrite_wtype(text, interval)

    def _typewrite_pynput(self, text, interval):
        """
        Simulate typing using pynput.

        Args:
            text (str): The text to type.
            interval (float): The interval between keystrokes in seconds.
        """
        for char in text:
            self.keyboard.press(char)
            self.keyboard.release(char)
            time.sleep(interval)

    def _typewrite_ydotool(self, text, interval):
        """
        Simulate typing using ydotool.

        Args:
            text (str): The text to type.
            interval (float): The interval between keystrokes in seconds.
        """
        cmd = "ydotool"
        run_command_or_exit_on_failure([
            cmd,
            "type",
            "--key-delay",
            str(int(interval * 1000)),
            "--",
            text,
        ])

    def _typewrite_wtype(self, text, interval):
        run_command_or_exit_on_failure([
            'wtype',
            '-d', str(int(interval * 1000)),
            '--', text,
        ])

    def _typewrite_dotool(self, text, interval):
        """
        Simulate typing using dotool.

        Args:
            text (str): The text to type.
            interval (float): The interval between keystrokes in seconds.
        """
        assert self.dotool_process and self.dotool_process.stdin
        self.dotool_process.stdin.write(f"typedelay {interval * 1000}\n")
        self.dotool_process.stdin.write(f"type {text}\n")
        self.dotool_process.stdin.flush()

    def cleanup(self):
        if self.ydotoold_process:
            self.ydotoold_process.terminate()
            self.ydotoold_process = None
        if self.input_method == 'dotool':
            self._terminate_dotool()
