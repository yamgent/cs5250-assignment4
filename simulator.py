import sys

NO_JOB = -1

class Process:
    '''
    A process as defined in the input text file.
    '''

    def __init__(self, id, arrival_time, burst_time):
        assert arrival_time >= 0
        assert burst_time >= 0

        self.id = id
        self.arrival_time = arrival_time
        self.burst_time = burst_time


    def __repr__(self):
        '''
        For printing purposes.
        '''

        return '[id %d: arrival_time %d, burst_time %d]' % (self.id, self.arrival_time, self.burst_time)


    def spawn_job(self, current_time):
        '''
        Create a new job associated with this process.
        '''
        
        assert current_time >= self.arrival_time
        return Job(self.id, self.arrival_time, self.burst_time, current_time - self.arrival_time, self.burst_time)


class Job:
    '''
    Describes a job scheduled for the CPU.
    '''

    def __init__(self, id, arrival_time, remaining_time, waiting_time, burst_time):
        assert arrival_time >= 0
        assert remaining_time >= 0
        assert waiting_time >= 0
        assert burst_time >= 0

        self.id = id
        self.arrival_time = arrival_time
        self.remaining_time = remaining_time
        self.waiting_time = waiting_time
        self.burst_time = burst_time

    
    def add_waiting_time(self, waiting_duration):
        '''
        Called when this job is NOT the current active one, add the waiting
        time by the waiting duration.
        '''
        
        assert waiting_duration >= 0
        self.waiting_time += waiting_duration


    def substract_remaining_time(self, processing_duration):
        '''
        Called when this job is the current active one, substract the 
        remaining time by the processing duration.
        '''

        assert processing_duration >= 0
        self.remaining_time -= min(processing_duration, self.remaining_time)

    
    def is_done(self):
        '''
        Is the job completed?
        '''

        return self.remaining_time <= 0


class JobReceiver:
    '''
    When probed, returns the new list of jobs that have arrived at the
    particular current time.

    Note: process_list must be in order of arrival time!
    '''

    def __init__(self, process_list):
        assert process_list is not None

        self.process_list = process_list
        self.next_new_job_index = 0

    
    def all_jobs_received(self):
        '''
        Are there no more jobs in the queue?
        '''

        return self.next_new_job_index >= len(self.process_list)


    def peek_next_process(self):
        '''
        Peek at the next process in the queue (Note: it may not
        have arrived yet! Need to check arrival_time <= current_time).
        '''

        if self.all_jobs_received():
            return None

        return self.process_list[self.next_new_job_index]


    def receive_new_jobs(self, current_time):
        '''
        Returns the list of new jobs at the current time.
        '''

        result = []

        if self.all_jobs_received():
            # no more jobs
            return result
        
        while (not self.all_jobs_received()) and self.peek_next_process().arrival_time <= current_time:
            # a new job has arrived
            result.append(self.peek_next_process().spawn_job(current_time))
            self.next_new_job_index += 1

        return result


