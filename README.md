# Create a docker container for pgadmin and postgresql

sudo docker ps -a

# Start the pgadmin container

sudo docker start {pg_admin_container}

# Start the postgresql container (stop the localhost and start container)

sudo service postgresql stop

sudo docker start {postgresql_container}


# Start the uvicorn for fastapi 

uvicorn app.main:app --reload