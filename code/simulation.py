import numpy as np
from get_constants import M_E, R_E, G, omega_E, c, dt, lam, w0, rg, etaZen

class simulate():
    def __init__(self, h, gs=2):
        """
        Initializes the entire class. It defines
        the satelite and ground station's physical values.

        Parameters:
        -----------
        h           : Satellite altitude (m)
        gs          : Number of ground stations
        """

        # Initializing satellite
        self.satellite = {
            "altitude": h,
            "radius": R_E + h,
            "omega": np.sqrt((G * M_E)/((R_E + h)**3)),
            "l_max": np.sqrt((R_E + h)**2 - R_E**2)
        }

        # Initializing ground stations
        self.ground_stations = {
            f"station_{i+1}": {"name": f"Station {i+1}"}
            for i in range(gs)
        }

    def epsilon(self, d):
        """
        Finds the angular separation given the orthodromic distance.

        Parameters:
        -----------
        d           : Orthodromic ground station separation

        Returns:
        --------
        epsilon     : Radial separation of ground stations
        """

        return d/(2*R_E)
    
    def initial_conditions(self, d):
        """
        Sets the initial conditions for the satellite
        and the ground stations.

        Parameters:
        -----------
        d           : Orthodromic ground station separation
        """

        ep = self.epsilon(d)
        r = self.satellite["radius"]

        self.ground_stations["station_1"]["phi_0"] = (np.pi/2) - ep
        self.ground_stations["station_2"]["phi_0"] = (np.pi/2) + ep

        theta_0 = np.pi - np.arccos(
            -(1/r) * (R_E * np.sin(ep) + np.cos(ep) *
                      np.sqrt(r**2 - R_E**2)))
        
        self.satellite["theta_0"] = theta_0

    def visibility(self):
        """
        Finds the total time the satellite spends
        in visibility.

        Returns:
        --------
        t_whole     : Total time spent in visibility (s)
        """

        omega_s = self.satellite["omega"]
        theta_0 = self.satellite["theta_0"]
        theta_f = np.pi - theta_0

        return (theta_f - theta_0) / (omega_s - omega_E)
    
    def L_function(self, station, t):
        """
        Computes the distance between the satellite and
        a ground station at some time t.

        Parameters:
        -----------
        station     : A dictionary that contains all station info
        t           : The time being considered (s)
        """

        phi_0 = station["phi_0"]
        theta_0 = self.satellite["theta_0"]
        r = self.satellite["radius"]
        omega_s = self.satellite["omega"]

        L = np.sqrt(r**2 + R_E**2 - 2*r*R_E*np.cos(
            (theta_0 - phi_0) + ((omega_s - omega_E) * t)
        ))

        return L
    
    def eta_sg(self, L):
        """
        Computes free space transmittance.

        Parameters:
        -----------
        L       : Distance between satellite and ground station (m)

        Returns:
        --------
        eta_sg      : Success probability due to device limitations
        """

        LR=np.pi*w0**2/lam

        wg=w0*np.sqrt(1+L**2/LR**2)

        return 1-np.exp(-2*rg**2/wg**2)
    
    def eta_Atm(self, L):
        """
        Computes atmospheric transmittance.

        Parameters:
        -----------
        L       : Distance between satellite and ground station (m)

        Returns:
        --------
        eta_atm     : Success probability due to atmospheric limitations
        """

        h = self.satellite["altitude"]

        secZen=1/((h/L)-(L**2-h**2)/(2*R_E*L))

        return etaZen**secZen
    
    def eta_Tot(self, L):
        """
        Computes total transmittance (the product of free space transmittance
        and atmospheric transmittance).

        Parameters:
        -----------
        L       : Distance between satellite and ground station (m)

        Returns:
        --------
        eta_tot     : Success probability due to all limitations
        """

        L_max = self.satellite["l_max"]

        if L < L_max:
            val = self.eta_sg(L)*self.eta_Atm(L)
            return val
        else:
            return 0.0
        
    def classical_comm(self, station, t):
        """
        Compute classical communication time for a ground station
        at a time t.

        Paraneters:
        -----------
        station     : A dictionary that contains all station info
        t           : The time being considered (s)

        Returns:
        --------
        cc_time     : The total time it takes for a single attempt
        """

        down = self.L_function(station, t)/c
        processing = 2*dt
        up = self.L_function(station, t+down+dt)/c

        return down + processing + up
    
    def region(self, t):
        """
        Checks to see where the satellite is in its orbit.

        Parameters:
        -----------
        t           : The time being considered (s)

        Returns:
        --------
        r           : Current region of the satellite
        """

        phi1_0 = self.ground_stations["station_1"]["phi_0"]
        phi2_0 = self.ground_stations["station_2"]["phi_0"]
        theta_0 = self.satellite["theta_0"]
        omega_s = self.satellite["omega"]

        t1 = (phi1_0 - theta_0) / (omega_s - omega_E)
        t2 = (phi2_0 - theta_0) / (omega_s - omega_E)

        if t <= t1:
            return 'r0'
        elif t > t2:
            return 'r2'
        else:
            return 'r1'
    
    def sort_gs(self, t):
        """
        Sorts ground stations by distance to satellite (furthest first).

        Parameters:
        -----------
        t           : The time being considered (s)

        Returns:
        --------
        sorted      : self.ground_stations sorted furthest first
        """

        return sorted(self.ground_stations.values(),
                      key=lambda gs: self.L_function(gs, t),
                      reverse=True)
        
    def simulate_comm(self):
        """
        Simulates communcation between satellite and ground stations.

        Returns:
        --------
        results     : A dictionary with a history of attempts.
        """

        L_max = self.satellite["l_max"]
        current_time = 1.0e-12
        end_time = self.visibility()

        results = []
        successful_stations = set()
        first_link_time = None

        # Making simulation condition
        while current_time < end_time:

            # Establishing which gs are visible
            gs_list = self.sort_gs(current_time)

            for station in gs_list:
                if self.L_function(station, current_time) >= L_max:
                    gs_list.remove(station)

            for station in gs_list:
                exit_for_loop = False

                while current_time < end_time:

                    # Checking to see if the ground stations have changed their arrangement
                    dummy = self.sort_gs(current_time)

                    for d_station in dummy:
                        if self.L_function(d_station, current_time) >= L_max:
                            dummy.remove(d_station)

                    if dummy != gs_list and len(successful_stations) == 0:
                        exit_for_loop = True
                        results.append({"result": "switch",
                                        "time": current_time})
                        break

                    # Making a communication attempt
                    comm_attempt = self.classical_comm(station, current_time)

                    if current_time + comm_attempt > end_time:
                        exit_for_loop = True
                        results.append({"station": station["name"],
                                        "result": "timeout",
                                        "time": current_time + comm_attempt})
                        return results

                    # Simulating a link
                    success_prob = self.eta_Tot(self.L_function(station, current_time+comm_attempt))
                    success = np.random.rand() < success_prob

                    if success:
                        results.append({"station": station["name"],
                                        "result": 1,
                                        "time": current_time})
                        successful_stations.add(station["name"])
                        current_time += comm_attempt

                        if len(successful_stations) == 1:
                            first_link_time = current_time

                        # Checking if all stations have successfully been linked
                        if len(successful_stations) == len(self.ground_stations):
                            elapsed_time = current_time - first_link_time
                            results.append({"result": "linked_both",
                                            "time": current_time,
                                            "elapsed_time": elapsed_time,
                                            "region": self.region(current_time)})
                                
                            # Reset successful stations
                            successful_stations.clear()
                            first_link_time = None
                            break

                        break
                    else:
                        # Keeping track of all failed attempts
                        results.append({"station": station["name"],
                                        "result": 0,
                                        "time": current_time})
                        current_time += comm_attempt

                    if current_time > end_time:
                        return results

                if exit_for_loop:
                    continue

        return results
