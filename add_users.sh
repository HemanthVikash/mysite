#!/bin/bash
UNAMEBASE="shruti"
# number of users to create
COUNT=13
i=1
BTICK='`'
SQL=''
echo "Database  User            Password" > ./users.txt
until [ $i -gt $COUNT ]; do
        UNAME="$UNAMEBASE$i"
        UDB="drupal_$i"
        UPASS=$(makepasswd --char=8)
        echo "$UDB      $UNAME  $UPASS" >> ./users.txt
        Q1="CREATE DATABASE IF NOT EXISTS $UDB;"
        Q2="GRANT ALL ON ${BTICK}$UDB${BTICK}.* TO '$UNAME'@'localhost' IDENTIFIED BY '$UPASS';"
        SQL="$SQL${Q1}${Q2}"
        let i=i+1
done

SQL="$SQL FLUSH PRIVILEGES;"
mysql -u root -p -e "$SQL"