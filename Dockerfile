FROM ghcr.io/haroldarpanet/style_seeker_ai/base-image:latest

# Install Rust and Cargo
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false

RUN poetry install --no-interaction --no-ansi

COPY . /app/

EXPOSE 8000

CMD ["gunicorn", "--config", "gunicorn_config.py", "style_seeker_ai.wsgi:application"]