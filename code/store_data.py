import numpy as np
import pandas as pd

def combine(all_outcomes):
    combined = {}
    stats = {}
    success = {}

    for key in all_outcomes[0]:
        combined[key] = []

    for _, outcome in all_outcomes.items():
        for key in outcome:
            if isinstance(outcome[key], list):
                combined[key].extend(outcome[key])
            else:
                combined[key].append(outcome[key])

    for var, values in combined.items():
        data = np.array(values, dtype=float)

        if var == 'fla':
            fla = data
        elif var == "success_times":
            data = np.floor(data).astype(int)

            success = data
        elif var == "success_regions":
            for r in range(3):
                region_vals = data[r::3]
                ravg = np.mean(region_vals)
                rstd = np.std(region_vals,  ddof=1)
                rstderr = rstd / np.sqrt(region_vals.size)

                stats[f"success_region_{r}_mean"] = ravg
                stats[f"success_region_{r}_std"] = rstd
                stats[f"success_region_{r}_stderr"] = rstderr
        else:
            stats[str(var)+"_mean"] = np.mean(data)
            stats[str(var)+"_std"] = np.std(data, ddof=1)
            stats[str(var)+"_stderr"] = np.std(data, ddof=1) / np.sqrt(len(data))

    df_success_times = pd.DataFrame(success)
    df_stats = pd.DataFrame([stats])
    df_fla = pd.DataFrame(fla)

    return stats, success, fla
    