class Cpu:
    '''
    Maintains the state of a simulated CPU.
    '''

    def __init__(self, process_list):
        self.current_time = 0
        self.remaining_jobs = []
        self.completed_jobs = []
        self.current_running_job_index = NO_JOB
        self.job_receiver = JobReceiver(process_list)
        self.schedule = []
        self.job_completed_event_callback = None


    def set_job_completed_event_callback(self, callback):
        '''
        Set the callback function that we should call when a job is completed.
        This callback should accept a parameter for a job object.
        '''

        self.job_completed_event_callback = callback


    def get_current_running_job(self):
        '''
        Get the current job.
        '''

        if self.current_running_job_index == NO_JOB:
            return None
        return self.remaining_jobs[self.current_running_job_index]


    def switch_to_job_with_index(self, new_job):
        '''
        Switch to the new job (given its index).
        '''

        # don't bother switching if it is the same job
        if self.current_running_job_index == new_job:
            return

        self.current_running_job_index = new_job
        if self.current_running_job_index != NO_JOB:
            self.schedule.append((self.current_time, self.get_current_running_job().id))


    def switch_to_job_with_object(self, new_job_object):
        '''
        Switch to the new job (given the particular object representation of the job).
        '''

        assert new_job_object in self.remaining_jobs

        for i in range(0, len(self.remaining_jobs)):
            if self.remaining_jobs[i] == new_job_object:
                self.switch_to_job_with_index(i)
                return

        assert False  # cannot find the object, something gone VERY wrong


    def wait_until_new_job_arrives(self):
        '''
        Called when there's no job in the CPU, wait until
        the new job arrives from JobReceiver.
        '''

        assert len(self.remaining_jobs) == 0
        assert not self.job_receiver.all_jobs_received()

        next_arrival_time = self.job_receiver.peek_next_process().arrival_time
        self.move_current_time_to(next_arrival_time)


    def increment_current_time(self, duration):
        '''
        Increment current time by given amount.
        '''
        self.move_current_time_to(self.current_time + duration)


    def move_current_time_to(self, new_time):
        '''
        Move the current time forward to new_time.

        What happens when time is moved forward?
            1. update all waiting job's waiting time
            2. update the current running job's remaining time
            3. put the current running job to the completed queue if it is done
            4. receive new jobs (if any)
            5. update current_time to be the new_time
        '''
        assert self.current_time <= new_time

        delta = new_time - self.current_time
        current_running_job = self.get_current_running_job()

        # 1. update all waiting job's waiting time
        for job in self.remaining_jobs:
            if job == current_running_job:
                continue
            job.add_waiting_time(delta)

        # 2. update the current running job's remaining time
        if current_running_job is not None:
            current_running_job.substract_remaining_time(delta)
            
            # 3. put the current running job to the completed queue if it is done
            if current_running_job.is_done():
                self.remaining_jobs.remove(current_running_job)
                self.completed_jobs.append(current_running_job)

                if self.job_completed_event_callback is not None:
                    self.job_completed_event_callback(current_running_job)

                self.switch_to_job_with_index(NO_JOB)
                current_running_job = None

        # 4. receive new jobs (if any)
        new_jobs = self.job_receiver.receive_new_jobs(new_time)
        for j in new_jobs:
            self.remaining_jobs.append(j)

        # 5. update current_time to be the new_time
        self.current_time = new_time


    def is_completely_done(self):
        '''
        Are we completely done with everything, such that
        all job_receiver's jobs are all processed?
        '''

        return self.job_receiver.all_jobs_received() and len(self.remaining_jobs) <= 0

    
    def get_average_waiting_time_for_completed_jobs(self):
        '''
        Get the average waiting time for all completed jobs.
        '''

        return float(sum([j.waiting_time for j in self.completed_jobs])) / float(len(self.completed_jobs))

    
    def has_remaining_jobs(self):
        '''
        Does this CPU still have remaining jobs to run?
        '''

        return len(self.remaining_jobs) > 0


def FCFS_scheduling(process_list):
    '''
    Scheduling process_list on first come first serve basis.
    '''

    cpu = Cpu(process_list)

    while not cpu.is_completely_done():
        if not cpu.has_remaining_jobs():
            cpu.wait_until_new_job_arrives()

        cpu.switch_to_job_with_index(0)
        cpu.increment_current_time(cpu.get_current_running_job().remaining_time)

    return cpu.schedule, cpu.get_average_waiting_time_for_completed_jobs()


# input: process_list, time_quantum (Positive Integer)
# output_1: Schedule list contains pairs of (time_stamp, proccess_id) indicating the time switching to that proccess_id
# output_2: Average Waiting Time
def RR_scheduling(process_list, time_quantum):
    '''
    Scheduling process_list on round robin policy with time_quantum.
    '''

    cpu = Cpu(process_list)
    
    while not cpu.is_completely_done():
        if cpu.get_current_running_job() is None:
            if not cpu.has_remaining_jobs():
                cpu.wait_until_new_job_arrives()

            cpu.switch_to_job_with_index(0)

        else:
            current_job_index = cpu.current_running_job_index
            time_spent_for_current_job = min(time_quantum, cpu.get_current_running_job().remaining_time)
            job_will_finish = (time_spent_for_current_job == cpu.get_current_running_job().remaining_time)

            cpu.increment_current_time(time_spent_for_current_job)

            if cpu.has_remaining_jobs():
                next_job_index = (current_job_index + 1) % len(cpu.remaining_jobs)
                if job_will_finish:
                    # finished job is removed on the spot, so the next job is the same spot
                    next_job_index = (current_job_index) % len(cpu.remaining_jobs)

                cpu.switch_to_job_with_index(next_job_index)

    return cpu.schedule, cpu.get_average_waiting_time_for_completed_jobs()


