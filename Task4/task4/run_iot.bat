@echo off
echo Запуск IoT-клієнта...
cd ..
call venv\Scripts\activate
cd iot_client
python iot_client.py
pause