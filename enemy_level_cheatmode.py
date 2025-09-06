def draw_obstacle(obstacle):
    glPushMatrix()
    glTranslatef(obstacle['pos'][0], obstacle['pos'][1], 0)
    final_color = apply_weather_color(obstacle['color'])
    glColor3f(*final_color)
    quad = gluNewQuadric()
    if obstacle['type'] == 'CONE':
        gluCylinder(quad, obstacle['size'], 0, obstacle['size'] * 2, 8, 1)
    elif obstacle['type'] == 'BARRIER':
        glScalef(obstacle['size'] * 2, obstacle['size'] * 0.5, obstacle['size'])
        glutSolidCube(1)
    elif obstacle['type'] == 'WALL':
        glScalef(obstacle['size'], obstacle['size'] * 0.2, obstacle['size'] * 2)
        glutSolidCube(1)
    elif obstacle['type'] == 'PILLAR':
        gluCylinder(quad, obstacle['size'] * 0.5, obstacle['size'] * 0.5, obstacle['size'] * 3, 12, 1)
    glPopMatrix()

def draw_walker(walker):
    glPushMatrix()
    glTranslatef(walker['pos'][0], walker['pos'][1], 10)
    body_color = apply_weather_color(walker['color'])
    glColor3f(*body_color)
    glPushMatrix()
    glScalef(4, 4, 15)
    glutSolidCube(1)
    glPopMatrix()
    head_color = apply_weather_color([0.9, 0.7, 0.5])
    glColor3f(*head_color)
    glTranslatef(0, 0, 11)
    glutSolidSphere(4, 8, 8)
    glPopMatrix()

def draw_environment():
    road_color = apply_weather_color([0.3, 0.3, 0.3])
    glColor3f(*road_color)
    glPushMatrix()
    glTranslatef(0, 0, -1)
    glScalef(WORLD_WIDTH, WORLD_HEIGHT, 1)
    glutSolidCube(1)
    glPopMatrix()

    line_color = apply_weather_color([0.9, 0.9, 0.9])
    glColor3f(*line_color)
    for y in range(-WORLD_HEIGHT//2, WORLD_HEIGHT//2, 100):
        for x in range(-WORLD_WIDTH//2, WORLD_WIDTH//2, 50):
            glPushMatrix()
            glTranslatef(x + 12.5, y, 0.1)
            glScalef(25, 4, 1)
            glutSolidCube(1)
            glPopMatrix()


def init_level(level_num):
    global static_barriers, walkers, moving_vehicles, parking_slots, current_parking_slot
    
    static_barriers.clear()
    walkers.clear()
    moving_vehicles.clear()
    parking_slots.clear()
    
    for i in range(OBSTACLE_COUNT + level_num * 2):
        barrier = {
            'pos': [random.uniform(-WORLD_WIDTH//2 + 50, WORLD_WIDTH//2 - 50),
                    random.uniform(-WORLD_HEIGHT//2 + 50, WORLD_HEIGHT//2 - 50), 5],
            'type': random.choice(['CONE', 'BARRIER', 'WALL', 'PILLAR']),
            'size': random.uniform(10, 25),
            'color': [random.uniform(0.5, 1.0), random.uniform(0.3, 0.8), 0.2],
            'health': 100
        }
        static_barriers.append(barrier)
    
    for i in range(MOVING_CAR_COUNT):
        moving_vehicle = {
            'pos': [random.uniform(-WORLD_WIDTH//2 + 100, WORLD_WIDTH//2 - 100),
                    random.uniform(-WORLD_HEIGHT//2 + 100, WORLD_HEIGHT//2 - 100), 5],
            'angle': random.uniform(0, 360), 'speed': random.uniform(0.2, 0.5),
            'path': [[random.uniform(-WORLD_WIDTH//2 + 50, WORLD_WIDTH//2 - 50),
                      random.uniform(-WORLD_HEIGHT//2 + 50, WORLD_HEIGHT//2 - 50)] for _ in range(5)],
            'path_idx': 0, 'type': random.choice(list(vehicle_types.keys())), 'active': True
        }
        moving_vehicles.append(moving_vehicle)
    
    for i in range(PEDESTRIAN_COUNT):
        walker = {
            'pos': [random.uniform(-WORLD_WIDTH//2 + 50, WORLD_WIDTH//2 - 50),
                    random.uniform(-WORLD_HEIGHT//2 + 50, WORLD_HEIGHT//2 - 50), 2],
            'angle': random.uniform(0, 360), 'speed': random.uniform(0.5, 2.0),
            'path': [[random.uniform(-WORLD_WIDTH//2 + 30, WORLD_WIDTH//2 - 30),
                      random.uniform(-WORLD_HEIGHT//2 + 30, WORLD_HEIGHT//2 - 30)] for _ in range(3)],
            'path_idx': 0, 'active': True,
            'safety_distance': 60,
            'color': [random.uniform(0.3, 0.8), random.uniform(0.3, 0.8), random.uniform(0.3, 0.8)]
        }
        walkers.append(walker)
    
    parking_slot = {
        'pos': [random.uniform(-WORLD_WIDTH//2 + 100, WORLD_WIDTH//2 - 100),
                random.uniform(-WORLD_HEIGHT//2 + 100, WORLD_HEIGHT//2 - 100), 0],
        'angle': random.choice([0, 45, 90, 135, 180]),
        'size': [PARKING_SPOT_SIZE + 10, PARKING_SPOT_SIZE + 10]
    }
    current_parking_slot = parking_slot
    parking_slots.append(parking_slot)
    
    player_vehicle['pos'] = [0, -200, 5]
    init_rain()


def update_ai_vehicles(dt):
    time_factor = dt * 60
    for vehicle in moving_vehicles:
        if not vehicle['active']: continue
        target = vehicle['path'][vehicle['path_idx']]
        dx, dy = target[0] - vehicle['pos'][0], target[1] - vehicle['pos'][1]
        distance = math.sqrt(dx*dx + dy*dy)
        if distance < 20:
            vehicle['path_idx'] = (vehicle['path_idx'] + 1) % len(vehicle['path'])
        elif distance > 0:
            vehicle['angle'] = math.degrees(math.atan2(dy, dx))
            rad = math.radians(vehicle['angle'])
            vehicle['pos'][0] += math.cos(rad) * vehicle['speed'] * time_factor
            vehicle['pos'][1] += math.sin(rad) * vehicle['speed'] * time_factor

def update_walkers(dt):
    time_factor = dt * 60
    for walker in walkers:
        if not walker['active']:
            continue
        
        player_distance = distance_2d(walker['pos'], player_vehicle['pos'])

        if player_distance < walker['safety_distance']:
            dx = walker['pos'][0] - player_vehicle['pos'][0]
            dy = walker['pos'][1] - player_vehicle['pos'][1]
            norm = math.sqrt(dx*dx + dy*dy)
            if norm > 0:
                walker['pos'][0] += (dx / norm) * walker['speed'] * 1.5 * time_factor
                walker['pos'][1] += (dy / norm) * walker['speed'] * 1.5 * time_factor
        else:
            if walker['path'] and len(walker['path']) > walker['path_idx']:
                target = walker['path'][walker['path_idx']]
                dx = target[0] - walker['pos'][0]
                dy = target[1] - walker['pos'][1]
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance < 10:
                    walker['path_idx'] = (walker['path_idx'] + 1) % len(walker['path'])
                elif distance > 0:
                    walker['pos'][0] += dx / distance * walker['speed'] * time_factor
                    walker['pos'][1] += dy / distance * walker['speed'] * time_factor


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