
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib 


def baseflow_separator(date_vector, flow_vector, plotme=False, Station_name=None):
   
    N = 5                     # averaging window, number of days
    tp_test_factor = 0.9      # turning point test factor     (If 90 percent of a given minimum (the “turning point test factor”) is less than both adjacent minimums, then that minimum is a turning point.)
                                                                              # eill be final processed dictionary of dataframes
    Site=[]; SumTotal=[]; SumBF=[]; SumRO=[]; AveTotal=[]; AveBF=[]; AveRO=[]; BFTF=[]; ROTF=[]  # lists for sumary dataframe

    mean_dates = []; mins = []; means = []
    for i in range(1,len(date_vector)-N,N):                         # mikes code, still not sure I understand it all
        N_day_data = []
        for j in range(0,N-1):
            N_day_data.append(float(flow_vector[i+j]))
        mean_dates.append(date_vector[i+(N//2)])
        mean_point = [date_vector[i+(N//2)]]
        N_day_mean = np.mean(N_day_data)
        mean_point.append(N_day_mean)
        means.append(mean_point)
        min_point = [date_vector[i+(N//2)]]
        N_day_min = np.min(N_day_data)
        min_point.append(N_day_min)
        mins.append(min_point)

    turning_points = []; tp_dates = []; tp_flow = []; sf_dates = []; sf_flow = [];     # mikes code, still not sure I understand it all
    for i in range(0,len(mins)-1,1):
        if (tp_test_factor*(mins[i][1]))<mins[i+1][1] and (tp_test_factor*(mins[i][1]))<mins[i-1][1]:
            turning_points.append(mins[i])
            tp_dates.append(mins[i][0])
            tp_flow.append(mins[i][1])

    keyname = 'Total_flow_{}'.format(Station_name)         
            
    Total_flows = pd.DataFrame({'Date': date_vector, keyname: flow_vector })
    Baseflows = pd.DataFrame({'Date': tp_dates, 'Base_flow_CFS': tp_flow })  
    All_flows = Total_flows.merge(Baseflows, how='outer', on='Date')                     # final dataframe with separated values of flow
    All_flows['Base_flow_CFS'].interpolate(inplace=True)                                 # baseflows were only calculated at turning points. here linearly interpolate to give a value for each day
    All_flows['Runoff_CFS'] = All_flows[keyname] - All_flows['Base_flow_CFS']
    All_flows['Runoff_CFS'] = All_flows['Runoff_CFS'].clip(lower=0)    # convert any negative runoff values to zero

    RO_mean = All_flows['Runoff_CFS'].mean()
    BF_mean = All_flows['Base_flow_CFS'].mean()
    TF_mean = All_flows[keyname].mean()   
    
    # plot stuff
    if plotme == True:
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.plot(All_flows['Date'],All_flows[keyname], '-',label='Total daily flow', marker='.')
        ax.plot(All_flows['Date'],All_flows['Base_flow_CFS'], '-',label='Baseflow', marker='.')
        ax.set_title("Baseflow separated Streamflow at {}".format(Station_name))
        ax.legend()
        plt.ylabel('Discharge (CFS)')

        plt.xticks(rotation=20)
        plt.tight_layout()
        
    #print("Ave.RO = {:.2f}, Ave.BF = {:.2f}, Ave.TF = {:.2f}".format(RO_mean, BF_mean, TF_mean))

    return All_flows, RO_mean, BF_mean, TF_mean