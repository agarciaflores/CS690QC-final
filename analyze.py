def analyze_results(results):
    """
    Analyzes the simulation results to determine the
    number of success resets during the elapsed time.
    It also keeps track of the number of attempts it takes to
    successfully link with the second ground station.
      
    Parameters:
    -----------
    results     : list of dictionary simulation results 
                  containing 'station', 'result', and 'time'.

    Returns:
    --------
    data        : A dictionary containing all the statistics.
    """

    # Initialize variables for data tracking
    data = {
        # Computing the total elapsed time in simulation (sanity check)
        "elapsed_time": results[-1]["time"] - results[0]["time"],

        # Number of times the system successfully linked
        "success_resets": 0,

        # Keeping track of when the success happened
        "success_times": [],

        # Keeping track of where the success happened
        "success_regions": [0, 0, 0]
    }

    # Number of attempts it took to link with second gs
    second_station = 0

    # Empty list to store all values of attempts to link
    # with first gs
    second_station_attempts = [[], [], []]

    # Empty list to store all values of times it took to
    # link with second gs
    second_station_times = [[], [], []]
    raw_times = []

    # Track the current iteration
    current_iteration = []

    for entry in results:
        if entry.get('result') == 'linked_both':
            # Update ticker
            data["success_resets"] += 1

            region = entry.get('region')
            index = int(region[-1])
            data["success_regions"][index] += 1
            data["success_times"].append(entry.get('time'))

            for iteration_entry in current_iteration:
                if iteration_entry.get('station') == current_iteration[-1]["station"]:
                    # Update second gs attempts
                    second_station += 1

            # Add second gs attempts to list
            second_station_attempts[index].append(second_station)

            # Keep track of how much time it took to link with second gs
            second_station_times[index].append(entry.get("elapsed_time"))
            raw_times.append(entry.get("elapsed_time"))

            # Resetting for next iteration
            current_iteration = []
            second_station = 0
        elif entry.get('result') == 'switch':
            # Resetting for next iteration
            current_iteration = []
        else:
            # Storing information for attempt tracking
            current_iteration.append(entry)

    # Finding averages & errors for second gs attempts
    data["second_station_attempts_r0"] = second_station_attempts[0]
    data["second_station_attempts_r1"] = second_station_attempts[1]
    data["second_station_attempts_r2"] = second_station_attempts[2]

    # Finding averages & errors for times for first gs
    data["second_station_times_r0"] = second_station_times[0]
    data["second_station_times_r1"] = second_station_times[1]
    data["second_station_times_r2"] = second_station_times[2]

    data["fla"] = raw_times

    return data