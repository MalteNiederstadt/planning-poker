set -o errexit  # exit on error
if [[ $CREATE_SUPERUSER ]];
then
  python manage.py createsuperuser --no-input
fi

pip install -r requirements/dev.txt

python manage.py collectstatic --no-input
python manage.py migrate

