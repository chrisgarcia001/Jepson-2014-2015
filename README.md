Jepson Research 2014-2015 @UMW
===============
### A Nearest-neighbor algorithm for response-maximizing interaction designs in social outreach campaigns

This project contains some of the code developed as part of a Jepson Fellowship at UMW during the 2014-15 year.
This research aimed to make social media outreach campaigns more effective through designing tailored interactions
for each user which increase the probability of a desired response. An interaction may contain many aspects
including (for example) a specific message or theme, tone, media channel through which the interaction occurs,
sender or message author, time sent, and many others. In this work a nearest-neighbor algorithm was developed
to determine the best interaction designs for each user by using historical data containing user information and 
response patterns. Interactions are designed in such a way as to maximize the probability of a desired response.

This method was tested in a set of simulation experiments which vary three user population factors based on a 2^3 
factorial design. The scenario parameter files and results are also contained in this repository. For convenience,
a batch file is included 

# Usage

The core algorithm is contained in the [knn.py]
