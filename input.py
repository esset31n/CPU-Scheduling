from rich import box
from rich.console import Console
from rich.table import Table
from rich.text import Text

console = Console()


def get_input(algorithm):
    # Create a table for the inputs
    input_table = Table(title="⧗ CPU Scheduling Input ⧗", title_style="bold italic bright_cyan",
                        header_style="bold italic bright_green",
                        style="cyan", box=box.ASCII_DOUBLE_HEAD, show_lines=True)

    input_table.add_column("Description", style="bold italic yellow", no_wrap=True)
    input_table.add_column("Input", style="bold italic yellow")

    # Get number of processes
    while True:
        try:
            n = int(console.input(Text("Enter the number of processes: ", style="bold italic #CB6D0F")))
            if n <= 0:
                raise ValueError
            input_table.add_row("Number of processes", str(n))
            break
        except ValueError:
            console.print(Text("Invalid input, please try again.", style="bold italic bright_red"))

    # Get arrival times
    while True:
        try:
            arrival_time = list(
                map(int, console.input(Text("Enter arrival time: ", style="bold italic #BD5E00")).split()))
            if len(arrival_time) != n:
                raise ValueError
            input_table.add_row("Arrival time", ' '.join(map(str, arrival_time)))
            break
        except ValueError:
            console.print(Text("Invalid input, please try again.", style="bold italic bright_red"))

    # Get burst times
    while True:
        try:
            burst_time = list(map(int, console.input(Text("Enter burst time: ", style="bold italic #A45200")).split()))
            if len(burst_time) != n:
                raise ValueError
            input_table.add_row("Burst time", ' '.join(map(str, burst_time)))
            break
        except ValueError:
            console.print(Text("Invalid input, please try again.", style="bold italic bright_red"))

    time_quantum = None
    priorities = None

    # Get time quantum for Round Robin
    if algorithm == 'rr':
        while True:
            try:
                time_quantum = int(console.input(Text("Enter time quantum: ", style="bold italic #894500")))
                if time_quantum <= 0:
                    raise ValueError
                input_table.add_row("Time quantum", str(time_quantum))
                break
            except ValueError:
                console.print(Text("Invalid input, please try again.", style="bold italic bright_red"))

    # Get priorities for NPP and PP
    if algorithm in ['npp', 'pp']:
        while True:
            try:
                priorities = list(map(int, console.input(Text("Enter priorities: ", style="bold #894500")).split()))
                if len(priorities) != n:
                    raise ValueError
                input_table.add_row("Priorities", ' '.join(map(str, priorities)))
                break
            except ValueError:
                console.print(Text("Invalid input, please try again.", style="bold italic bright_red"))

    # Print the input table
    print("\n")
    console.print(input_table)

    return n, arrival_time, burst_time, time_quantum, priorities


def get_input_for_evaluate_all():
    # Create a table for the inputs
    input_table = Table(title="⧗ CPU Scheduling Input ⧗", title_style="bold italic bright_cyan",
                        header_style="bold italic bright_green",
                        style="cyan", box=box.ASCII_DOUBLE_HEAD, show_lines=True)

    input_table.add_column("Description", style="bold italic yellow", no_wrap=True)
    input_table.add_column("Input", style="bold italic yellow")
    # Get number of processes
    while True:
        try:
            n = int(console.input(Text("Enter the number of processes: ", style="bold italic #CB6D0F")))
            if n <= 0:
                raise ValueError("Number of processes must be positive.")
            input_table.add_row("Number of processes", str(n))
            break
        except ValueError:
            console.print(Text("Invalid input, please try again.", style="bold italic bright_red"))
    # Get arrival times
    while True:
        try:
            arrival_time = list(map(int, console.input(Text("Enter arrival time: ", style="bold italic #BD5E00")).split()))
            if len(arrival_time) != n:
                raise ValueError("Number of arrival times must match the number of processes.")
            input_table.add_row("Arrival time", ' '.join(map(str, arrival_time)))
            break
        except ValueError:
            console.print(Text("Invalid input, please try again.", style="bold italic bright_red"))

    # Get burst times
    while True:
        try:
            burst_time = list(map(int, console.input(Text("Enter burst time: ", style="bold italic #A45200")).split()))
            if len(burst_time) != n:
                raise ValueError("Number of burst times must match the number of processes.")
            input_table.add_row("Burst time", ' '.join(map(str, burst_time)))
            break
        except ValueError:
            console.print(Text("Invalid input, please try again.", style="bold italic bright_red"))

    time_quantum = None
    priorities = None
    # Get time quantum for Round Robin
    if n > 1:
        while True:
            try:
                time_quantum = int(console.input(Text("Enter time quantum: ", style="bold italic #894500")))
                if time_quantum <= 0:
                    raise ValueError("Time quantum must be positive.")
                input_table.add_row("Time quantum", str(time_quantum))
                break
            except ValueError:
                console.print(Text("Invalid input, please try again.", style="bold italic bright_red"))

        while True:
            try:
                priorities = list(map(int, console.input(Text("Enter priorities: ", style="bold #894500")).split()))
                if len(priorities) != n:
                    raise ValueError("Number of priorities must match the number of processes.")
                input_table.add_row("Priorities", ' '.join(map(str, priorities)))
                break
            except ValueError:
                console.print(Text("Invalid input, please try again.", style="bold italic bright_red"))

    # Print the input table
    print("\n")
    console.print(input_table)
    return n, arrival_time, burst_time, time_quantum, priorities
