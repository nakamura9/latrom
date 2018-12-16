echo "Retrieving data from server..."
git pull origin master
echo "Merging databases"
python manage.py migrate
echo "starting server"
python manage.py runserver 

