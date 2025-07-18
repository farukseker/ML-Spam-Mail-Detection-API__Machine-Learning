from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
import pandas as pd
import joblib
import io

# Initialize the application
app = FastAPI(title="Spam Mail Prediction API")

# Load the model and vectorizer once at startup
model = joblib.load("models/spam_model.pkl")
vectorizer = joblib.load("models/tfidf_vectorizer.pkl")

# Request model
class MailRequest(BaseModel):
    message: str

@app.get("/")
def root():
    return {"message": "Spam Mail API is ready"}

# Single message prediction
@app.post("/predict")
def predict_single(data: MailRequest):
    vect = vectorizer.transform([data.message])
    result = model.predict(vect)[0]
    label = "spam" if result == 1 else "ham"
    return {"prediction": label}

# Bulk prediction via CSV upload
@app.post("/predict_csv")
async def predict_csv(file: UploadFile = File(...)):
    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))

    if "message" not in df.columns:
        return JSONResponse(content={"error": "Missing 'message' column in CSV"}, status_code=400)

    vect = vectorizer.transform(df["message"])
    predictions = model.predict(vect)
    df["prediction"] = ["spam" if p == 1 else "ham" for p in predictions]

    # Return the resulting CSV
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)

    return StreamingResponse(output, media_type="text/csv", headers={
        "Content-Disposition": "attachment; filename=result.csv"
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
