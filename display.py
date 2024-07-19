import pandas as pd
from rich import box
from rich.console import Console
from rich.text import Text
from rich.table import Table
from algorithms import fcfs, sjf, srtf, rr, npp, pp

console = Console()


def select_algorithm():
    table = Table(title="⧗ CPU Scheduling Menu ⧗", title_style="bold italic bright_cyan", show_header=True,
                  header_style="bold italic bright_green", style="cyan", box=box.ASCII_DOUBLE_HEAD, show_lines=True)

    # Add columns to the table
    table.add_column("Choices", style="bold italic yellow", no_wrap=True, justify="center")
    table.add_column("Algorithm", style="bold italic yellow", no_wrap=True, justify="center")

    # Add rows to the table
    print("\n")
    menu = [
        ("1", "First Come First Serve (FCFS)"),
        ("2", "Shortest Job First (SJF)"),
        ("3", "Shortest Remaining Time First (SRTF)"),
        ("4", "Round Robin (RR)"),
        ("5", "Non-Preemptive Priority (NPP)"),
        ("6", "Preemptive Priority (PP)"),
        ("7", "Evaluate All"),
        ("8", "Exit")
    ]

    for choice, algorithm in menu:
        table.add_row(choice, algorithm)

    # Print the table
    console.print(table)

    while True:
        try:
            print("\n")
            choice_text = Text("Enter your choice (1-8): ", style="bold italic #FF9021 ")
            console.print(choice_text, end='')
            choice = int(input())
            if 1 <= choice <= 8:
                break
            else:
                raise ValueError
        except ValueError:
            console.print(Text("Invalid input, please try again.", style="bold italic bright_red"))

    algorithm_names = {
        'fcfs': "First Come First Serve (FCFS)",
        'sjf': "Shortest Job First (SJF)",
        'srtf': "Shortest Remaining Time First (SRTF)",
        'rr': "Round Robin (RR)",
        'npp': "Non-Preemptive Priority (NPP)",
        'pp': "Preemptive Priority (PP)",
        'evaluate_all': "Evaluate All Algorithms",
        'exit': "Exit"
    }
    algorithm_key = ['fcfs', 'sjf', 'srtf', 'rr', 'npp', 'pp', 'evaluate_all', 'exit'][choice - 1]
    return algorithm_names[algorithm_key], algorithm_key

def display_results(solved_processes_info, algorithm_name):
    print("\n")
    # Convert DataFrame to list of dictionaries if it's not already
    if isinstance(solved_processes_info, pd.DataFrame):
        solved_processes_info = solved_processes_info.to_dict(orient='records')

    # Check for 'Time Quantum' in the last dictionary
    time_quantum = None
    if 'Time Quantum' in solved_processes_info[-1]:
        time_quantum = solved_processes_info[-1]['Time Quantum']
        solved_processes_info.pop(-1)  # Remove the Time Quantum dictionary

    df = pd.DataFrame(solved_processes_info)
    # Rename columns as necessary
    df = df.rename(columns={
        'job': 'Process',
        'at': 'AT',
        'bt': 'BT',
        'ft': 'FT',
        'tat': 'TT',
        'wat': 'WT',
        'priority':'Priority'
    })

    # If 'Priority' column exists, include it
    if 'Priority' in df.columns:
        columns_order = ['Process', 'AT', 'BT', 'Priority', 'FT', 'TT', 'WT']
        df = df[columns_order]
    else:
        df.drop(columns=['Priority'], errors='ignore', inplace=True)

    # Calculate sums and averages
    sum_tt = df['TT'].sum()
    sum_wat = df['WT'].sum()
    count_processes = len(df)
    avg_tat = sum_tt / count_processes if count_processes else 0
    avg_wat = sum_wat / count_processes if count_processes else 0

    # Initialize table
    table = Table(title=f"⧗ {algorithm_name} Algorithm Results ⧗",
                  title_style="bold italic bright_cyan",
                  header_style="bold bright_green",
                  style="cyan", box=box.ASCII_DOUBLE_HEAD, show_lines=True)

    # Add columns to table
    for column in df.columns:
        table.add_column(column, justify="center")

    # Add rows to table
    for _, row in df.iterrows():
        table.add_row(*[Text(str(value), style="bold italic yellow") for value in row])

    # Prepare the last row for quantum time and averages
    bottom_row = [Text('')] * (len(df.columns) - 3)  # Placeholder for columns before 'FT'

    # Add Quantum Time at the beginning of the bottom row
    if time_quantum is not None:
        bottom_row[0] = Text(f"Quantum: {time_quantum}", style="bold italic bright_green")

    # Append the averages to the bottom row
    bottom_row.extend([
        Text('Average:', style="bold italic bright_green"),
        Text(f"{avg_tat:.2f}", style="bold italic bright_green"),
        Text(f"{avg_wat:.2f}", style="bold italic bright_green")
    ])

    # Add the bottom row to the table
    table.add_row(*bottom_row)

    # Print the table
    console.print(table)


