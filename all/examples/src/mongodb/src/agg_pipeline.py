# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pymongo>=4.19,<5",
#     "mongoengine>=0.29",
#     "python-dotenv>=1.2",
# ]
# ///

import helper


client = helper.connect()

# Set the db object to point to the business database
db = client.business
# Count the total number of 5 ratings
print("The number of 5 star reviews:")
fivestarcount = db.reviews.count_documents({"rating": 5})
print(fivestarcount)
# Now let's use the aggregation framework to sum the occurrence of each rating across the entire data set
print("\nThe sum of each rating occurance across all data grouped by rating ")
stargroup = db.reviews.aggregate(
    # The Aggregation Pipeline is defined as an array of different operations
    [
        # The first stage in this pipe is to group data
        {"$group": {"_id": "$rating", "count": {"$sum": 1}}},
        # The second stage in this pipe is to sort the data
        {"$sort": {"_id": 1}}
        # Close the array with the ] tag
    ]
)
# Print the result
for group in stargroup:
    print(group)
