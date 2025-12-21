"""
AI Idea Bench 2025 - 集中式配置管理模块

使用 Pydantic 进行配置验证，从 .env 文件加载配置
"""

from pathlib import Path
from functools import lru_cache
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class APISettings(BaseSettings):
    """API 相关配置"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # GPT-4o API
    gpt4o_api_key: str = Field(default="", alias="GPT4O_API_KEY")
    gpt4o_base_url: str = Field(
        default="https://api.openai.com/v1", alias="GPT4O_BASE_URL"
    )

    # DeepSeek API
    deepseek_api_key: str = Field(default="", alias="DEEPSEEK_API_KEY")
    deepseek_base_url: str = Field(
        default="https://api.deepseek.com/v1", alias="DEEPSEEK_BASE_URL"
    )
    deepseek_model_name: str = Field(
        default="deepseek-chat", alias="DEEPSEEK_MODEL_NAME"
    )

    # Semantic Scholar API
    semantic_scholar_api_key: str = Field(default="", alias="S2_API_KEY")

    # OpenRouter API (for Llama)
    openrouter_api_key: str = Field(default="", alias="OPENROUTER_API_KEY")


class PathSettings(BaseSettings):
    """路径相关配置"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # 项目根目录（自动检测）
    project_root: Path = Field(default_factory=lambda: Path(__file__).parent)

    # 数据集路径
    papers_data_path: Path = Field(
        default=Path("../papers_data"), alias="PAPERS_DATA_PATH"
    )
    target_paper_data_path: Path = Field(
        default=Path("../target_paper_data.json"), alias="TARGET_PAPER_DATA_PATH"
    )

    # 中间数据路径
    dataset_temple_path: Path = Field(
        default=Path("./dataset_temple"), alias="DATASET_TEMPLE_PATH"
    )
    cited_paper_content_path: Path = Field(
        default=Path("./dataset_temple/cited_paper_conten.json"),
        alias="CITED_PAPER_CONTENT_PATH",
    )
    mcq_motivation_path: Path = Field(
        default=Path("./dataset_temple/mcq_motivation.json"),
        alias="MCQ_MOTIVATION_PATH",
    )
    mcq_experiment_plan_path: Path = Field(
        default=Path("./dataset_temple/mcq_experiment_plan.json"),
        alias="MCQ_EXPERIMENT_PLAN_PATH",
    )
    target_paper_data_w_hd_cd_path: Path = Field(
        default=Path("./dataset_temple/target_paper_data_w_hd_cd.json"),
        alias="TARGET_PAPER_DATA_W_HD_CD_PATH",
    )
    hd_cd_paper_content_path: Path = Field(
        default=Path("./dataset_temple/hd_cd_paper_conten.json"),
        alias="HD_CD_PAPER_CONTENT_PATH",
    )
    paper_temple_path: Path = Field(
        default=Path("./dataset_temple/paper_temple"),
        alias="PAPER_TEMPLE_PATH",
    )

    # 模型输出路径
    model_output_base_path: Path = Field(
        default=Path("./model_output"), alias="MODEL_OUTPUT_BASE_PATH"
    )

    @property
    def ai_scientist_output_path(self) -> Path:
        return self.model_output_base_path / "AI-Scientist"

    @property
    def ai_researcher_output_path(self) -> Path:
        return self.model_output_base_path / "AI-Researcher"

    @property
    def scipip_output_path(self) -> Path:
        return self.model_output_base_path / "SciPIP"

    @property
    def social_science_output_path(self) -> Path:
        return self.model_output_base_path / "Social_Science"


class ModelSettings(BaseSettings):
    """模型相关配置"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # 生成参数
    num_reflections: int = Field(default=3, alias="NUM_REFLECTIONS")
    num_ideas: int = Field(default=2, alias="NUM_IDEAS")
    max_num_generations: int = Field(default=20, alias="MAX_NUM_GENERATIONS")
    temperature: float = Field(default=0.6, alias="TEMPERATURE")


class GrobidSettings(BaseSettings):
    """Grobid PDF 解析相关配置"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    java_home: str = Field(default="", alias="JAVA_HOME")
    grobid_path: str = Field(default="", alias="GROBID_PATH")


class Settings(BaseSettings):
    """总配置类，组合所有子配置"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    api: APISettings = Field(default_factory=APISettings)
    paths: PathSettings = Field(default_factory=PathSettings)
    model: ModelSettings = Field(default_factory=ModelSettings)
    grobid: GrobidSettings = Field(default_factory=GrobidSettings)


@lru_cache
def get_settings() -> Settings:
    """获取全局配置单例（带缓存）"""
    return Settings()


# 便捷访问
settings = get_settings()

