FROM python:3.12-slim

# Install system dependencies required for Rust (Not necessary as of now)
# RUN apt-get update && apt-get install -y curl build-essential

# Install Rust
# RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Ensure Cargo is on the PATH
# ENV PATH="/root/.cargo/bin:${PATH}"

WORKDIR /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Ensure container stays alive to get shell access
CMD ["sleep", "infinity"]