import pandas as pd


def sjf(arrival_time, burst_time):
    # Create a fresh DataFrame each time sjf is called
    processes_info = pd.DataFrame({
        'job': [f'P{i + 1}' if len(arrival_time) > 26 else chr(65 + i) for i in range(len(arrival_time))],
        "at": arrival_time,
        "bt": burst_time
    }).sort_values(by=["at", "bt"]).reset_index(drop=True)

    gantt_chart_info = []
    ready_queue = []
    finished_jobs = []
    solved_processes = []  # List to hold finished process info

    current_time = processes_info.iloc[0]['at']  # Start at the arrival time of the first process
    while len(finished_jobs) < len(arrival_time):
        # Populate the ready queue with processes that have arrived
        for _, process in processes_info.iterrows():
            if process['at'] <= current_time and process['job'] not in ready_queue and process[
                 'job'] not in finished_jobs:
                ready_queue.append(process['job'])

        if not ready_queue:
            current_time += 1  # Increment time if the ready queue is empty
            continue

        # Select the next process with the shortest burst time from the ready queue
        next_process_job = min(ready_queue, key=lambda x: processes_info[processes_info['job'] == x]['bt'].iloc[0])

        # Get process info
        process_row = processes_info[processes_info['job'] == next_process_job].iloc[0]
        start_time = max(current_time, process_row['at'])
        finish_time = start_time + process_row['bt']

        # Append to gantt_chart_info
        gantt_chart_info.append({
            "job": next_process_job,
            "start": start_time,
            "stop": finish_time
        })

        # Append to solved_processes list
        solved_processes.append({
            "job": next_process_job,
            "at": process_row['at'],
            "bt": process_row['bt'],
            "ft": finish_time,
            "tat": finish_time - process_row['at'],
            "wat": start_time - process_row['at']
        })

        # Update ready_queue and finished_jobs
        ready_queue.remove(next_process_job)
        finished_jobs.append(next_process_job)

        # Move forward in time
        current_time = finish_time

    # Convert solved_processes list to DataFrame and sort
    solved_processes_df = pd.DataFrame(solved_processes)
    solved_processes_df = solved_processes_df.sort_values(by=["ft", "job"]).reset_index(drop=True)

    return {"solved_processes_info": solved_processes_df.to_dict('records'), "gantt_chart_info": gantt_chart_info}


def fcfs(arrival_time, burst_time):
    processes_info = pd.DataFrame({
        'job': [f'P{i + 1}' if len(arrival_time) > 26 else chr(65 + i) for i in range(len(arrival_time))],
        'at': arrival_time,
        'bt': burst_time
    }).sort_values(by='at').reset_index(drop=True)

    finish_time = []
    gantt_chart_info = []

    for idx, (index, process) in enumerate(processes_info.iterrows()):
        if idx == 0 or process['at'] > finish_time[idx - 1]:
            finish_time.append(process['at'] + process['bt'])
            gantt_chart_info.append({'job': process['job'], 'start': process['at'], 'stop': finish_time[idx]})
        else:
            finish_time.append(finish_time[idx - 1] + process['bt'])
            gantt_chart_info.append(
                {'job': process['job'], 'start': finish_time[idx - 1], 'stop': finish_time[idx]})

        processes_info.at[index, 'ft'] = finish_time[idx]
        processes_info.at[index, 'tat'] = finish_time[idx] - process['at']
        processes_info.at[index, 'wat'] = finish_time[idx] - process['at'] - process['bt']

    return {'solved_processes_info': processes_info, 'gantt_chart_info': gantt_chart_info}


