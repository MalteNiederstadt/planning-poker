set -o errexit  # exit on error

pip install wheel
pip install -r requirements/dev.txt
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --no-input
python manage.py migrate


if [[ $CREATE_SUPERUSER ]];
then
  python manage.py createsuperuser --no-input
fi
