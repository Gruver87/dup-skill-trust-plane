FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY configs ./configs
COPY src ./src

# Sibling gates are mounted or pre-installed in compose build context via extras.
RUN pip install --no-cache-dir -e .

ENV TRUST_BIND=0.0.0.0
ENV TRUST_PORT=8788
EXPOSE 8788

CMD ["python", "-m", "skill_trust", "serve", "--host", "0.0.0.0", "--port", "8788"]