def srtf(arrival_time, burst_time):
    processes_info = sorted(
        [
            {
                "job": f"P{index + 1}" if len(arrival_time) > 26 else chr(65 + index),
                "at": at,
                "bt": bt,
            }
            for index, (at, bt) in enumerate(zip(arrival_time, burst_time))
        ],
        key=lambda x: (x["at"], x["bt"]),
    )

    solved_processes_info = []
    gantt_chart_info = []

    ready_queue = []
    current_time = processes_info[0]["at"]
    unfinished_jobs = processes_info.copy()

    remaining_time = {process["job"]: process["bt"] for process in processes_info}

    ready_queue.append(unfinished_jobs.pop(0))
    while any(remaining_time.values()) and unfinished_jobs:
        prev_idle = False
        if not ready_queue and unfinished_jobs:
            prev_idle = True
            ready_queue.append(unfinished_jobs.pop(0))

        ready_queue.sort(key=lambda x: remaining_time[x["job"]])

        process_to_execute = ready_queue[0]

        process_at_less_than_bt = [
            p
            for p in processes_info
            if p["at"] <= remaining_time[process_to_execute["job"]] + (
                process_to_execute["at"] if prev_idle else current_time)
            and p != process_to_execute
            and p not in ready_queue
            and p in unfinished_jobs
        ]

        got_interruption = False
        for p in process_at_less_than_bt:
            if prev_idle:
                current_time = process_to_execute["at"]

            amount = p["at"] - current_time

            if current_time >= p["at"]:
                ready_queue.append(p)

            if p["bt"] < remaining_time[process_to_execute["job"]] - amount:
                remaining_time[process_to_execute["job"]] -= amount
                ready_queue.append(p)
                prev_current_time = current_time
                current_time += amount
                gantt_chart_info.append(
                    {"job": process_to_execute["job"], "start": prev_current_time, "stop": current_time}
                )

                got_interruption = True
                break

        process_to_arrive = [
            p
            for p in processes_info
            if p["at"] <= current_time
            and p != process_to_execute
            and p not in ready_queue
            and p in unfinished_jobs
        ]

        ready_queue.extend(process_to_arrive)

        if not got_interruption:
            remaining_t = remaining_time[process_to_execute["job"]]
            remaining_time[process_to_execute["job"]] -= remaining_t
            current_time += remaining_t if not prev_idle else (process_to_execute["at"] + remaining_t - current_time)

            for p in process_at_less_than_bt:
                if current_time >= p["at"] and p not in ready_queue:
                    ready_queue.append(p)

            gantt_chart_info.append(
                {"job": process_to_execute["job"], "start": current_time - remaining_t, "stop": current_time}
            )

        ready_queue.append(ready_queue.pop(0))

        if remaining_time[process_to_execute["job"]] == 0:
            if process_to_execute in unfinished_jobs:
                unfinished_jobs.remove(process_to_execute)
            if process_to_execute in ready_queue:
                ready_queue.remove(process_to_execute)

            solved_processes_info.append(
                {
                    **process_to_execute,
                    "ft": current_time,
                    "tat": current_time - process_to_execute["at"],
                    "wat": current_time - process_to_execute["at"] - process_to_execute["bt"],
                }
            )

    solved_processes_info.sort(key=lambda x: (x["at"], x["job"]))

    return {"solved_processes_info": solved_processes_info, "gantt_chart_info": gantt_chart_info}


def rr(arrival_time, burst_time, time_quantum):
    processes_info = sorted([
        {'job': f"P{index + 1}" if len(arrival_time) > 26 else chr(65 + index),
         'at': at,
         'bt': bt}
        for index, (at, bt) in enumerate(zip(arrival_time, burst_time))
    ], key=lambda x: x['at'])

    solved_processes_info = []
    gantt_chart_info = []
    ready_queue = []
    current_time = processes_info[0]['at']
    unfinished_jobs = processes_info.copy()
    remaining_time = {process['job']: process['bt'] for process in processes_info}

    ready_queue.append(unfinished_jobs[0])
    while any(remaining_time.values()) and unfinished_jobs:
        if not ready_queue and unfinished_jobs:
            ready_queue.append(unfinished_jobs[0])
            current_time = ready_queue[0]['at']

        process_to_execute = ready_queue[0]

        if remaining_time[process_to_execute['job']] <= time_quantum:
            remaining_t = remaining_time[process_to_execute['job']]
            remaining_time[process_to_execute['job']] -= remaining_t
            prev_current_time = current_time
            current_time += remaining_t

            gantt_chart_info.append({
                'job': process_to_execute['job'],
                'start': prev_current_time,
                'stop': current_time
            })
        else:
            remaining_time[process_to_execute['job']] -= time_quantum
            prev_current_time = current_time
            current_time += time_quantum

            gantt_chart_info.append({
                'job': process_to_execute['job'],
                'start': prev_current_time,
                'stop': current_time
            })

        process_to_arrive_in_this_cycle = [
            p for p in processes_info
            if p['at'] <= current_time and
            p != process_to_execute and
            p not in ready_queue and
            p in unfinished_jobs
        ]

        ready_queue.extend(process_to_arrive_in_this_cycle)
        ready_queue.append(ready_queue.pop(0))

        if remaining_time[process_to_execute['job']] == 0:
            unfinished_jobs.remove(process_to_execute)
            ready_queue.remove(process_to_execute)

            solved_processes_info.append({
                **process_to_execute,
                'ft': current_time,
                'tat': current_time - process_to_execute['at'],
                'wat': current_time - process_to_execute['at'] - process_to_execute['bt']
            })

    solved_processes_info.sort(key=lambda x: (x['at'], x['job']))
    # Include time_quantum in the solved_processes_info dictionary
    solved_processes_info.append({'Time Quantum': time_quantum})
    return {'solved_processes_info': solved_processes_info, 'gantt_chart_info': gantt_chart_info}


