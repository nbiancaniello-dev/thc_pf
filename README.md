# Cursor Backend Challenge

You have to build a microservice that exposes a REST API with two different tables: `users` and `states`. 
Both tables should be open to creation, deletion, or update. 
Every request must only set the `Content-Type: application/json`.

[![CircleCI](https://dl.circleci.com/status-badge/img/circleci/82UCLJQ6A8o5rRSH4fZh65/5RcRNgdavvWGzeAteUNeQ3/tree/master.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/circleci/82UCLJQ6A8o5rRSH4fZh65/5RcRNgdavvWGzeAteUNeQ3/tree/master)

### Features
- Create new Users
- Get Users List
- Get User By ID
- Update User
- Delete User

## Pre-Requisites

- Docker installed without SUDO Permission
- Docker compose installed without SUDO
- Ports free: 3000 and 5432

## How to run the APP

```
chmod 771 ./up_dev.sh
./up_dev.sh
```

## How to run the tests

```
chmod 771 ./up_test.sh
./up_test.sh
```

## Areas to improve

- Data should be move from tests to an external file
- Generic method should be used to mock endpoints
- Error handling could be improved (I.E handling non-existing user on Delete)
- A Seed migration would be useful to have an already working app with data

## Techs

- uv: 0.13.4
- python: 3.14.7 
- fastapi: 0.148.0
- alembic: 1.20.0
- pytest: pytest-9.1.1
- postgres: 18.6 + psycopg

## Decisions made

- Clean Architecture: To be able to handle further changes in the future in a proper way.
- Alembic: Because it allows migration over changes in the database and it is widely used and many developers use it.
- Docker: To make it portable
- Pytest: It is the most used framework, many developers use it. (Review)

## Route

- : [![API Swagger] (https://localshot:3000/api)]

## Env vars should be defined

To find an exmplae of the values you can use .env.example