def display_gantt_chart(gantt_chart_info, scale=0, padding=10, max_blocks_per_line=7):
    # Sort the info by start time just in case
    gantt_chart_info = sorted(gantt_chart_info, key=lambda x: x['start'])

    # Break gantt_chart_info into chunks of max_blocks_per_line
    chunks = [gantt_chart_info[i:i + max_blocks_per_line] for i in range(0, len(gantt_chart_info), max_blocks_per_line)]
    console.print("\n ⧗ Gantt Chart ⧗", style="bold italic bright_cyan")
    for chunk in chunks:
        # Find the last time mark for the chunk
        last_time = max(info['stop'] for info in chunk)

        # Generate the top border of the chart for the chunk
        border = " +" + "+".join(
            "-" * int((info['stop'] - info['start']) * scale + padding - 1) for info in chunk) + "+"
        console.print(Text(border, style="bold cyan"))

        # Track positions of plus signs
        plus_positions = [i for i, char in enumerate(border) if char == '+']

        # Generate the middle part of the chart with process names
        middle_parts = []
        for info in chunk:
            job_text = Text(info['job'], style="bold #FF9021")
            total_width = int((info['stop'] - info['start']) * scale + padding - 1)
            left_padding = (total_width - len(info['job'])) // 2
            right_padding = total_width - len(info['job']) - left_padding
            middle_parts.append(Text(' ' * left_padding) + job_text + Text(' ' * right_padding))
        middle = Text(" |", style="bold cyan") + Text("|", style="bold cyan").join(middle_parts) + Text("|",
                                                                                                        style="bold cyan")
        console.print(middle)

        # Print the border again
        console.print(Text(border, style="bold cyan"))

        # Generate the line with start and stop times aligned with the plus signs
        times_line = ""
        for i, info in enumerate(chunk):
            # Calculate the number of spaces needed before the start time
            if i == 0:  # First position aligns with the start of the chart
                start_spaces = 1
            else:
                start_spaces = plus_positions[i] - len(times_line) - len(str(info['start'])) + 1

            # Append the start time with the correct alignment
            times_line += " " * start_spaces + str(info['start'])

        # Append the last stop time
        last_stop_spaces = len(border) - len(times_line) - len(str(last_time))  # Adjustment here
        times_line += " " * last_stop_spaces + str(last_time)

        console.print(Text(times_line, style="bold yellow"))
        print()  # Add a newline for spacing between chunks


def prompt_repeat_evaluation():
    print("\n")
    table = Table(title="⧗ Evaluate Another Algorithm? ⧗", title_style="bold italic bright_cyan",
                  header_style="bold italic bright_green",
                  style="cyan", box=box.ASCII_DOUBLE_HEAD, show_lines=True)

    # Add columns to the table
    table.add_column("Choices", style="bold italic yellow", no_wrap=True, justify="center")
    table.add_column("Yes or No ?", style="bold italic yellow", no_wrap=True, justify="center")

    # Add rows to the table
    menu = [
        ("1", "Yes"),
        ("2", "No")
    ]

    for choice, option in menu:
        table.add_row(choice, option)

    # Print the table
    console.print(table)

    while True:
        try:
            choice_text = Text("\nEnter your choice (1-2): ", style="bold italic #FF9021")
            console.print(choice_text, end='')
            repeat_choice = int(input())
            if repeat_choice in [1, 2]:
                return repeat_choice
            else:
                raise ValueError
        except ValueError:
            console.print(Text("Invalid input, please try again.", style="bold italic bright_red"))


