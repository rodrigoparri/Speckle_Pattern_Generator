import numpy as np

def generate_speckle(diameter:int):
    """
    :param diameter: speckle diameter in pixels
    :return:array of size diameter x diameter
    """
    #x is a row vector storing all possible x coordinates of each slot
    #y is a colum vector storing all possible y coordinates of each slot
    y , x = np.ogrid[:diameter, :diameter]
    # mask is an x*y matrix storing booleans indicating whether the distance of each pixel to the central pixel <= D**2
    mask = 4*((x - diameter / 2) ** 2 + (y - diameter / 2) ** 2) <= diameter ** 2
    speckle = np.zeros((diameter, diameter))
    speckle[mask] = 1
    print(speckle)

if __name__ == "__main__":

    generate_speckle(7)