[Corresponding Medium article](#https://medium.com/@jonathan.mandt/upsamping-trajectory-data-with-google-directions-api-969adf4e176?sk=0b8978942c4ecec2f7bc9773b5c78678)

## Upsampling Trajectory data

### Table of Contents

- [Summaray](#summary)
- [Getting Started](#getting-started)


### Summary
Plotting trajectorial data has always one crucial requirement. 
The ability to accurately plot this data always depends on how far apart two consecutive coordinates are from each other, both in time and space.

The T-Drive data set contains 17,662,250 GPS points, which were recorded within Beijing from February the 2nd to February the 8th 2008, representing the trajectories of 10,357 different taxi drivers. 
For each taxi there is a text file containing the whole trajectory of the vehicle.
The average sampling rate is one data point every 177 seconds considering all trajectories of all taxis in the greater area of Beijing. 
As recording rates vary a lot, we filtered those, where the time gap between two consecutive points was greater than 30 seconds. 
The figure above shows a heat map of the remaining points with recording rate less than 30 seconds. 
The colors intensify with the number of taxis being in the same area, whereby blue indicates areas with fewer taxis and red implies areas with a very high number of taxis.
You can download the whole T-Drive dataset here.

So every 177 seconds is not a very high density of datapoints. In order to be able to simulate Taxi drives through Beijing you would need a much higher density. 
Thats where Googles Direction API comes into play. I used it to find in between point between to consecutive GPS coordinates if the time delta in between them was less than 30 seconds.

### Getting Started
* clone the repo
* get an API key for Google directions API
* export environmental variable or directly paste it in
* run the code