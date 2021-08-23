echo "[INFO] generate update file..."
cd ..\..

IF "%1" == "true" (
    py genUpdateFile.py
)
