from random import *
from bisect import *
from statistics import *
from math import *

# Simulation parameters
Pf = 0.64  # probability of unsuccesfull transmittion
Ps = 1 -Pf #probability of succesfull transmittion
lamda = 0.7 #arrival rate
mu = 0.7 #we suppose that the service rate is equal to the arrival rate
ltp = 1 # Length of a timeout period (spacificly for each time out occurring)!!
n = 100000 # Number of simulated packets

# Unique ID for each event
evID = 0

# Count number of simulated packets
count = 0

# Count number of failed transsmit atemps
tr_atemps = 1

# maximoum atemps trial
max_atemps = 4

# Count number of succesfull transsmitions
suc_trans = 0

#length of buffers queue
L = 100

#coynt the number of the lost packets due to full buffer
lost_packets = 0

#count the number of the packet droped after 4 transmit failers
droped_packets = 0

# State variables
Q = 0
S = False  # Server is free

# Output variables
arrs = []
deps = [] #a packet departure when it losed or droped or recived

# Event list
evList = None #i avoid adding every single event that
# simulation have and instead used arrival and departure only. A departure event means that a packet
#no longer is in our system due to receive event or drop event. Also a loss event is not regarded as an event because
#it is not geting inside the system at all


# REG for the arrival event
def get_next_arrival_event(clock):
    global evID
    iat = expovariate(lamda)
    ev = (clock + iat, evID, arrival_event_handler)
    evID += 1
    return ev


# REG for the departure event
def get_next_departure_event(clock):
    global evID,tr_atemps,suc_trans,flag,ltp,droped_packets
    st = expovariate(mu) #the clasic service time
    added_time = 0 #aditional service time for the time out event
    tr_atemps = 1 #number of attemps server tried to transmit a packet
    flag = True
    while flag and tr_atemps <= max_atemps:
        probability_for_transmit = random()
        if probability_for_transmit < Ps:
            suc_trans += 1
            flag = False
        else:
            added_time += ltp
            tr_atemps += 1

    if flag == True:
        droped_packets += 1
    ev = (clock + st + added_time, evID, departure_event_handler)
    evID += 1
    return ev


# Event handler for the arrival event
def arrival_event_handler(clock):
    global n, count, Q, S, arrs
    Q += 1
    arrs.append(clock)  # Record arrival time
    if S == False:
        S = True
        schedule_event(get_next_departure_event(clock))
    count += 1
    if count < n:
        schedule_event(get_next_arrival_event(clock))



# Event handler for the departure event
def departure_event_handler(clock):
    global Q, S, deps
    Q -= 1
    deps.append(clock)  # Record departure time
    if Q == 0:
        S = False
    else:
        S = True
        schedule_event(get_next_departure_event(clock))



# Insert an event into the event list
def schedule_event(ev):
    global evList
    insort_right(evList, ev)


# Main simulation function
def sim():
    global Q, S, arrs, deps, count, evList, suc_trans, lost_packets,droped_packets
    droped_packets = 0
    suc_trans =0
    clock = 0
    evList = []
    lost_packets = 0

    # Reset state and output variables
    Q = 0
    S = False
    arrs = []
    deps = []
    count = 0

    # Insert initial events
    ev = get_next_arrival_event(clock)
    schedule_event(ev)

    # Start simulation
    while len(evList) > 0:
        ev = evList.pop(0)
        clock = ev[0]

        if Q >= L:
            if ev[2] == departure_event_handler:
                departure_event_handler(clock)
            if ev[2] == arrival_event_handler:#I make the hypothesis that when a packet is
                # being lost due to the full buffer the service time is zero !!!!!
                lost_packets += 1
                count += 1
                if count < n:
                    schedule_event(get_next_arrival_event(clock))
        else:
            ev[2](clock)


def main():
    global arrs, deps
    m = 50  # Number of replications
    Samples = []
    suc=[]
    a=[]
    lp = []
    dp=[]
    for i in range(m):
        d = []
        seed(i)  # Reseed RNG
        sim()
        d = list(map(lambda x, y: x - y, deps, arrs))
        dp.append(droped_packets)
        lp.append(lost_packets)
        suc.append(suc_trans)
        a.append(len(arrs))
        Samples.append(mean(d))


    droped_packets_mean = mean(dp)
    lost_packets_mean = mean(lp)
    succesfull_received_mean = mean(suc)
    packets_in_system_mean = mean(a)

    sample_mean = mean(Samples)
    sample_std_dev = stdev(Samples)

    t = {"80%": 1.282, "90%": 1.645, "95%": 1.960, "98%": 2.326}  # validity levels

    for val_level in t:
        ci1 = sample_mean - t[val_level] * (sample_std_dev / sqrt(m))
        ci2 = sample_mean + t[val_level] * (sample_std_dev / sqrt(m))
        print("Confidence Interval for validity level",val_level,"is:", "(", round(ci1, 2), ",", round(ci2, 2), ")")


    print("Average Delay of a packet that whent through the system = ", round(sample_mean, 4))
    print("Standard deviation for delay is:", round(sample_std_dev, 4))

    print("Presentage of the susscefull received packets compered to the packets that went to the system:",
          round((succesfull_received_mean / packets_in_system_mean)*100, 4), "%")
    print("Presentage of the susscefull received packets compered to the total number of packets that was simulated:",
          round((succesfull_received_mean / n)*100, 4), "%")
    print("Presentage of the lost packets due to full buffer:",
          round((lost_packets_mean / n) * 100, 4), "%")
    print("Presentage of the droped packets due to 4 unsucefull transmit atemps:",
          round((droped_packets_mean / n) * 100, 4), "%")
    print("Population Mean = ", round((pow(0.64,4) * 4 + pow(0.64*1,3)*3 + pow(0.64*1,2)*2 +pow(0.64*1,1)), 2))

if __name__ == '__main__':
    main()





