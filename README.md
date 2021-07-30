## User Specific Docs

This microservices built on Django

## Contacts API
api/v1/contacts\
api/v1/contacts/{id}\
api/v1/contacts?mobile_no={number}\
GET, POST, PUT, PATCH, DELETE

POST Payload:
[{
    "name": "Ranjeet Singh",
    "mobile_no": "8459159143",
    "email": "ranjeet@gmail.com",
    "unique_id": "xxx"
}]  

PUT/PATCH: 
{
    "name": "Ranjeet Singh",
    "mobile_no": "8459159143",
    "email": "ranjeet@gmail.com",
    "unique_id": "xxxx"
} 

DELETE: 
contacts/{id}