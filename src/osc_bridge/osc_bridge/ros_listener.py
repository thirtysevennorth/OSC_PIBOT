# Copyright 2016 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import rclpy
from rclpy.node import Node
from pythonosc.dispatcher import Dispatcher
from std_msgs.msg import String
from nav_msgs.msg import Odometry
from sensor_msgs.msg import BatteryState
from irobot_create_msgs.msg import AudioNoteVector
from pythonosc.udp_client import SimpleUDPClient


server_ip = "192.168.0.1"
server_port = 1337

topiclist = [('/pibot/battery',      '/battery_state', BatteryState),
             ('/pibot/odom'   ,      '/odom'         , Odometry),
             ('/pibot/cmd_playnote', '/cmd_audio'    , AudioNoteVector)]

class MultiSubscriber(Node):
    def make_subscriber(topic, typ, callback,):
        self.create_subscription(typ, topic, callback, 10)

    def __init__(self, ip, port, topiclist):
        super().__init__('create3_multi_subscriber')
        # Init client
        self.osc_client = SimpleUDPClient(ip, port)

        # Init subscriptions and their callbacks
        self.topic_subscriptions = []
        for (addr, topic, typ) in topiclist:
            callback = lambda msg: self.osc_client.send_message(addr, msg.data)
            subscription = self.create_subscription(typ, topic, callback, 10)
            self.topic_subscriptions.append(subscription)

        self.subscriptions  # prevent unused variable warning

def main(args=None):
    rclpy.init(args=args)

    create3_multi_subscriber = MultiSubscriber(server_ip, server_port, topiclist)

    try:
        rclpy.spin(create3_multi_subscriber)
    except (KeyboardInterrupt):
        pass
    finally:
        create3_multi_subscriber.destroy_node()
        rclpy.shutdown()