def evaluate_all_algorithms(arrival_time, burst_time, time_quantum, priorities):
    # FCFS
    fcfs_result = fcfs(arrival_time, burst_time)
    # console.print("\n[bold magenta]First Come First Serve (FCFS):[/bold magenta]")
    display_results(fcfs_result['solved_processes_info'], "First Come First Serve (FCFS)")
    display_gantt_chart(fcfs_result['gantt_chart_info'])

    # SJF
    sjf_result = sjf(arrival_time, burst_time)
    # console.print("\n[bold magenta]Shortest Job First (SJF):[/bold magenta]")
    display_results(sjf_result['solved_processes_info'], "Shortest Job First (SJF)")
    display_gantt_chart(sjf_result['gantt_chart_info'])

    # SRTF
    srtf_result = srtf(arrival_time, burst_time)
    # console.print("\n[bold magenta]Shortest Remaining Time First (SRTF):[/bold magenta]")
    display_results(srtf_result['solved_processes_info'], "Shortest Remaining Time First (SRTF)")
    display_gantt_chart(srtf_result['gantt_chart_info'])

    # Round Robin
    rr_result = rr(arrival_time, burst_time, time_quantum)
    # console.print("\n[bold magenta]Round Robin (RR):[/bold magenta]")
    display_results(rr_result['solved_processes_info'], "Round Robin (RR)")
    display_gantt_chart(rr_result['gantt_chart_info'])

    # Non-Preemptive Priority
    npp_result = npp(arrival_time, burst_time, priorities)
    # console.print("\n[bold magenta]Non-Preemptive Priority (NPP):[/bold magenta]")
    display_results(npp_result['solved_processes_info'], "Non-Preemptive Priority (NPP)")
    display_gantt_chart(npp_result['gantt_chart_info'])

    # Preemptive Priority
    pp_result = pp(arrival_time, burst_time, priorities)
    # console.print("\n[bold magenta]Preemptive Priority (PP):[/bold magenta]")
    display_results(pp_result['solved_processes_info'], "Preemptive Priority (PP)")
    display_gantt_chart(pp_result['gantt_chart_info'])

    # Collect results in a dictionary
    all_results = {
        'First Come First Serve (FCFS)': fcfs_result['solved_processes_info'],
        'Shortest Job First (SJF)': sjf_result['solved_processes_info'],
        'Shortest Remaining Time First (SRTF)': srtf_result['solved_processes_info'],
        'Round Robin (RR)': rr_result['solved_processes_info'],
        'Non-Preemptive Priority (NPP)': npp_result['solved_processes_info'],
        'Preemptive Priority (PP)': pp_result['solved_processes_info']
    }

    # Get all averages and display them
    get_all_averages(all_results)

# def get_all_averages(results_dict):
#     print("\n")
#     averages_list = []
#
#     # Iterate through each algorithm result and calculate the averages
#     for algo_name, solved_info in results_dict.items():
#         df = pd.DataFrame(solved_info)
#         avg_tt = df['tat'].mean()  # Average Turnaround Time
#         avg_wt = df['wat'].mean()  # Average Waiting Time
#         averages_list.append((algo_name, avg_tt, avg_wt))
#
#     # Sort the list of averages by Average Turnaround Time, then by Average Waiting Time
#     averages_list.sort(key=lambda x: (x[1], x[2]))
#
#     # Create a Rich Table
#
#     table = Table(title="⧗ Algorithm Fastest to Slowest ⧗", title_style="bold italic bright_cyan",
#                   header_style="bold bright_green", style="cyan", box=box.ASCII_DOUBLE_HEAD, show_lines=True)
#
#     table.add_column("Algorithm", style="dim")
#     table.add_column("Average TT", justify="right")
#     table.add_column("Average WT", justify="right")
#
#     # Add the rows to the table
#     for algo_name, avg_tt, avg_wt in averages_list:
#         # Create Text objects with styles
#         algo_text = Text(algo_name, style="bold bright_yellow")
#         avg_tt_text = Text(f"{avg_tt:.2f}", style="bold yellow")
#         avg_wt_text = Text(f"{avg_wt:.2f}", style="bold yellow")
#
#         # Add the row with styled Text objects
#         table.add_row(algo_text, avg_tt_text, avg_wt_text)
#
#     # Print the table
#     console.print(table)
def get_all_averages(results_dict):
    print("\n")
    averages_list = []

    # Iterate through each algorithm result and calculate the averages
    for algo_name, solved_info in results_dict.items():
        df = pd.DataFrame(solved_info)
        total_busy_time = df['bt'].sum()  # Total Busy Time
        total_time = max(df['ft']) - min(df['at'])  # Total Time
        cpu_utilization = (total_busy_time / total_time) * 100 if total_time > 0 else 0

        avg_tt = df['tat'].mean()  # Average Turnaround Time
        avg_wt = df['wat'].mean()  # Average Waiting Time

        averages_list.append((algo_name, avg_tt, avg_wt, cpu_utilization))

    # Sort the list of averages by Average Turnaround Time, then by Average Waiting Time
    averages_list.sort(key=lambda x: (x[1], x[2]))

    # Create a Rich Table
    table = Table(title="⧗ Algorithm Fastest to Slowest ⧗",
                  title_style="bold italic bright_cyan",
                  header_style="bold bright_green",
                  style="cyan", box=box.ASCII_DOUBLE_HEAD, show_lines=True)

    table.add_column("Algorithm", style="dim")
    table.add_column("Average TT", justify="right")
    table.add_column("Average WT", justify="right")
    table.add_column("CPU Utilization", justify="right")

    # Add the rows to the table
    for algo_name, avg_tt, avg_wt, cpu_util in averages_list:
        algo_text = Text(algo_name, style="bold bright_yellow")
        avg_tt_text = Text(f"{avg_tt:.2f}", style="bold yellow")
        avg_wt_text = Text(f"{avg_wt:.2f}", style="bold yellow")
        cpu_util_text = Text(f"{cpu_util:.2f}%", style="bold yellow")

        table.add_row(algo_text, avg_tt_text, avg_wt_text, cpu_util_text)

    # Print the table
    console.print(table)


