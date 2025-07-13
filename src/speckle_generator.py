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

def image_speckle(width:int=25, height:int=25, diameter:float=0.5, resolution:int=300, grid_step:float=0.7, min_diameter:int=1, pos_rand:int=0):
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
    size_rand_checker = min_diameter <= 0
    pos_rand_checker = pos_rand <= 0

    # dots per mm
    dpmm = resolution / 25.4
    # target width and height to crop the image to at the end of the function
    width_px = math.floor(width * dpmm)
    height_px = math.floor(height * dpmm)
    diameter_px = math.ceil(diameter * dpmm)
    grid_step_px = math.floor(diameter_px * grid_step)
    # size scalar in as function for diameter
    size_rand_diam = min_diameter / 100
    # position deviation as function of diameter
    pos_rand_diam = pos_rand / 100

    numx_steps_px = math.ceil(width_px / grid_step_px)
    numy_steps_px = math.ceil(height_px / grid_step_px)
    # initial image dimension are bigger for later trimming. +1 step is added for overflow safety
    initial_width_px = (numx_steps_px + 1) * grid_step_px
    initial_height_px = (numy_steps_px + 1) * grid_step_px

    image = np.full((initial_width_px, initial_height_px), 255, dtype=np.uint8)
    # speckle coordinates in number of steps. index of row and column of speckle
    y_step_coord, x_step_coord = np.ogrid[:numy_steps_px, :numx_steps_px]

    # num_unique_diameter = math.ceil(diameter_px)
    # number of unique speckles is also diameter_px
    speckle_buffer = np.zeros((diameter_px, diameter_px, diameter_px), dtype=np.uint8)
    buffer_pos = 0
    # filling the buffer
    for d in range(math.ceil(size_rand_diam * diameter_px), diameter_px):
        # Speckle side_len is adjusted to maximum diameter size.
        speckle_buffer[buffer_pos] = generate_speckle(side_len=diameter_px, diameter=d)
        buffer_pos += 1

    # index for selecting random speckle must be between 1 (inclusive) and buffer_poss (exclusive)
    high_index_bound = max(1, buffer_pos)
    # random position radius
    random_radius_px = math.ceil(diameter_px / 2 * pos_rand_diam)
    high_rand_pos_bound = max(1, random_radius_px)

    for y_coord in np.ravel(y_step_coord):
        for x_coord in x_step_coord[0]:
            # random delta is calculated twice so random increment is decoupled in x and y
            y_rand_delta = np.random.randint(low=0, high=high_rand_pos_bound)
            x_rand_delta = np.random.randint(low=0, high=high_rand_pos_bound)
            # coordinates of the upper left corner of the speckle in the complete image
            y_coord_px = y_coord * grid_step_px + y_rand_delta
            x_coord_px = x_coord * grid_step_px + x_rand_delta
            # select a random speckle from speckle buffer
            rand_speckle_index = np.random.randint(low=0, high=high_index_bound)
            # &= is the bitwise AND operator
            image[y_coord_px: y_coord_px + diameter_px, x_coord_px : x_coord_px + diameter_px] &= speckle_buffer[rand_speckle_index]
            #print(y_coord, x_coord)

    # image crop
    image = image[1: 1+height_px, 1: 1+width_px]
    return image.copy()

if __name__ == "__main__":

    #generate_speckle(side_len=11, diameter=3)
    #image_speckle(10, 10, .5, 300, 1, 80, 150)
    print(image_speckle())