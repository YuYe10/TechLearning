"""pydantic-settings：用 Pydantic 管理配置（环境变量 / .env 文件）。"""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_", env_file=".env", extra="ignore")
    host: str = "localhost"
    port: int = 8000
    debug: bool = False


def main():
    # 模拟环境变量（真实项目里由部署环境注入，而不是写死在代码里）
    os.environ["APP_HOST"] = "prod.example.com"
    os.environ["APP_PORT"] = "9000"
    os.environ["APP_DEBUG"] = "true"

    s = Settings()
    print("host :", s.host)
    print("port :", s.port, "| 类型:", type(s.port).__name__)
    print("debug:", s.debug, "| 类型:", type(s.debug).__name__)
    print("model_dump:", s.model_dump())


if __name__ == "__main__":
    main()
