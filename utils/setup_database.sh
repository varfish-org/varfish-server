#!/usr/bin/env bash

echo "***********************************************"
echo "Setting up Database and User for PostgreSQL"
echo "***********************************************"

# while loops to ensure input not empty

# -------------
# Database Name
# -------------
while [[ -z "$db_name" ]]
do
    echo -n "Database Name: "
    read db_name
done

# ----------------
# User Name Choice
# ----------------

# Choice to create a new user or use and existing one
while [ "$use_existing_user" != "y" ] && [ "$use_existing_user" != "n" ]
do
    echo -n "Do you want to use an existing db-user? [y|n] "
    read use_existing_user
done

# Existing user
if [ "$use_existing_user" == "y" ]
then
    # Get and parse existing users

    # All users in the psql database
    users="$( sudo su - postgres -c "psql -c \"SELECT u.usename FROM pg_catalog.pg_user u;\"")"
    # Regex to remove table header and row count
    regex="usename\ -+ \K(.*)(?=\ \(\d*\ rows?\))"
    # Use grep to execute regex
    users=$(echo $users | grep -Po "$regex")
    # Create user array by
    # Splitting users string at spaces
    IFS=' '
    read -ra user_array <<< "$users"

    # Choose existing user
    echo ""
    choice=-1
    # Choice has to be in range and an integer
    while (( $choice < 0 )) || (( $choice > ${#user_array[@]} - 1 ))
    do
        echo "Choose an existing user"
        idx=0
        for user in "${user_array[@]}"; do # access each element of array
            echo "[$idx] $user"
            idx=$(( idx + 1 ))
        done
        echo -n "> "
        read choice
    done
    username=${user_array[$choice]}

# New user
else
    while [[ -z "$username" ]]
    do
        echo -n "New username: "
        read username
    done

    # ----------------
    # Password Choice
    # ----------------
    while [[ -z "$password" ]]
    do
        echo -n "Password: "
        read -s password
    done
    echo ""
fi


sudo su - postgres -c "psql -c \"CREATE DATABASE $db_name;\""
if [ "$use_existing_user" == "n" ]
then
    sudo su - postgres -c "psql -c \"CREATE USER $username WITH PASSWORD '$password';\""
fi
sudo su - postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE $db_name to $username;\""
sudo su - postgres -c "psql -c \"ALTER USER $username CREATEDB;\""
