import json

import os
from datetime import datetime


def get_unique_first_five_chars(_folder_path):
    """
    This function retrieves the first 5 characters of all filenames in a folder and returns a list
    of unique strings.

    Args:
        _folder_path: The path to the folder containing the files.

    Returns:
        A list of unique strings representing the first 5 characters of filenames.
    """
    unique_first_five = set()
    for filename in os.listdir(_folder_path):
        first_five = filename[:5]  # Get the first 5 characters
        unique_first_five.add(first_five)  # Add to set for uniqueness

    return list(unique_first_five)  # Convert set back to list


def list_files(_start_name):
    """
    This function returns a list of filenames starting with "asd" in the current directory.

     Args:
        _start_name: A string representing the start of the name of files to include in the return.

    Returns:
        A list of strings representing filenames starting with _start_name.
    """
    asd_files = []
    for filename in os.listdir("perf_results"):
        if filename.startswith(_start_name):
            asd_files.append("perf_results/" + filename)
    return asd_files


def average_benchmark_results(_filenames):
    """
    This function takes a list of filenames and calculates the average of a specific benchmark
    metric within the JSON files.

    Args:
        _filenames: A list of strings representing the filenames of the JSON files.

    Returns:
        A float representing the average value of the benchmark metric or None if there's an error.
    """

    averages = {}
    units = {}
    parameters = []
    runtimes = []
    test_name = ""
    for index, filename in enumerate(_filenames):
        try:
            with open(filename) as f:
                data_string = f.read()
                data = json.loads(data_string)

            if index == 0:
                parameters = data["parameters"]
                test_name = data["id"]

            start_time_str = data["startTime"]
            finish_time_str = data["finishTime"]

            date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
            start_time = datetime.strptime(start_time_str, date_format)
            finish_time = datetime.strptime(finish_time_str, date_format)
            runtime = (finish_time - start_time).total_seconds()
            runtimes.append(runtime)

            for result in data["results"]:
                result_id = result["id"]
                if result_id not in averages:
                    averages[result_id] = []
                try:
                    averages[result_id].append(result["data"])
                except KeyError as _:
                    averages[result_id].append(result["stats"]["average"])

                if result_id not in units:
                    units[result_id] = result["units"]

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error processing {filename}: {e}")
            return None

    for _key, _value in averages.items():
        averages[_key] = sum(_value) / len(_value)

    average_runtime = sum(runtimes) / len(runtimes)

    # Return dictionary with averages and parameters
    return {"test_name": test_name, "units": units, "averages": averages, "parameters": parameters,
            "average_runtime": average_runtime}


folder_path = "perf_results"
filename_start = "ConditionalMutationsPT_10000_"

filenames = list_files(filename_start)
results = average_benchmark_results(filenames)

print(f"----------Test name: {results['test_name']}----------")

print(f"Average runtime (seconds): {results['average_runtime']}")
print("Average Results:")
for key, value in results["averages"].items():
    print(f"\t{key}: {value} {results['units'][key]}")
print("Parameters:")
for param in results["parameters"]:
    print(f"\t{param['id']}: {param['data']}")
