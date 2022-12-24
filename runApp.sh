
pip3 install -r requirements.txt

killall -9 flask	
flask run &

sleep 4

firefox http://localhost:5000/
