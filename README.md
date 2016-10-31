Jepson Research 2014-2015 @UMW
===============
### A Nearest-Neighbor Algorithm for Response-Maximizing Interaction Design in Social Outreach Campaigns

This project contains some of the code developed as part of a Jepson Fellowship at UMW during the 2014-15 year.
This research aimed to make social media outreach campaigns more effective through designing tailored interactions
for each user which increase the probability of a desired response. An interaction may contain many aspects
including (for example) a specific message or theme, tone, media channel through which the interaction occurs,
sender or message author, time sent, and many others. In this work a nearest-neighbor algorithm was developed
to determine the best interaction designs for each user by using historical data containing user information and 
response patterns. Interactions are designed in such a way as to maximize the probability of a desired response.

This method was tested in a set of simulation experiments which vary three user population factors based on a 2^3 
factorial design. The scenario parameter files and results are also contained in this repository. For convenience,
a batch file is included. 

#### Usage

The core algorithm is contained in the [knn.py](https://github.com/chrisgarcia001/Jepson-2014-2015/blob/master/knn.py).
This algorithm is based on the k-nearest-neighbor algorithm used in machine learning classification.
The core representations are as follows:

##### Users, Interaction Designs, and Responses 
Each user is represented as a list of feature values (e.g. [age, location, political party, ...]), and each 
interaction design (message for short) is likewise a list feature values (e.g. [theme, tone, media channel, ...]).
A response is either 0 or 1, where 1 indicates that a user responded as desired to the interaction and 0 indicates
that they didn't. Each data row is a tuple of form (user, interaction, response).

##### Similarity Functions
A similarity function is a function which takes two users as input and returns a numeric value indicating how
similar the two are. The key property necessary is that the similarity score will be higher for two users
who are more similar.

##### Mode-Weighting Functions
In many cases the users nearer to a specific user should carry more weight in determining how to design
an interaction than those further away. A weighting function can be used to weight the choice of 
different interaction attributes in proportion to the similarity. A weighting function simply takes a
number as input (presumably a similaity measure) and returns a weight.

##### Example
Here is a simple example of how to construct and run the algorithm:

```python
from knn import *  # Import the algorithm module

op = KNNOptimizer() # Initialize algorithm

# Get historic data from somewhere:
historic_data = get_data() # data is of form [(user, interaction, response), ....]
op.set_data_rows(historic_data) # Set data rows

# A similarity function takes 2 users and returns a number:
op.set_similarity_f(my_similarity_func) 

# Build a simple weighting function which treats all neighbors equally:
att_selector_f = build_weighted_mode_selector(lambda x: 1)

# Get list of users to build interactions for from somewhere:
current_users = get_current_users()  

k = 10 # Set number of nearest neighbors to use - many strategies for setting this.

# Get the optimal interaction designs for each of the current users:
interactions = map(lambda user: op.optimize(user, k, att_selector_f), current_users)
...

```

#### Paper and Citation
The full paper can be found [here.](http://www.emeraldinsight.com/doi/abs/10.1108/K-09-2015-0236)
If you wish to cite this work, please use the following reference:
Christopher Garcia, "A nearest-neighbor algorithm for targeted interaction design in social outreach campaigns", Kybernetes, Vol. 45 Iss: 8, pp.1243 - 1256.

#### License
This is licensed under the Apache License Version 2.0.