def npp(arrival_time, burst_time, priorities):
    processes_info = sorted(
        [
            {
                "job": f"P{index + 1}" if len(arrival_time) > 26 else chr(index + 65),
                "at": at,
                "bt": burst_time[index],
                "priority": priorities[index],
            }
            for index, at in enumerate(arrival_time)
        ],
        key=lambda x: (x["at"], x["priority"]),
    )

    gantt_chart_info = []
    solved_processes_info = []
    ready_queue = []
    finished_jobs = []

    current_time = 0
    while len(finished_jobs) < len(processes_info):
        # Add processes to the ready queue that have arrived
        for process in processes_info:
            if process["at"] <= current_time and process not in ready_queue and process not in finished_jobs:
                ready_queue.append(process)

        # Sort the ready queue by priority, then by arrival time
        rq_sorted_by_priority = sorted(
            ready_queue, key=lambda x: (x["priority"], x["at"])
        )

        if rq_sorted_by_priority:
            process_to_execute = rq_sorted_by_priority[0]
            start_time = max(current_time, process_to_execute["at"])
            finish_time = start_time + process_to_execute["bt"]
            gantt_chart_info.append(
                {
                    "job": process_to_execute["job"],
                    "start": start_time,
                    "stop": finish_time,
                }
            )
            solved_processes_info.append(
                {
                    **process_to_execute,
                    "ft": finish_time,
                    "tat": finish_time - process_to_execute["at"],
                    "wat": start_time - process_to_execute["at"],
                }
            )
            current_time = finish_time
            ready_queue.remove(process_to_execute)
            finished_jobs.append(process_to_execute)
        else:
            current_time += 1

    # Sort the processes by job name within arrival time
    solved_processes_info.sort(key=lambda x: (x["at"], x["job"]))

    return {"solved_processes_info": solved_processes_info, "gantt_chart_info": gantt_chart_info}


def pp(arrival_time, burst_time, priorities):
    processes_info = sorted(
        [{'job': f"P{index + 1}" if len(arrival_time) > 26 else chr(index + 65),
          'at': at, 'bt': bt, 'priority': priority}
         for index, (at, bt, priority) in enumerate(zip(arrival_time, burst_time, priorities))],
        key=lambda x: (x['at'], x['priority'])
    )

    solved_processes_info = []
    gantt_chart_info = []

    ready_queue = []
    current_time = processes_info[0]['at']
    unfinished_jobs = processes_info.copy()

    remaining_time = {process['job']: process['bt'] for process in processes_info}

    ready_queue.append(unfinished_jobs[0])

    while any(remaining_time.values()) and unfinished_jobs:
        prev_idle = False
        if not ready_queue and unfinished_jobs:
            prev_idle = True
            ready_queue.append(unfinished_jobs[0])

        ready_queue.sort(key=lambda x: x['priority'])

        process_to_execute = ready_queue[0]

        process_at_less_than_bt = [p for p in processes_info if p['at'] <= remaining_time[process_to_execute[
            'job']] + current_time and p != process_to_execute and p not in ready_queue and p in unfinished_jobs]
        got_interruption = False

        for p in process_at_less_than_bt:
            if prev_idle:
                current_time = process_to_execute['at']

            amount = p['at'] - current_time

            if current_time >= p['at']:
                ready_queue.append(p)

            if p['priority'] < process_to_execute['priority']:
                remaining_time[process_to_execute['job']] -= amount
                ready_queue.append(p)
                prev_current_time = current_time
                current_time += amount
                gantt_chart_info.append(
                    {'job': process_to_execute['job'], 'start': prev_current_time, 'stop': current_time})
                got_interruption = True
                break

        process_to_arrive = [p for p in processes_info if p[
            'at'] <= current_time and p != process_to_execute and p not in ready_queue and p in unfinished_jobs]

        ready_queue.extend(process_to_arrive)

        if not got_interruption:
            if prev_idle:
                remaining_t = remaining_time[process_to_execute['job']]
                remaining_time[process_to_execute['job']] -= remaining_t
                current_time = process_to_execute['at'] + remaining_t

                for p in process_at_less_than_bt:
                    if current_time >= p['at']:
                        ready_queue.append(p)

                gantt_chart_info.append(
                    {'job': process_to_execute['job'], 'start': process_to_execute['at'], 'stop': current_time})
            else:
                remaining_t = remaining_time[process_to_execute['job']]
                remaining_time[process_to_execute['job']] -= remaining_t
                prev_current_time = current_time
                current_time += remaining_t

                for p in process_at_less_than_bt:
                    if current_time >= p['at'] and p not in ready_queue:
                        ready_queue.append(p)

                gantt_chart_info.append(
                    {'job': process_to_execute['job'], 'start': prev_current_time, 'stop': current_time})

        ready_queue.append(ready_queue.pop(0))

        if remaining_time[process_to_execute['job']] == 0:
            unfinished_jobs.remove(process_to_execute)
            if process_to_execute in ready_queue:
                ready_queue.remove(process_to_execute)

            solved_processes_info.append({
                **process_to_execute,
                'ft': current_time,
                'tat': current_time - process_to_execute['at'],
                'wat': current_time - process_to_execute['at'] - process_to_execute['bt']
            })

    solved_processes_info.sort(key=lambda x: (x['at'], x['job']))

    return {'solved_processes_info': solved_processes_info, 'gantt_chart_info': gantt_chart_info}
