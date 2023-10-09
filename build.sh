set -o errexit  # exit on error

pip install -r requirements/dev.txt

python manage.py collectstatic --no-input
python manage.py migrate