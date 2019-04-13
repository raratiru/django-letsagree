#!/bin/sh

psql -c 'create database travis_ci_test;' -U postgres
psql -c "CREATE USER $TOX_DB_PASSWD WITH PASSWORD $TOX_DB_USER;" -U postgres
psql -c "GRANT ALL PRIVILEGES ON DATABASE travis_ci_test to $TOX_DB_USER;" -U postgres
mysql -u root -e 'CREATE DATABASE travis_ci_test;'
mysql -u root -e "CREATE USER '"$TOX_DB_USER"'@'localhost' IDENTIFIED BY '"$TOX_DB_PASSWD"';"
mysql -u root -e "GRANT ALL ON travis_ci_test.* TO '"$TOX_DB_USER"'@'localhost';"
mysql -u root -e "FLUSH PRIVILEGES;"
