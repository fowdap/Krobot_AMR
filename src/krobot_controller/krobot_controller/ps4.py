#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
import pygame
from geometry_msgs.msg import Twist 

class MyNode(Node):
    def __init__(self):
        super().__init__('remote_publisher')
        pygame.init()
        pygame.joystick.init()

        while True:
            if pygame.joystick.get_count() > 0:
                # print("Joystick found.")
                self.joystick = pygame.joystick.Joystick(0)
                # print (joystick.get_name())
                self.joystick.init()
                break    
            else:
                # print("No joystick found. trying again...")
                pygame.joystick.quit()
                pygame.init()
                pygame.joystick.init()
       
        # pygame.event.pump()  # Update event queue
        self.publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        self.timer = self.create_timer(0.2, self.publish_command)

    def read_controller_input(self):

        if pygame.joystick.get_count() > 0:
            pygame.event.pump()  # Update event queue
            # Get joystick axes and buttons
    
            left_stick_x = self.joystick.get_axis(0)
            left_stick_y = self.joystick.get_axis(1)
            self.get_logger().info('Publishing: data=%.2f, Angular=%.2f' % (left_stick_x, left_stick_y)) 

            left_stick_x = 0.0 if -0.1 < left_stick_x < 0.1 else left_stick_x
            left_stick_y = 0.0 if -0.1 < left_stick_y < 0.1 else left_stick_y

            return left_stick_x, left_stick_y
        else:
            pygame.joystick.quit()
            pygame.init()
            pygame.joystick.init()
            if pygame.joystick.get_count() > 0 :
                self.joystick = pygame.joystick.Joystick(0)
                    # print (joystick.get_name())
                self.joystick.init()
            return 0.0, 0.0

    
    def publish_command(self):

        left_stick_x, left_stick_y = self.read_controller_input()


        msg = Twist()  # Create a Twist message object
        msg.linear.x = -left_stick_y  # Set linear speed in the x-direction (move forward)
        msg.angular.z = -left_stick_x * 2  # Set angular speed to zero (no rotation)
        self.publisher.publish(msg)  # Publish the velocity command
        self.get_logger().info('Publishing: Linear=%.2f, Angular=%.2f' % (msg.linear.x, msg.angular.z))  # Log message


def main(args=None):
    rclpy.init(args=args)
    my_node = MyNode()
    rclpy.spin(my_node)
    rclpy.shutdown()


if __name__=="__main__":
    main()
