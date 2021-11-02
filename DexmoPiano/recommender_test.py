import numpy as np
import pandas as pd
from surprise import Reader
from surprise import Dataset
from surprise import SVD
from surprise import accuracy
from surprise.model_selection import train_test_split

#get data
# Creation of the dataframe. Column names are irrelevant.



# extract one proficiency profile (1 user, 1 session)

iterables = [["x", "y","z"], [1,2,3,4], [(2,3,2), (2,3,1), (3,3,1)]]
index = pd.MultiIndex.from_product(iterables, names=["user", "session", "params"])

df = pd.DataFrame (np.random.randn(len(index)), index=index)

ratings_dict={ 'itemID': [], 'userID': [], 'rating': []}

for multi_index in index:

    userID = multi_index[0]+str(multi_index[1])
    param = multi_index[2]

    m=multi_index
    err = df.loc[m]
    ratings_dict['itemID'].append(param)
    ratings_dict['userID'].append(userID)
    ratings_dict['rating'].append(err)




# df = pd.DataFrame(columns=["timestamp", "uid", "session", "parameters", "error_pitch", "error_timing"])

# testing the easiest setup
# ratings_dict = {'itemID': [1, 3, 5, 7,9,11,13,15,17,19],
#                 'userID': [10,11,12,13,14,15,16,17,18,19],
#                 'rating': [5,5,5,5,5,4,4,4,4,4]}
df = pd.DataFrame(ratings_dict)



reader =Reader()
data = Dataset.load_from_df(df[['userID', 'itemID', 'rating']], reader)
trainset, testset = train_test_split(data, test_size=.25)

#factorize
svd = SVD()
svd.fit(trainset)
predictions = svd.test(testset)
print (predictions)

accuracy.rmse(predictions, verbose=True)
