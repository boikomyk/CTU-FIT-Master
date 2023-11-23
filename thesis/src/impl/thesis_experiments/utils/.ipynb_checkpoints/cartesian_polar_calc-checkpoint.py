import math
import numpy as np

LOG_WARNINGS = False

def cartesian_to_polar(x, THRESH = 0.0001):
    """   
    Converts 2d cartesian position and velocity coordinates to polar coordinates
    Args:
    x : np.array - position and velocity components in cartesian respectively 
    THRESH : float - minimum value of rho to return non-zero values

    Returns: 
    rho, drho : floats - radius and velocity magnitude respectively
    phi : float - angle in radians
    """
    p_x,p_y,v_x,v_y = x
    
    rho = math.sqrt(p_x**2 + p_y**2)
    phi = np.arctan2(p_y, p_x)
    
    if rho < THRESH:
        if LOG_WARNINGS:
            print("WARNING: in cartesian_to_polar(): d_squared < THRESH")
        rho, phi, drho = 0, 0, 0
    else:
        drho = (p_x * v_x + p_y * v_y) / rho
    
    return np.array([rho,phi,drho])


def polar_to_cartesian(y):
    """
    Converts 2D polar coordinates into cartesian coordinates
    Args:
    rho. drho : floats - radius magnitude and velocity magnitudes respectively
    phi : float - angle in radians
    Returns:
    x, y, vx, vy : floats - position and velocity components in cartesian respectively
    """
    rho, phi, drho = y
 
    p_x, p_y = rho * math.cos(phi), rho * math.sin(phi)
    v_x, v_y = drho * math.cos(phi) , drho * math.sin(phi)
    
    return np.array([p_x,p_y,v_x,v_y])
