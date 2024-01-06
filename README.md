Here a simple readme for this project.


To run this project you need install:
pipx
pip
python = "^3.10"
django = "5.0.1"
pillow = "10.2.0"

also to run this

git clone https://github.com/robertos1232/ProjektStudiaProgwZastosowaniach.git

cd programowanie_w_zastosowaniach
./manage.py runserver


If you want to delete db and start allover again

git clone https://github.com/robertos1232/ProjektStudiaProgwZastosowaniach.git

cd programowanie_w_zastosowaniach

./manage.py migrate
./manage.py createsuperuser
./manage.py runserver

