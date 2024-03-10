async def rotate(degrees, degrees_per_s, rad=11.5):
    print(f"Rotating {degrees} degrees at a speed of {degrees_per_s} d/s, with radius {rad}...")
    # print("Starting pos:")
    # start_pos = await get_pos()

    if degrees == 0:
        return
    elif degrees > 0:
        direction = 'right'
    else:
        direction = 'left'

    degrees = abs(degrees)
    wheel_speed = 0.85 * wheel_speed_for_rotation(rad, degrees_per_s) #calculate_wheel_speed_for_rotation(degrees, degrees_per_s)
    # wheel_speed = (wheel_speed * param_rotation_speed_factor) + param_rotation_speed_offset
    rotation_dur = degrees / degrees_per_s

    if direction == 'right':
        speed_l = wheel_speed
        speed_r = -wheel_speed
    elif direction == 'left':
        speed_l = -wheel_speed
        speed_r = wheel_speed

    result = await set_wheel_speeds_dur(speed_l, speed_r, rotation_dur)
    print(f"==Done rotating {degrees} degrees at a speed of {degrees_per_s} d/s, with radius {rad}...")
    # end_pos = await get_pos()
    # print(f"Start pos: {start_pos}, End pos: {end_pos}")
    # print(f"++ Rotation headings: Start: {start_pos.heading}, End: {end_pos.heading}")
    # print(f"++ Rotation headings diff = {end_pos.heading - start_pos.heading}")


range(1, 30, 0.5)


d = dict()

d[3] = 5

dict([(i, 1) for i in range(1,30)])

d
