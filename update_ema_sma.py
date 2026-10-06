def update_ema(prev_value, new_value, frame_size):
    k = 2 / (frame_size + 1)
    return (new_value * k) + (prev_value * (1 - k))


def update_sma(oldest_value, current_value, new_value, frame_size):
    return current_value - (oldest_value / frame_size) + (new_value / frame_size)