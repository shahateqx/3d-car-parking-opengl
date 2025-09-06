from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time







def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"3D Car Parking Challenge")
    
    glutDisplayFunc(show_screen)
    glutKeyboardFunc(keyboard_listener)
    glutIdleFunc(idle)
    glutSpecialFunc(special_key_listener)
    
    init_level(1)
    
    glutMainLoop()

if __name__ == "__main__":
    main()