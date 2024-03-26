apt-get update
echo "INSTALLING FFMPEG"
apt-get install -y ffmpeg
echo "INSTALLING FFMPEG DONE?"
git config --global --add safe.directory /code
git pull
pip install --upgrade pip
pip install -r requirements.txt
playwright install
python3 telegrambot.py

