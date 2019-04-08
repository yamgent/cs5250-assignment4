import sys

class Process:
    '''
    A process as defined in the input text file.
    '''

    def __init__(self, id, arrival_time, burst_time):
        self.id = id
        self.arrival_time = arrival_time
        self.burst_time = burst_time

    def __repr__(self):
        '''
        For printing purposes.
        '''

        return '[id %d: arrival_time %d, burst_time %d]' % (self.id, self.arrival_time, self.burst_time)

def FCFS_scheduling(process_list):
    '''
    Scheduling process_list on first come first serve basis.
    '''

    # store the (switching time, proccess_id) pair
    schedule = []
    current_time = 0
    waiting_time = 0

    for process in process_list:        
        if current_time < process.arrival_time:
            current_time = process.arrival_time

        schedule.append((current_time, process.id))
        waiting_time = waiting_time + (current_time - process.arrival_time)
        current_time = current_time + process.burst_time

    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time


# input: process_list, time_quantum (Positive Integer)
# output_1: Schedule list contains pairs of (time_stamp, proccess_id) indicating the time switching to that proccess_id
# output_2: Average Waiting Time
def RR_scheduling(process_list, time_quantum):
    '''
    Scheduling process_list on round robin policy with time_quantum.
    '''

    return (['To be completed, scheduling process_list on round robin policy with time_quantum.'], 0.0)


def SRTF_scheduling(process_list):
    '''
    Scheduling process_list on SRTF, using process.burst_time to calculate the remaining time of the current process.
    '''

    return (['To be completed, scheduling process_list on SRTF, using process.burst_time to calculate the remaining time of the current process.'], 0.0)


def SJF_scheduling(process_list, alpha):
    '''
    Scheduling SJF without using information from process.burst_time.
    '''

    return (['To be completed, scheduling SJF without using information from process.burst_time.'], 0.0)


def read_input(input_txt_path):
    '''
    Read each process listed in the input.txt and returns
    a list of corresponding Process.
    '''

    result = []

    with open(input_txt_path, 'r') as f:
        for line in f:
            line_vals = [int(x) for x in line.split()]

            if len(line_vals) != 3:
                print('Invalid format! Expected 3 numbers in a line.')
                exit()

            result.append(Process(line_vals[0], line_vals[1], line_vals[2]))

    return result


def write_output(output_txt_path, schedule, avg_waiting_time):
    '''
    Write the result of a particular simulation.
    '''

    with open(output_txt_path, 'w') as f:
        for item in schedule:
            f.write(str(item) + '\n')
        f.write('Average waiting time %.2f \n'%(avg_waiting_time))


def run_simulators(folder_path):
    '''
    Read the list of processes and run each simulation.
    '''

    input_txt_path = folder_path + '/input.txt'
    process_list = read_input(input_txt_path)

    print('printing input ----')
    for process in process_list:
        print(process)

    print('simulating FCFS ----')
    FCFS_schedule, FCFS_avg_waiting_time = FCFS_scheduling(process_list)
    write_output(folder_path + '/FCFS.txt', FCFS_schedule, FCFS_avg_waiting_time)

    print('simulating RR ----')
    RR_schedule, RR_avg_waiting_time = RR_scheduling(process_list, time_quantum = 2)
    write_output(folder_path + '/RR.txt', RR_schedule, RR_avg_waiting_time)

    print('simulating SRTF ----')
    SRTF_schedule, SRTF_avg_waiting_time = SRTF_scheduling(process_list)
    write_output(folder_path + '/SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time)

    print ('simulating SJF ----')
    SJF_schedule, SJF_avg_waiting_time = SJF_scheduling(process_list, alpha = 0.5)
    write_output(folder_path + '/SJF.txt', SJF_schedule, SJF_avg_waiting_time)


def main(argv):
    '''
    Main entry point of the application.
    '''

    process_name = argv[0]

    if len(argv) < 2:
        print('Please pass in the path of the folder containing input.txt.')
        print('Usage: python %s [path_to_folder]' % (process_name))
        exit()
    
    folder_path = argv[1]
    run_simulators(argv[1])


if __name__ == '__main__':
    main(sys.argv)
