
import pygame





if __name__=="__main__":

    pygame.init()
    pygame.joystick.init()

    while True:
        if pygame.joystick.get_count() > 0:
            print("Joystick found.")
            joystick = pygame.joystick.Joystick(0)
            print (joystick.get_name())
            joystick.init()
            break

        # elif serial for new romote       
        else:
            print("No joystick found. trying again...")
            pygame.joystick.quit()
            pygame.init()
            pygame.joystick.init()
            
            