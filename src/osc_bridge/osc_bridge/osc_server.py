import subprocess
import threading
#import asyncio

import rclpy
from rclpy.node import Node

# Messages, Services, Actions
from std_msgs.msg import String, Header
from irobot_create_msgs.msg import AudioNoteVector, AudioNote
from builtin_interfaces.msg import Duration

# OSC
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import AsyncIOOSCUDPServer, BlockingOSCUDPServer
from pythonosc.udp_client import SimpleUDPClient

# # Start the subprocess with stdout and stderr piped
# process = subprocess.Popen(command_string, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)

# # Read from the process output in real-time
# for line in process.stdout:
#     print(line, end='')

# # Close the streams and wait for the process to exit
# process.stdout.close()
# process.stderr.close()
# process.wait()


# def filter_handler(address, *args):
#     print(f"{address}: {args}")

ip = "127.0.0.1"
port = 1337


# def filter_handler(address, *args):
#     print(f"{address}: {args}")

# async def loop():
#     """Example main loop that only runs for 10 iterations before finishing"""
#     for i in range(10):
#         print(f"Loop {i}")
#         await asyncio.sleep(1)

class PibotServer(Node):
    def __init__(self, ip: str, port: int):
        super().__init__('pibot_server')
        # OSC stuff
        # Pihub
        self.pihub_ip = "192.168.0.204"
        self.pihub_port = 1337
        self.pihub_client = SimpleUDPClient(self.pihub_ip, self.pihub_port)
        # Pibot server
        self.ip = ip
        self.port = port
        self.dispatcher = Dispatcher()
        self.dispatcher.map("/test/*", self.print_msg)
        self.dispatcher.map("/play-note", self.play_single_note)
        self.dispatcher.set_default_handler(self.default_handler)
        # self.osc_server = AsyncIOOSCUDPServer((self.ip, self.port), self.dispatcher, asyncio.get_event_loop())
        # transport, protocol = await server.create_serve_endpoint()
        self.server = BlockingOSCUDPServer((self.ip, self.port), self.dispatcher)
        self.osc_thread = threading.Thread(target=self.server.serve_forever)
        self.osc_thread.start()

        self.note_publishers = [self.create_publisher(AudioNoteVector, f'/pibot{bot_ID}/cmd_audio', 10) for bot_ID in [1, 2, 3]]
        # Log
        print(f">>> OSC server thread started, listening on port {self.port}")
        self.play_single_note(None, 1, 250)
        self.send_pihub("/info", "I'm live!")

    def send_pihub(self, addr, msg):
        self.pihub_client.send_message(addr, msg)

    def play_single_note(self, address, *args):
        (bot_id, freq) = args
        print(f"Received BotID: {bot_id}, freq: {freq}")
        duration = Duration(sec=1, nanosec=0)
        note = AudioNote(frequency=freq, max_runtime=duration)
        notes = [note]
        msg = AudioNoteVector(notes=notes, append=False)
        self.note_publishers[bot_id].publish(msg)
        # cmd_preamble = "ros2 topic pub --once /cmd_audio irobot_create_msgs/msg/AudioNoteVector"
        # note_str = f"{{frequency: {note}}}"
        # cmd_notes = f"{{append: false, notes: [{note_str}]}}"
        # cmd = f"{cmd_preamble} {cmd_notes}"
        # print(f"Running command str:\n{cmd}")
        # result = subprocess.check_output(cmd, shell=True, executable="/bin/bash", stderr=subprocess.STDOUT)
        # print(f"It was run! Result:\n{result}\n")

    def navigate_to_pos(self, x, y):
        msg = None
        publisher.publish(msg)

        #ros2 topic pub --once /cmd_audio irobot_create_msgs/msg/AudioNoteVector "{append: false, notes: [{frequency: 100, max_runtime: {sec: 1,nanosec: 0}}, {frequency: 50, max_runtime: {sec: 1,nanosec: 0}}]}"
    def print_msg(self, address, *args):
        print(f"Address: {address}\nMessage: {args}\n\n")

    def default_handler(self, address, *args):
        self.get_logger().info(f"WARNING: Received message without `/ros_publish/...` address:\nAddress: {address}\nMessage: {args}")

    # def sh_cmd_handler(self, address, *args):
    #     self.get_logger().info(f"\nAddress: {address}\nArgs: {args}")
    #     # Process OSC msg
    #     osc_msg_topic = address
    #     osc_msg_data = args[0]

    #     process = subprocess.Popen(osc_msg_data, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    #     # Read from the process output in real-time
    #     for line in process.stdout:
    #         self.get_logger().info(f"Feedback: {line}\n")

    #     # Create Publisher
    #     publisher = self.create_publisher(String, osc_msg_topic, 10)
    #     # Make ROS message
    #     print(type(osc_msg_data))
    #     ros_msg = String()
    #     ros_msg.data = osc_msg_data
    #     # Publish
    #     publisher.publish(ros_msg)
    #     # Log
    #     self.get_logger().info('Publishing: "%s"' % ros_msg.data)

    # def osc_ros_publish(self, address, *args):
    #     self.get_logger().info(f"\nAddress: {address}\nArgs: {args}")
    #     print(type(args))
    #     # Process OSC msg
    #     osc_msg_topic = address
    #     osc_msg_data = args[0]
    #     # Create Publisher
    #     publisher = self.create_publisher(String, osc_msg_topic, 10)
    #     # Make ROS message
    #     print(type(osc_msg_data))
    #     ros_msg = String()
    #     ros_msg.data = osc_msg_data
    #     # Publish
    #     publisher.publish(ros_msg)
    #     # Log
    #     self.get_logger().info('Publishing: "%s"' % ros_msg.data)

def main(args=None):
    print(">>> Starting OSC server node...")
    rclpy.init(args=args)

    server = PibotServer(ip, port)
    
    try:
    	rclpy.spin(server)
    except (KeyboardInterrupt):
        pass
    finally:
    	server.destroy_node()
    	rclpy.shutdown()

if __name__ == '__main__':
    main()