def SRTF_scheduling(process_list):
    '''
    Scheduling process_list on SRTF, using process.burst_time to calculate the remaining time of the current process.
    '''

    cpu = Cpu(process_list)

    while not cpu.is_completely_done():
        if not cpu.has_remaining_jobs():
            cpu.wait_until_new_job_arrives()
            cpu.switch_to_job_with_index(0)
        
        # find the smallest remaining time job and switch to it
        smallest_remaining_time_job = cpu.remaining_jobs[0]
        for j in cpu.remaining_jobs:
            if j.remaining_time < smallest_remaining_time_job.remaining_time:
                smallest_remaining_time_job = j
        cpu.switch_to_job_with_object(smallest_remaining_time_job)

        # determine how long to run it ...
        time_spent = smallest_remaining_time_job.remaining_time

        # ... if no new job arrives before job completion, then just run to job to completion.
        # Otherwise, we must only run till the next job arrives, in case the next job
        # changes the candidate for the shortest remaining time left
        next_job_in_queue = cpu.job_receiver.peek_next_process()
        if next_job_in_queue is not None:
            duration_before_next_job_arrives = next_job_in_queue.arrival_time - cpu.current_time
            time_spent = min(time_spent, duration_before_next_job_arrives)

        # now actually run it
        cpu.increment_current_time(time_spent)

    return cpu.schedule, cpu.get_average_waiting_time_for_completed_jobs()


def SJF_scheduling(process_list, alpha):
    '''
    Scheduling SJF without using information from process.burst_time.
    '''
    
    cpu = Cpu(process_list)
    
    # set up prediction table
    prediction = { }
    all_process_ids = [p.id for p in process_list]
    for i in all_process_ids:
        prediction[i] = 5

    # hook up a prediction update function
    def update_prediction(completed_job):
        prediction[completed_job.id] = (alpha * completed_job.burst_time) + ((1 - alpha) * prediction[completed_job.id])
    cpu.set_job_completed_event_callback(update_prediction)

    while not cpu.is_completely_done():
        if not cpu.has_remaining_jobs():
            cpu.wait_until_new_job_arrives()
            cpu.switch_to_job_with_index(0)

        # find the best job to run based on predictions
        best_job_to_run = cpu.remaining_jobs[0]
        for j in cpu.remaining_jobs:
            if prediction[j.id] < prediction[best_job_to_run.id]:
                best_job_to_run = j
        
        cpu.switch_to_job_with_object(best_job_to_run)
        cpu.increment_current_time(best_job_to_run.remaining_time)


    return cpu.schedule, cpu.get_average_waiting_time_for_completed_jobs()


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

    # note: each scheduler reloads the process_list in case it is contaminated
    # by the previous scheduling algorithm's execution.

    print('simulating FCFS ----')
    process_list = read_input(input_txt_path)
    FCFS_schedule, FCFS_avg_waiting_time = FCFS_scheduling(process_list)
    write_output(folder_path + '/FCFS.txt', FCFS_schedule, FCFS_avg_waiting_time)

    print('simulating RR ----')
    process_list = read_input(input_txt_path)
    RR_schedule, RR_avg_waiting_time = RR_scheduling(process_list, time_quantum = 2)
    write_output(folder_path + '/RR.txt', RR_schedule, RR_avg_waiting_time)

    print('simulating SRTF ----')
    process_list = read_input(input_txt_path)
    SRTF_schedule, SRTF_avg_waiting_time = SRTF_scheduling(process_list)
    write_output(folder_path + '/SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time)

    print ('simulating SJF ----')
    process_list = read_input(input_txt_path)
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
