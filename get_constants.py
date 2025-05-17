"""
A collection of commonly used physical constants in SI units.
"""

__all__ = [
    "M_E",
    "R_E",
    "G",
    "omega_E",
    "c",
    "dt",
    "lam",
    "w0",
    "rg",
    "etaZen"
]

# Constants for satellite orbit and communication
# - - - - - - - - - - - - - - - - - - - - - - - -
# Mass of Earth (kg)
M_E: float = 5.972e24

# Equatorial radius of Earth (m)
R_E: float = 6.378e6

# Gravitational constant (N.m^{2}.kg^{-2})
G: float = 6.674e-11

# Angular velocity of Earth (m.s^{-1})
omega_E: float = 7.292e-5

# Speed of light in vacuum (m.s^{-1})
c: float = 2.9979e8

# Processing time (s)
dt: float = 1.0e-3


# Constants for loss model
# - - - - - - - - - - - - 
# Wavelength of communication signals (m)
lam: float = 810e-9

# Initial beam waist (m)
w0: float = 0.025

# Ground station receiver radius (m)
rg: float = 0.75

# Atmospheric transmittance at zenisth (1)
etaZen: float = 0.5