#!/bin/sh

# psql -c "create database $TOX_DB_NAME;" -U postgres
# psql -c "CREATE USER $TOX_DB_PASSWD WITH PASSWORD '`echo $TOX_DB_USER`';" -U postgres
# psql -c "GRANT ALL PRIVILEGES ON DATABASE $TOX_DB_NAME to $TOX_DB_USER;" -U postgres
# psql -c "ALTER USER $TOX_DB_USER CREATEDB;" -U postgres
mysql -u root -e 'CREATE DATABASE travis_ci_test;'
mysql -u root -e "CREATE USER '`echo $TOX_DB_USER`'@'localhost' IDENTIFIED BY '`echo $TOX_DB_PASSWD`';"
mysql -u root -e "GRANT ALL ON travis_ci_test.* TO '`echo $TOX_DB_USER`'@'localhost';"
mysql -u root -e "FLUSH PRIVILEGES;"
