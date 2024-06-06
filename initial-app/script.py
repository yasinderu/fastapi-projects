import pymongo
import json

# Connect to MongoDB
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['courses']
collection = db['courses']

# Read courses from courses.json
with open('courses.json', 'r') as file:
    courses = json.load(file)

# Create index for efficient retrival
collection.create_index('name')

# Add rating field to each course
for course in courses:
    course['rating'] = {'total': 0, 'count': 0}

for course in courses:
    for chapter in course['chapters']:
        chapter['rating'] = {'total': 0, 'count':0}

# Add courses to collection
for course in courses:
    collection.insert_one(course)

# Close MongoDB connection
client.close()