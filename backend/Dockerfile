# 基础镜像
ARG PYTHON_BUILDER_IMAGE=3.13-slim-bookworm
FROM python:${PYTHON_BUILDER_IMAGE} AS python-base

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

RUN apt-get update \
  && apt-get install -y --no-install-recommends git tini build-essential curl libpq-dev libpq5 \
  && apt-get autoremove -y \
  && apt-get clean -y \
  && rm -rf /var/lib/apt/lists/* /root/.cache

RUN pip install --quiet -U pip wheel setuptools virtualenv

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Developer image
FROM python-base AS dev-image

ARG UV_INSTALL_ARGS="--all-features"
ARG LITESTAR_APP="src.app.asgi:create_app"

ENV PATH="/workspace/app/.venv/bin:$PATH" \
    VIRTUAL_ENV="/workspace/app/.venv" \
    UV_NO_CACHE=1 \
    UV_INSTALL_ARGS="${UV_INSTALL_ARGS}" \
    UV_SYSTEM_PYTHON=1 \
    LITESTAR_APP="${LITESTAR_APP}" \
    PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# 工作目录
WORKDIR /workspace/app

# 拷贝依赖定义
COPY pyproject.toml uv.lock requirements.txt ./

# 初始化 Node 环境（如果前端存在）
# RUN uvx nodeenv --quiet /opt/nodeenv/ && npm install

# 同步依赖（第一轮）
RUN uv sync ${UV_INSTALL_ARGS} --no-install-project

# 拷贝应用代码
COPY src ./src

# 第二轮同步，确保应用依赖安装齐
RUN uv sync ${UV_INSTALL_ARGS}

STOPSIGNAL SIGINT
EXPOSE 8000
ENTRYPOINT ["tini","--"]
CMD ["litestar","run","--host","0.0.0.0","--port","8000"]
