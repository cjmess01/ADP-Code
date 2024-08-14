def process_harmonic(buffer_mag, buffer_phase, harmonic, frequency, sample_multiplier):
    search_range = int(frequency)
    if(frequency < 10):
        search_range = 2
    
    begin = int(sample_multiplier*(harmonic) - (search_range //2) )           #define begin as the location in the spectrum of where we will begin
    maximum = -100
    maxloc = 0


    #print(begin)
    # import matplotlib.pyplot as plt
    # plt.plot(buffer_mag)
    # plt.plot(buffer_phase)
    # plt.show()
    # plt.plot(buffer_mag[begin:(begin+(search_range))])
    # plt.plot(buffer_phase[begin:(begin+(search_range))], color='red')
    # plt.show()

    for q in range(search_range):
        searchloc = ((begin+q)) #set the current search location within the spectrum
        int(searchloc)
        if searchloc> len(buffer_mag):    #if our search location is outside the length of the spectrum, abort
            continue
        if buffer_mag[searchloc] > maximum:   #if the magnitude of the spectrum is greater than what we have seen, reset the max
            maximum = buffer_mag[searchloc]
            maxloc = searchloc

    harmonic_magnitude = maximum
    harmonic_phase = buffer_phase[maxloc]

    # maximum = -100
    # for q in range(search_range):
    #     searchloc = ((begin+q)) #set the current search location within the spectrum
    #     int(searchloc)
    #     if searchloc> len(buffer_phase):    #if our search location is outside the length of the spectrum, abort
    #         continue
    #     if buffer_phase[searchloc] > maximum:   #if the magnitude of the spectrum is greater than what we have seen, reset the max
    #         maximum = buffer_phase[searchloc]
    #         maxloc = searchloc
    # harmonic_phase = buffer_phase[maxloc]
    print(f"Freq: {frequency}\nHarm: {harmonic}")
    print(harmonic_magnitude)
    print(harmonic_phase)
    print("")

    return harmonic_magnitude, harmonic_phase




