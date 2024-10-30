# compositeService


## SSH into the EC2 Instance: (VSCode)

```bash
ssh -i "<path_to_key>\compositeServiceKeyPair.pem" ec2-user@ec2-54-84-254-253.compute-1.amazonaws.com
```

## Setting Up SSH Authentication for GitHub Access on EC2

* SSH Authentication: Generate an SSH key, add it to GitHub, and use the SSH URL to clone.

### Generate an SSH Key (on an EC2 instance)

* Run the following command on the EC2 instance to generate an SSH key pair:
    ```bash
    ssh-keygen -t ed25519 -C "username@email.com"
    ```
    * A public key has been saved in /home/ec2-user/.ssh/id_ed25519.pub

* [GitHub SSH and GPG keys settings](https://github.com/settings/keys). 
* Click on `New SSH key`
* Paste public key stored in `~/.ssh/id_ed25519.pub` into the "Key" field and save it.

* Clone the Repository Using SSH
    ```bash
    git clone git@github.com:Clouc-Computing/compositeService.git
    ```

## Sprint 2

### Initial Setup
* Initial Setup
    ```bash
    sudo yum install python3 -y
    python3 -m venv .venv
    source .venv/bin/activate
    ```
    * Added `.venv/` to `.gitignore` 

    ```bash
    python3 -m pip install --upgrade pip
    pip3 install -r requirements.txt
    ```
* After installing any python packages:
    ```bash
    pip3 freeze > requirements.txt
    ```

### `microservice-2` repository PostgreSQL
* [PostgreSQL Commands](https://www.postgresql.org/docs/current/sql-commands.html)
    ```bash
    CREATE DATABASE microservice_db;
    CREATE USER microservice_user WITH PASSWORD 'dbuserdbuser';
    GRANT ALL PRIVILEGES ON DATABASE microservice_db TO microservice_user;
    ```


### Testing connection with a microservice
* Start the microservice on a specific port, which can be accessed by:
    ```bash
    http://127.0.0.1:5000
    ````



## OpenAPI Documentation
* Created a OpenAPI Documentation for CRUD Operations (e.g. GET, POST, PUT, DELETE) with descriptions on SwaggerHub  
    [OpenAPI Documentation](https://app.swaggerhub.com/apis/SL5036/COMS4153-Project-OpenAPI-Documentation/1.0)
    

## Composite microservice/resource:
* e.g. /api/student_infos, /api/student_infos/{uni}

1. GET, PUT and POST for a resource that requires operations on the sub-resources
    * Calls/delegates to atomic services for GET and POST.

2. Basic support for navigation paths, including query parameters,
    * e.g. /studentInfo/{uni}/courses or /studentInfo/{uni}/teams
    * 202 Accepted and implementing an asynchronous update to a URL.

3. An implementation of a method that calls the sub-resources synchronously
    * Implement one method synchronously

4. An implementation of the method that calls a resource asynchronously
    * Implement one asynchronously using threads, co-routines, ...

5. Basic support for navigation paths, including query parameters
    * e.g. /student_infos/{uni}/courses, /student_infos/{uni}/teams

6. Middleware on each resource that implements before and after logging for all methods/paths.

7. Getting the URLs/dependencies from the environment variables.

8. Deploy the composite service and other components





