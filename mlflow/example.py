# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "mlflow-skinny==3.18.0",
# ]
# ///

"""Log a run to the local MLflow server.

Run: pip install -r requirements.txt && python example.py
"""
import os

import mlflow

URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
mlflow.set_tracking_uri(URI)
mlflow.set_experiment("containerising-demo")

with mlflow.start_run(run_name="hello"):
    mlflow.log_param("alpha", 0.5)
    mlflow.log_metric("rmse", 0.42)
    with open("note.txt", "w") as f:
        f.write("hello from the containerising templates\n")
    mlflow.log_artifact("note.txt")  # uploaded through the server (--serve-artifacts)
print("done, open", URI)
