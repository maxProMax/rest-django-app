# rest-django-app

run something

$ docker-compose run --rm app sh -c 'django-admin startproject app .'

$ docker-compose run --rm app sh -c 'python manage.py test'

in EC2 instance create ssh-key

$ ssh-keygen -t ed25519 -b 4096

---

connect to server
$ ssh ec2-user@13.60.35.47

13.60.35.47 - server ip address

---

enable docker service in the service

$ sudo systemctl enable docker.service
$ sudo systemctl start docker.service

add permission to run docker

$ sudo usermod -aG docker ec2-user
