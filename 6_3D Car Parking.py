from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time


cam_mode = 1

vehicle_types = {
    'SEDAN': {
        'length': 40, 'width': 20, 'max_speed': 8, 'acceleration': 0.3,
        'turn_rate': 4, 'brake_power': 0.5, 'color': [0.8, 0.2, 0.2]
    },
    'SUV': {
        'length': 50, 'width': 25, 'max_speed': 6, 'acceleration': 0.2,
        'turn_rate': 3, 'brake_power': 0.7, 'color': [0.2, 0.6, 0.2]
    },
    'SPORTS_CAR': {
        'length': 35, 'width': 18, 'max_speed': 12, 'acceleration': 0.5,
        'turn_rate': 6, 'brake_power': 0.8, 'color': [0.8, 0.8, 0.2]
    },
    'TRUCK': {
        'length': 60, 'width': 30, 'max_speed': 4, 'acceleration': 0.15,
        'turn_rate': 2, 'brake_power': 0.4, 'color': [0.4, 0.4, 0.8]
    }
}

player_vehicle = {
    'pos': [0, 0, 5], 'angle': 0, 'speed': 0, 'max_speed': 8,
    'acceleration': 0.3, 'turn_rate': 4, 'brake_power': 0.5,
    'health': MAX_HEALTH, 'gear': 'DRIVE', 'type': 'SEDAN',
    'length': 40, 'width': 20, 'damage_level': 0
}



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

def change_vehicle(vehicle_type):
    player_vehicle['type'] = vehicle_type
    vehicle_data = vehicle_types[vehicle_type]
    for key, value in vehicle_data.items():
        if key in player_vehicle:
            player_vehicle[key] = value

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