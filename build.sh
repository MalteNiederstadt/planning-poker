set -o errexit  # exit on error

pip install wheel
pip install -r requirements/dev.txt

python manage.py collectstatic --no-input
python manage.py migrate
export DJANGO_SETTINGS_MODULE=example.settings

if [[ $CREATE_SUPERUSER ]];
then
  python manage.py createsuperuser --no-input
fi
