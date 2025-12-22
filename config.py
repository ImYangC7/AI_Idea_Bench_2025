"""
AI Idea Bench 2025 - 集中式配置管理模块

使用 Pydantic 进行配置验证，从 .env 文件加载配置
"""

from pathlib import Path
from functools import lru_cache
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# .env 文件路径（基于 config.py 所在目录）
_ENV_FILE = Path(__file__).parent / ".env"


class APISettings(BaseSettings):
    """API 相关配置 (OpenAI-compatible format)"""
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Primary LLM - Used for idea generation (AI-Scientist)
    idea_gen_api_key: str = Field(default="", alias="IDEA_GEN_API_KEY")
    idea_gen_base_url: str = Field(
        default="https://api.openai.com/v1", alias="IDEA_GEN_BASE_URL"
    )
    idea_gen_model_name: str = Field(default="gpt-4o", alias="IDEA_GEN_MODEL_NAME")

    # Evaluation LLM - Used for MCQ, competition, idea matching, novelty assessment
    eval_api_key: str = Field(default="", alias="EVAL_API_KEY")
    eval_base_url: str = Field(
        default="https://api.deepseek.com/v1", alias="EVAL_BASE_URL"
    )
    eval_model_name: str = Field(default="deepseek-chat", alias="EVAL_MODEL_NAME")

    # Semantic Scholar API
    semantic_scholar_api_key: str = Field(default="", alias="S2_API_KEY")


def _get_project_root() -> Path:
    """获取项目根目录（config.py 所在目录）"""
    return Path(__file__).parent.resolve()


class PathSettings(BaseSettings):
    """路径相关配置"""
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # 项目根目录（自动检测，基于 config.py 位置）
    project_root: Path = Field(default_factory=_get_project_root)

    # 数据集路径（相对于项目根目录的上级）
    papers_data_path: Path = Field(
        default=Path("../papers_data"), alias="PAPERS_DATA_PATH"
    )
    target_paper_data_path: Path = Field(
        default=Path("../target_paper_data.json"), alias="TARGET_PAPER_DATA_PATH"
    )

    # 中间数据路径（相对于项目根目录）
    dataset_temple_path: Path = Field(
        default=Path("dataset_temple"), alias="DATASET_TEMPLE_PATH"
    )
    cited_paper_content_path: Path = Field(
        default=Path("dataset_temple/cited_paper_conten.json"),
        alias="CITED_PAPER_CONTENT_PATH",
    )
    mcq_motivation_path: Path = Field(
        default=Path("dataset_temple/mcq_motivation.json"),
        alias="MCQ_MOTIVATION_PATH",
    )
    mcq_experiment_plan_path: Path = Field(
        default=Path("dataset_temple/mcq_experiment_plan.json"),
        alias="MCQ_EXPERIMENT_PLAN_PATH",
    )
    target_paper_data_w_hd_cd_path: Path = Field(
        default=Path("dataset_temple/target_paper_data_w_hd_cd.json"),
        alias="TARGET_PAPER_DATA_W_HD_CD_PATH",
    )
    hd_cd_paper_content_path: Path = Field(
        default=Path("dataset_temple/hd_cd_paper_conten.json"),
        alias="HD_CD_PAPER_CONTENT_PATH",
    )
    paper_temple_path: Path = Field(
        default=Path("dataset_temple/paper_temple"),
        alias="PAPER_TEMPLE_PATH",
    )

    # 模型输出路径（相对于项目根目录）
    model_output_base_path: Path = Field(
        default=Path("model_output"), alias="MODEL_OUTPUT_BASE_PATH"
    )

    def _resolve(self, path: Path) -> Path:
        """将相对路径解析为绝对路径（基于项目根目录）"""
        if path.is_absolute():
            return path
        return (self.project_root / path).resolve()

    @property
    def ai_scientist_output_path(self) -> Path:
        return self._resolve(self.model_output_base_path) / "AI-Scientist"

    @property
    def ai_researcher_output_path(self) -> Path:
        return self._resolve(self.model_output_base_path) / "AI-Researcher"

    @property
    def scipip_output_path(self) -> Path:
        return self._resolve(self.model_output_base_path) / "SciPIP"

    @property
    def social_science_output_path(self) -> Path:
        return self._resolve(self.model_output_base_path) / "Social_Science"

    def resolve_path(self, attr_name: str) -> Path:
        """获取解析后的绝对路径"""
        path = getattr(self, attr_name)
        return self._resolve(path)


class ModelSettings(BaseSettings):
    """模型相关配置"""
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
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
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    java_home: str = Field(default="", alias="JAVA_HOME")
    grobid_path: str = Field(default="", alias="GROBID_PATH")


class Settings(BaseSettings):
    """总配置类，组合所有子配置"""
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
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

