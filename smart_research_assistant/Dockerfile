# ---- Base image ----
FROM python:3.12-slim

# ---- Set working directory ----
WORKDIR /app

# ---- Copy requirements and install dependencies ----
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Copy the rest of your project ----
COPY . .

# ---- Create folder for generated PDFs ----
RUN mkdir -p outputs

# ---- Expose both FastAPI and Streamlit ports ----
EXPOSE 8000 8501

# ---- Define environment variables (you’ll inject actual keys at runtime) ----
ENV GEMINI_API_KEY="AIzaSyDgIuCfgQnqE4l_J4EX-ClysACAw7cNq8s"
ENV TAVILY_API_KEY="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"

# ---- Run both FastAPI and Streamlit inside container ----
CMD ["bash", "-c", "\
uvicorn server:app --host 0.0.0.0 --port 8000 & \
streamlit run ui/app.py --server.port 8501 --server.address 0.0.0.0 \
"]