def banner():
    font = """
   
    
         ██████╗██████╗ ██╗   ██╗   ████████╗██╗███╗   ███╗███████╗
        ██╔════╝██╔══██╗██║   ██║   ╚══██╔══╝██║████╗ ████║██╔════╝
        ██║     ██████╔╝██║   ██║█████╗██║   ██║██╔████╔██║█████╗  
        ██║     ██╔═══╝ ██║   ██║╚════╝██║   ██║██║╚██╔╝██║██╔══╝  
        ╚██████╗██║     ╚██████╔╝      ██║   ██║██║ ╚═╝ ██║███████╗
         ╚═════╝╚═╝      ╚═════╝       ╚═╝   ╚═╝╚═╝     ╚═╝╚══════╝
                                                           
         ███████╗██╗  ██╗██████╗ ██████╗ ███████╗███████╗███████╗   
         ██╔════╝╚██╗██╔╝██╔══██╗██╔══██╗██╔════╝██╔════╝██╔════╝   
         █████╗   ╚███╔╝ ██████╔╝██████╔╝█████╗  ███████╗███████╗   
         ██╔══╝   ██╔██╗ ██╔═══╝ ██╔══██╗██╔══╝  ╚════██║╚════██║   
         ███████╗██╔╝ ██╗██║     ██║  ██║███████╗███████║███████║   
         ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝   
    _+===========_+_================_+_=============_+_=============+_ 
                     Angelo Valdez & Mikael Aggarao                       
                OS Project Ver. 1 - All rights reserved 
                            S.Y. 2023-2024 
                                  ⧗⧗⧗
                              
                                
    """
    # table = Table(show_header=False, box=box.DOUBLE)
    # table.add_row(Text(font, style="bold italic bright_cyan"))
    #
    # console.print(table)
    console.print(Text(font, style="bold italic bright_cyan"))


def exit_banner():
    font = """

           o x o x o x o x Departing ... . . . ..
         o      _____            _______________ ___=====__T___
       .][__n_n_|DD[  ====_____  |    |.\/.|   | |   |_|     |_
      >(________|__|_[_________]_|____|_/\_|___|_|___________|_|
      _/oo OOOOO oo`  ooo   ooo   o^o       o^o   o^o     o^o
-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+




"""
    # | ￣￣￣￣￣￣￣￣￣￣￣￣￣ |
    # | Farewell ! |
    # | ＿＿＿＿＿＿＿＿＿＿＿＿＿ |
    # `\ // // / `
    # \(•v•) /
    # \ /
    # —————
    # | |
    # | _ | _

    console.print(Text(font, style="bold bright_cyan"))


def compare_results():
    return
