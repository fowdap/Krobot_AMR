#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseWithCovarianceStamped
import time

class InitialPosePublisher(Node):
    def __init__(self):
        super().__init__('initial_pose_publisher')

        # Create publisher on /initialpose topic
        self.publisher_ = self.create_publisher(PoseWithCovarianceStamped, '/initialpose', 10)

        time.sleep(1)

        # Set up a one-shot timer to delay publishing by 1 second
        self.timer = self.create_timer(1.0, self.publish_pose)

    def publish_pose(self):
        msg = PoseWithCovarianceStamped()
        msg.header.frame_id = 'map'
        msg.header.stamp = self.get_clock().now().to_msg()

        # Set initial position
        msg.pose.pose.position.x = 0.0
        msg.pose.pose.position.y = 0.0
        msg.pose.pose.position.z = 0.0

        # Set orientation (facing forward)
        msg.pose.pose.orientation.z = 0.0
        msg.pose.pose.orientation.w = 1.0

        # Set some default covariance
        covariance = [
                    0.25, 0.0, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.25, 0.0, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.25, 0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0685, 0.0, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0685, 0.0,
                    0.0, 0.0, 0.0, 0.0, 0.0, 0.0685
                    ]

        msg.pose.covariance = covariance
        self.publisher_.publish(msg)
        self.get_logger().info('Initial pose published.')

        # Shutdown after publishing
        rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    node = InitialPosePublisher()
    rclpy.spin(node)  # Keeps node alive until publish_pose runs
    node.destroy_node()

if __name__ == '__main__':
    main()
