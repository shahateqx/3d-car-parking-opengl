from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time


cam_mode = 1
collision_sparks = []

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

game_status = {
    'score': 0, 'level': 1, 'time_left': 60, 'game_over': False,
    'paused': False, 'level_complete': False, 'mode': 'CLASSIC',
    'collisions': 0, 'cheat_mode': False
}

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_hud():
    speed_kmh = abs(player_vehicle['speed']) * 10
    draw_text(10, 770, f"Speed: {speed_kmh:.0f} km/h")
    draw_text(10, 750, f"Health: {player_vehicle['health']:.0f}%")
    draw_text(10, 730, f"Gear: {player_vehicle['gear']}")
    draw_text(10, 710, f"Score: {game_status['score']}")
    draw_text(10, 690, f"Time: {game_status['time_left']:.1f}s")
    draw_text(10, 670, f"Weather: {weather_types[current_weather_idx]} (O)")
    
    cam_modes = ['Top-Down (Orbit)', 'Third-Person', 'First-Person']
    draw_text(800, 770, f"Camera: {cam_modes[cam_mode]} (C)")
    draw_text(800, 750, f"Vehicle: {player_vehicle['type']}")

    if game_status['game_over']:
        draw_text(450, 400, "GAME OVER")
        draw_text(430, 370, "Press R to restart")
    if game_status['level_complete']:
        draw_text(420, 400, "LEVEL COMPLETE!")
        draw_text(410, 370, "Press N for next level")
    if game_status['paused']:
        draw_text(470, 400, "PAUSED")

def update_vehicle_physics(dt):
    if game_status['paused'] or game_status['game_over']: return
    vehicle = player_vehicle
    time_factor = dt * 60

    if vehicle['gear'] == 'DRIVE' and vehicle['speed'] < 0: vehicle['speed'] = min(0, vehicle['speed'] + vehicle['brake_power'] * time_factor)
    elif vehicle['gear'] == 'REVERSE' and vehicle['speed'] > 0: vehicle['speed'] = max(0, vehicle['speed'] - vehicle['brake_power'] * time_factor)
    
    vehicle['speed'] *= (0.98 ** time_factor)
    if abs(vehicle['speed']) < 0.01: vehicle['speed'] = 0
    
    if abs(vehicle['speed']) > 0:
        rad = math.radians(vehicle['angle'])
        dx = math.cos(rad) * vehicle['speed'] * time_factor
        dy = math.sin(rad) * vehicle['speed'] * time_factor
        vehicle['pos'][0] += dx
        vehicle['pos'][1] += dy
        
        if abs(vehicle['speed']) > vehicle['max_speed'] * 0.7:
            add_skid_marks(vehicle['pos'], vehicle['angle'])

def handle_collision(collision_type, object_hit):
    if game_status['cheat_mode']: return
    
    damage = abs(player_vehicle['speed']) * 2
    player_vehicle['health'] -= damage
    player_vehicle['damage_level'] += damage
    game_status['collisions'] += 1
    player_vehicle['speed'] *= -0.3
    
    if collision_type == 'PEDESTRIAN':
        object_hit['active'] = False
        for _ in range(15):
            collision_sparks.append({
                'pos': list(player_vehicle['pos']),
                'velocity': [random.uniform(-3, 3), random.uniform(-3, 3), random.uniform(2, 6)],
                'color': [1, 0, 0],
                'life': 60
            })
    elif collision_type == 'OBSTACLE' or collision_type == 'CAR':
        game_status['game_over'] = True

    if player_vehicle['health'] <= 0:
        player_vehicle['health'] = 0
        game_status['game_over'] = True

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