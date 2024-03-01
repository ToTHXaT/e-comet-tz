##yandex-cloud folder contain everything to upload a function to yandex cloud

For than we need
1. Create a .env file inside the folder containing all fields from .env.template
2. Login into yc tool
```bash
yc init

```
3. Create service account or use existing
```bash
yc iam service-account create --name my-robot # create
yc iam service-account --folder-id <folder ID> list # copy service-account-id
```
4. Run *upload_function_to_yc.bash*

##The app itself is located in the root folder and is packed into docker

1. Create .env with appropriate data
2. Change port setting in docker-compose.yml to the desired one
3. Build image
```bash
docker-compose build
```
4. Start docker-compose
```bash
docker-compose up
```

##*create_tables.sql* contains sql script needed to setup Postgresql database.
##It is expected to be executed before launching any of this apps