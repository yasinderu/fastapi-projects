from fastapi.testclient import TestClient
from pymongo import MongoClient
from bson import ObjectId
import pytest
from main import app

client = TestClient(app)
mongo_client = MongoClient('mongodb://localhost:27017/')
db = mongo_client['courses']

course_id = '66613a6be11d10b2e1541e57'

# Test get courses
def test_get_courses_no_params():
    response = client.get('/courses')
    assert response.status_code == 200

# Test get courses with query param
def test_get_courses_sort_by_alphabetical():
    response = client.get('/courses?sort_by=alphabetical')
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) > 0
    assert sorted(courses, key=lambda x: x['name']) == courses

def test_get_courses_sort_by_date():
    response = client.get('/courses?sort_by=date')
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) > 0
    assert sorted(courses, key=lambda x: x['date'], reverse=True) == courses

def test_get_courses_sort_by_rating():
    response = client.get('/courses?sort_by=rating')
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) > 0
    assert sorted(courses, key=lambda x: x['rating']['total'], reverse=True) == courses

def test_get_courses_filter_by_domain():
    response = client.get('/courses?domain=mathematics')
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) > 0
    assert all([c['domain'][0] == 'mathematics' for c in courses])

def test_get_courses_filter_by_domain_and_sort_by_alphabetical():
    response = client.get('/courses?domain=mathematics&sort_by=alphabetical')
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) > 0
    assert all([c['domain'][0] == 'mathematics' for c in courses])
    assert sorted(courses, key=lambda x: x['name']) == courses

def test_get_courses_filter_by_domain_and_sort_by_date():
    response = client.get('/courses?domain=mathematics&sort_by=date')
    assert response.status_code == 200
    courses = response.json()
    assert len(courses) > 0
    print('courses', courses)
    assert all([c['domain'][0] == 'mathematics' for c in courses])
    assert sorted(courses, key=lambda x: x['date'], reverse=True) == courses

# Test get course by id
def test_get_courses_by_id_exists():
    response = client.get(f'/courses/{course_id}')
    assert response.status_code == 200
    course = response.json()

    course_db = db.courses.find_one({'_id': ObjectId('66613a6be11d10b2e1541e57')})
    course_name_from_db = course_db['name']
    course_name_from_response = course['name']
    assert course_name_from_db == course_name_from_response

def test_get_course_by_id_not_exists():
    response = client.get('/courses/66613a6be11d10b2e1541e55')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Course not found'}

# Test get chourse chapter info
def test_get_chapter_info():
    response = client.get(f'/courses/{course_id}/1')
    assert response.status_code == 200
    chapter = response.json()
    assert chapter['name'] == "Big Picture of Calculus"
    assert chapter['text'] == "Highlights of Calculus"

def test_get_chapter_info_not_found():
    response = client.get(f'/courses/{course_id}/990')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Chapter not found'}

# Test rate course
def test_rate_chapter():
    chapter_id = '1'
    rating = 1

    response = client.post(f'/courses/{course_id}/{chapter_id}?rating={rating}')
    assert response.status_code == 200

    # Check if the response body has the expected structure
    assert 'name' in response.json()
    assert 'rating' in response.json()
    assert 'total' in response.json()['rating']
    assert 'count' in response.json()['rating']

    assert response.json()['rating']['total'] > 0
    assert response.json()['rating']['count'] > 0

def test_rate_chapter_not_exists():
    response = client.post('/courses/66613a6be11d10b2e1541e57/990/rate', json={'rating': 1})
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}