from input import get_input, get_input_for_evaluate_all
from algorithms import sjf, fcfs, srtf, rr, npp, pp
from display import select_algorithm, display_results, display_gantt_chart, prompt_repeat_evaluation, banner, \
    exit_banner, evaluate_all_algorithms


def main():
    banner()
    while True:
        algorithm_name, algorithm = select_algorithm()
        if algorithm == 'exit':
            exit_banner()
            return

        # n, arrival_time, burst_time, time_quantum, priorities = get_input(algorithm)

        # all algo evaluated:
        if algorithm != 'evaluate_all':
            n, arrival_time, burst_time, time_quantum, priorities = get_input(algorithm)
            result = None
            if algorithm == 'fcfs':
                result = fcfs(arrival_time, burst_time)
            elif algorithm == 'sjf':
                result = sjf(arrival_time, burst_time)
            elif algorithm == 'srtf':
                result = srtf(arrival_time, burst_time)
            elif algorithm == 'rr':
                result = rr(arrival_time, burst_time, time_quantum)
            elif algorithm == 'npp':
                result = npp(arrival_time, burst_time, priorities)
            elif algorithm == 'pp':
                result = pp(arrival_time, burst_time, priorities)

            if result:
                display_results(result['solved_processes_info'], algorithm_name)
                display_gantt_chart(result['gantt_chart_info'])
        else:
            n, arrival_time, burst_time, time_quantum, priorities = get_input_for_evaluate_all()
            evaluate_all_algorithms(arrival_time, burst_time, time_quantum, priorities)
        while True:
            try:
                repeat_choice = prompt_repeat_evaluation()
                if repeat_choice not in [1, 2]:
                    raise ValueError
                break
            except ValueError:
                print("Invalid input, please try again.")

        if repeat_choice == 2:
            exit_banner()
            break


if __name__ == '__main__':
    main()
