import numpy as np
import math
import sys

np.set_printoptions(threshold=sys.maxsize, linewidth=np.inf)

def generate_speckle(side_len:int ,diameter:int):
    """
    Creates an array of diameter x diameter with a centered circle of 1s and zeros in the rest of the slots
    :param diameter: speckle diameter in pixels
    :return:array of size diameter x diameter
    """
    # check if diameter is larger than array size
    if side_len < diameter:
        raise ValueError("Diameter must be equal or smaller than width and height")
    else:
        #x is a row vector storing all possible x coordinates of each slot
        #y is a colum vector storing all possible y coordinates of each slot
        y , x = np.ogrid[:side_len, :side_len]
        # mask is an x*y matrix storing booleans indicating whether the distance of each pixel to the central pixel <= D**2
        mask = 4*((x - side_len / 2) ** 2 + (y - side_len / 2) ** 2) <= diameter ** 2
        speckle = np.full((side_len, side_len), 255, dtype=np.uint8)
        speckle[mask] = 0
        return speckle.copy()

def image_speckle(width:int=5, height:int=30, diameter:float=0.5, resolution:int=300, grid_step:float=1, min_diameter:int=1, pos_rand:int=100):
    """
    Creates an array of speckles using the arrays created by generata_speckle.
    :param width: in mm, width of the image
    :param height: in mm, height of the image
    :param diameter: in mm, maximum diameter of the speckles
    :param resolution: in dot per inch, resolution of the image
    :param grid_step: as times the diameter, separation between speckles
    :param min_diameter: as % of the diameter, minimum diameter
    :param pos_rand: as % of the diameter, maximum random position deviation
    :return:array of speckles.
    """
    width_checker = width <= 0
    height_checker = height <= 0
    diameter_checker = diameter <= 0
    resolution_checker = resolution <= 0
    grid_step_checker = grid_step <= 0.69
    size_rand_checker = min_diameter < 1
    pos_rand_checker = pos_rand <= 0

    # dots per mm
    dpmm = resolution / 25.4
    # target width and height to crop the image to at the end of the function
    width_px = math.floor(width * dpmm)
    height_px = math.floor(height * dpmm)
    #print("W", width_px)
    #print("H", height_px)

    diameter_px = math.ceil(diameter * dpmm)
    grid_step_px = math.ceil(diameter_px * grid_step)
    # size scalar per one diameter
    size_rand_diam = min_diameter / 100
    # min_diameter_px must be a ceiling function so it´s never zero since size_rand_diam != 0
    min_diameter_px = math.ceil(size_rand_diam * diameter_px)

    # position deviation per one diameter
    pos_rand_diam = pos_rand / 100

    num_x_steps = math.ceil(width_px / grid_step_px)
    num_y_steps = math.ceil(height_px / grid_step_px)
    #print("num_x_steps", num_x_steps)
    #print("num_y_steps", num_y_steps)
    padding = 10 * grid_step_px
    # initial image dimension are bigger for later trimming. +1 step is added for overflow safety
    initial_width_px = num_x_steps * grid_step_px + 2 * padding
    initial_height_px = num_y_steps * grid_step_px + 2 * padding

    #print("init_W", initial_width_px)
    #print("init_H", initial_height_px)
    image = np.full((initial_height_px, initial_width_px), 255, dtype=np.uint8)

    # speckle coordinates in number of steps. index of row and column of speckle
    y_step_coord = np.arange(num_y_steps)
    x_step_coord = np.arange(num_x_steps)

    speckle_buffer = np.zeros((diameter_px, diameter_px, diameter_px), dtype=np.uint8)
    buffer_pos = 0
    # filling the buffer
    for d in range(min_diameter_px, diameter_px + 1):  # 1 is added so star-stop is at least always one
        # Speckle side_len is adjusted to maximum diameter size.
        speckle_buffer[buffer_pos] = generate_speckle(side_len=diameter_px, diameter=d)

        if min_diameter_px == diameter_px:
            buffer_pos = 0
        else:
            buffer_pos += 1

    # higher index bound for selecting random speckle must be between 1 (inclusive) and buffer_poss (exclusive)
    high_index_bound = max(1, buffer_pos)
    # random position radius
    random_radius_px = math.ceil(diameter_px *2* pos_rand_diam)
    rand_pos_bound = max(1, random_radius_px)

    for y_coord in y_step_coord:
        for x_coord in x_step_coord:
            # random delta is calculated twice so random increment is decoupled in x and y
            y_rand_delta = np.random.randint(low=-rand_pos_bound, high=rand_pos_bound)
            x_rand_delta = np.random.randint(low=-rand_pos_bound, high=rand_pos_bound)
            # coordinates of the upper left corner of the speckle in the complete image
            y_coord_px = (y_coord + 1) * grid_step_px + y_rand_delta + padding
            x_coord_px = (x_coord + 1) * grid_step_px + x_rand_delta + padding
            # select a random speckle from speckle buffer
            rand_speckle_index = np.random.randint(low=0, high=high_index_bound)
            # &= is the bitwise AND operator
            image[y_coord_px: y_coord_px + diameter_px, x_coord_px : x_coord_px + diameter_px] &= speckle_buffer[rand_speckle_index]
            #print(y_coord, x_coord)

    # image crop
    image = image[padding : padding + height_px, padding : padding + width_px]
    return image.copy()

if __name__ == "__main__":

    #generate_speckle(side_len=11, diameter=3)
    print(image_speckle(25, 30, 1.5, 100, 1, 80, 20))
