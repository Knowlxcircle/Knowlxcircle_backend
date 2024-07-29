# Knowlxcircle API Documentation

## Table of Contents
- [Introduction](#introduction)
- [Authentication](#authentication)
- [Endpoints](#endpoints)
  - [Gemini](#gemini)
    - [Home Page](#1-home-page)
    - [Chatbot Page or Ask Page](#2-chatbot-page-or-ask-page)
    - [Article Built by Gemini](#3-article-built-by-gemini)

  - [Articles](#articles)
    - [Articles Page](#1-articles-page)
    - [Create Article](#2-create-article)
  - [Circles](#circles)
    - [Create Circle](#1-create-circle)
    - [Get All Circle](#2-get-all-circle)

## Introduction
This is the API documentation for the Knowlxcircle project. The API is built using the Django Rest Framework. The API is used to interact with the Knowlxcircle database. The API is used to create, read, update and delete data from the database. 

The API is hosted locally and deployed by Microsoft Azure. The API is hosted at the following URL: [https://knowlxcircleapi.azurewebsites.net/](https://knowlxcircleapi.azurewebsites.net/) 

for local development, here is the steps to run the API locally:
1. Clone the repository
2. Build the environment using the following command:
```bash
python -m venv env
```
3. Activate the environment using the following command:
```bash
source env/bin/activate
```
2. Install the required packages using the following command:
```bash
pip install -r requirements.txt
```
3. Run the following command to migrate the database:
```bash
python manage.py makemigrations
python manage.py migrate
```
4. Run the following command to start the server:
```bash
python manage.py runserver
```
5. The API will be hosted at the following URL: [http://localhost:8000/api/v1/](http://localhost:8000/api/v1/)

## Authentication
this API have implement the JWT authentication, but to access the API you not need to provide any token, you can access the API without any token, but if you want to access the API with the token, you can get the token by login to the API using the following endpoint:
```
POST /api/v1/auth/login/
```
the response will be returned in JSON format with
```json
{
    "status": 200,
    "message": "Success",
    "response": {
        "refresh": "str(refresh)",
        "access": "str(refresh.access_token)"
    }
}
```

## Endpoints
The API has the following endpoints:
### Gemini
#### 1. Home Page:
this endpoint is used to get the home page data, this endpoint is used to get the data that will be displayed on the home page of the website.
```
GET /api/v1/gemini/home/
```
this endpoint will return the response in JSON format with the following structure:
```json
{
    "status": 200,
    "message": "Success",
    "response": {
        "prompt": "str(title)",
        "message": "str(description)",
        "created_at": "str(created_at)"
    }
}
```



#### 2. Chatbot Page or Ask Page:

 this endpoint is used to get the data that will be displayed on the chatbot page of the website.

-- GET: this endpoint returning all the prompt and response data.
```
GET /api/v1/gemini/chat/
```
This endpoint will return the response in JSON format with the following structure:
```json
{
    "status": 200,
    "message": "Success",
    "response": [
        {
            "id": 1,
            "prompt": "str(prompt)",
            "response": "str(response)",
            "created_at": "str(created_at)"
        },
        {
            "id": 2,
            "prompt": "str(prompt)",
            "response": "str(response)",
            "created_at": "str(created_at)"
        }
    ]
}

```
-- POST: this endpoint is used to add a new prompt and returning the response.
```
POST /api/v1/gemini/chat/
```
```json
POST {
    "chat_query" : "str(chat_query)"   
}
```
this endpoint will return the response in JSON format with the following structure:
```json
{
    "status": 201,
    "message": "Created",
    "response": {
        "id": 1,
        "prompt": "str(prompt)",
        "response": "str(response)",
        "created_at": "str(created_at)"
    }
}
```

-- GET: this endpoint is used to get the prompt and response data by id.
```
GET /api/v1/gemini/chat/<int:pk>/
```
this endpoint will return the response in JSON format with the following structure:
```json
{
    "status": 200,
    "message": "Success",
    "response": {
        "prompt": "str(prompt)",
        "response": "str(response)",
        "created_at": "str(created_at)"
    }
}
```

#### 3. Article Built by Gemini
this endpoint is used to get the data that will be displayed on the articles page of the website.
-- POST: this endpoint is used to add a new article that build by Gemini and returning the response.
```
POST /api/v1/article/gemini/
```
```json
POST {
    "query" : "str(query)"
}
```
this endpoint will return the response in JSON format with the following structure:
```json
{
    "id": 1,
    "title": "str(title)",
    "author": "str(author)",
    "created_at": "str(created_at)",
    "updated_at": "str(updated_at)",
    "published": "bool(published)",
    "sections": [
        {
            "id": 1,
            "article": "int(article)",
            "body": "str(body)",
            "order": "int(order)"
        },
        {
            "id": 2,
            "article": "int(article)",
            "body": "str(body)",
            "order": "int(order)"
        }
    ]
}
```

### Articles
#### 1. Articles Page:
this endpoint is used to get the data that will be displayed on the articles page of the website.
-- GET: this endpoint returning all the articles data.
```
GET /api/v1/article/articles/
```
this endpoint will return the response in JSON format with the following structure: (will only return article section > 0)
```json
{
    "status": 200,
    "message": "Success",
    "response": [
        {
            "id": 1,
            "title": "str(title)",
            "author": "str(author)",
            "created_at": "str(created_at)",
            "updated_at": "str(updated_at)",
            "published": "bool(published)",
            "sections": [
                {
                    "id": 1,
                    "article": "int(article)",
                    "body": "str(body)",
                    "order": "int(order)"
                },
                {
                    "id": 2,
                    "article": "int(article)",
                    "body": "str(body)",
                    "order": "int(order)"
                }
            ],
            "comments" : [
                {
                    "id": 1,
                    "article": "int(article)",
                    "author": "str(author)",
                    "body": "str(body)",
                    "created_at": "str(created_at)"
                },
                {
                    "id": 2,
                    "article": "int(article)",
                    "author": "str(author)",
                    "body": "str(body)",
                    "created_at": "str(created_at)"
                }
            ]

        },
        {
            "id": 2,
            "title": "str(title)",
            "author": "str(author)",
            "created_at": "str(created_at)",
            "updated_at": "str(updated_at)",
            "published": "bool(published)",
            "sections": [
                {
                    "id": 1,
                    "article": "int(article)",
                    "body": "str(body)",
                    "order": "int(order)"
                },
                {
                    "id": 2,
                    "article": "int(article)",
                    "body": "str(body)",
                    "order": "int(order)"
                }
            ],
            "comments" : [
                {
                    "id": 1,
                    "article": "int(article)",
                    "author": "str(author)",
                    "body": "str(body)",
                    "created_at": "str(created_at)"
                },
                {
                    "id": 2,
                    "article": "int(article)",
                    "author": "str(author)",
                    "body": "str(body)",
                    "created_at": "str(created_at)"
                }
            ]

        }
    ]
}
```

-- GET: this endpoint is used to get the article data by id.
```
GET /api/v1/article/articles/<int:id>/
```
this endpoint will return the response in JSON format with the following structure:
```json
{
    "status": 200,
    "message": "Success",
    "response": {
        "id": 1,
        "title": "str(title)",
        "author": "str(author)",
        "created_at": "str(created_at)",
        "updated_at": "str(updated_at)",
        "published": "bool(published)",
        "sections": [
            {
                "id": 1,
                "article": "int(article)",
                "body": "str(body)",
                "order": "int(order)"
            },
            {
                "id": 2,
                "article": "int(article)",
                "body": "str(body)",
                "order": "int(order)"
            }
        ],
        "comments" : [
            {
                "id": 1,
                "article": "int(article)",
                "author": "str(author)",
                "body": "str(body)",
                "created_at": "str(created_at)"
            },
            {
                "id": 2,
                "article": "int(article)",
                "author": "str(author)",
                "body": "str(body)",
                "created_at": "str(created_at)"
            }
        ]
    }
}
```

#### 2. Create Article:
this endpoint is used to create a new article.

-- POST: this endpoint is used to add a new article and returning the response.
```
POST /api/v1/article/title/
```
```json
POST {
    "title" : "str(title)",
    "author" : "str(author)",
    "published" : "bool(published)"
}
```
this endpoint will return the response in JSON format with the following structure:
```json
{
    "status": 201,
    "message": "Created",
    "response": {
        "id": 1,
        "title": "str(title)",
        "author": "str(author)",
    }
}

```
POST: this endpoint is used to add a new section to the article.
```
POST /api/v1/article/section/
```
```json
POST {
    "article_Id" : "int(article)",
    "body" : "str(body)",
    "order" : "int(order)"
}
```
this endpoint will return the response in JSON format with the following structure:
```json
{
    "status": 201,
    "message": "Created",
    "response": {
        "article": "int(article)",
        "body": "str(body)",
        "order": "int(order)"
    }
}
```

### Circles
#### 1. Create Circle:
this endpoint is used to create a new circle.
```
POST /api/v1/circle/create/
```
```json
POST {
    "name" : "str(name)",
    "description" : "str(description)"
}
```
this endpoint will return the response in JSON format with the following structure:
```json
{
    "status": 201,
    "message": "Created",
    "response": {
        "id": 1,
        "name": "str(name)",
    }
}
```

#### 2. Get All Circle
this endpoint is used to get all the circle data.
```
GET /api/v1/circle/circles/
```
this endpoint will return the response in JSON format with the following structure:
```json
{
    "status": 200,
    "message": "Success",
    "response": 
        "circles" : [
        {
            "id": 1,
            "name": "str(name)",
            "description": "str(description)",
            "members": int(num_of_members),
            "created_at": "str(created_at)"
            "updated_at": "str(updated_at)"
            "sentiment": "str(sentiment)"
        },
        {
            "id": 2,
            "name": "str(name)",
            "description": "str(description)",
            "members": int(num_of_members),
            "created_at": "str(created_at)",
            "updated_at": "str(updated_at)",
            "sentiment": "str(sentiment)"
        },
    ]
}
```