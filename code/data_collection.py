import os,sys,time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from simulation import simulate
from analyze import analyze_results
from store_data import combine

def main():
    # Defining the satellite altitudes
    alt = np.arange(5e6, 10.5e6, 5e5)

    # Defining ground station separation
    sep = np.arange(5e5, 2.5e6, 5e5)

    # Number of orbits for simulation
    n = 500

    general = time.time()
    k = 0

    for h in alt:

        start_time, overall = time.strftime("%H:%M:%S", time.localtime()), time.time()
        print(f"\n\nStarting {h} ({k + 1}/{len(alt)}) at {start_time} ({overall - general:.1f} s)")
        print("-"*70)
        sys.stdout.flush()
        k += 1

        # Establising simulation instance for satellite altitude h
        sim = simulate(h)

        folder = os.path.join("..", "data", str(h))
        os.makedirs(folder, exist_ok=True)

        all = {}
        stats = {}
        times = {}
        fla = {}
        m = 0

        for d in sep:
            all[d] = {}
            current, start = time.strftime("%H:%M:%S", time.localtime()), time.time()
            print(f"Starting {d} ({m + 1}/{len(sep)}) at {start_time} ({start - overall:.1f} s)")
            print("-  "*23)
            sys.stdout.flush()
            for j in range(n):

                # Setting initial conditions
                sim.initial_conditions(d)

                # Running simulation and analyzing results
                all[d][j] = analyze_results(sim.simulate_comm())

                if (j+1) % (n/50) == 0:
                    current, end = time.strftime("%H:%M:%S", time.localtime()), time.time()
                    print(f"{j+1:03}/{n} done for {d} ({m+1}/{len(sep)}) @ {current} ({end - start:.1f} s)")
                    sys.stdout.flush()

            stats[d], times[d], fla[d] = combine(all[d])

            m += 1

        pd.DataFrame(stats).to_csv(os.path.join(folder, f"{h}-stats.csv"), index=False)
        pd.DataFrame.from_dict(times, orient="index") \
            .to_csv(os.path.join(folder, f"{h}-times.csv"))
        pd.DataFrame.from_dict(fla, orient="index") \
            .to_csv(os.path.join(folder, f"{h}-fla.csv"))
        
if __name__ == "__main__":
    main()