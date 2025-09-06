from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time


cam_mode = 1

def keyboard_listener(key, x, y):
    global current_weather_idx

    if game_status['game_over'] or game_status['level_complete']:
        if key == b'r': reset_level()
        if key == b'n' and game_status['level_complete']: reset_level()
        return
    
    if key == b'p': game_status['paused'] = not game_status['paused']
    if key == b'o': current_weather_idx = (current_weather_idx + 1) % len(weather_types)
    
    if game_status['paused']: return

    vehicle, vehicle_type = player_vehicle, vehicle_types[player_vehicle['type']]
    if key == b'w':
        if vehicle['gear'] == 'DRIVE': vehicle['speed'] = min(vehicle_type['max_speed'], vehicle['speed'] + vehicle_type['acceleration'])
    elif key == b's':
        if vehicle['gear'] == 'DRIVE': vehicle['speed'] = max(0, vehicle['speed'] - vehicle_type['brake_power'])
        elif vehicle['gear'] == 'REVERSE': vehicle['speed'] = max(-vehicle_type['max_speed'] * 0.5, vehicle['speed'] - vehicle_type['acceleration'])
    elif key == b'a':
        if abs(vehicle['speed']) > 0.1: vehicle['angle'] += vehicle_type['turn_rate']
    elif key == b'd':
        if abs(vehicle['speed']) > 0.1: vehicle['angle'] -= vehicle_type['turn_rate']
    elif key == b'g':
        gears = ['DRIVE', 'REVERSE', 'PARK']
        vehicle['gear'] = gears[(gears.index(vehicle['gear']) + 1) % len(gears)]
    elif key == b't':
        game_status['cheat_mode'] = not game_status['cheat_mode']
    elif key == b'c':
        global cam_mode
        cam_mode = (cam_mode + 1) % 3
    elif key in [b'1', b'2', b'3', b'4']:
        vehicle_map = {b'1': 'SEDAN', b'2': 'SUV', b'3': 'SPORTS_CAR', b'4': 'TRUCK'}
        change_vehicle(vehicle_map[key])




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