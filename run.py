from pyngrok import ngrok
import subprocess

public_url = ngrok.connect(8000)

print("Public URL:")
print(public_url)

subprocess.run(["python3", "app.py"])
