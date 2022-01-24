import helper


client = helper.connect()

# Set the db object to point to the business database
db = client.business
# Showcasing the count() method of find, count the total number of 5 ratings
print("The number of 5 star reviews:")
fivestarcount = db.reviews.find({"rating": 5}).count()
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
