git config --global --add safe.directory /code
git pull
pip install --upgrade pip
pip install -r requirements.txt
playwright install
python3 telegrambot.py

