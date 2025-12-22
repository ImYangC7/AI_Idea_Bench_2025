<h1 align="center">
  <b>AI Idea Bench 2025: AI Research Idea Generation Benchmark</b><br>
</h1>

<p align="center">
  📚 <a href="https://arxiv.org/pdf/2504.14191">[Paper]</a>
  🤗 <a href="https://huggingface.co/datasets/yanshengqiu/AI_Idea_Bench_2025">[Dataset]</a>
</p>


## 💬 Introduction

### Benchmark
We construct the AI Idea Bench 2025 dataset, comprising 3,495 influential target papers in AI-related conferences along with their corresponding motivating papers, to systematically evaluate the effectiveness of idea generation methods.

### Evaluation Framework
We propose an evaluation framework that aligns generated research ideas with the content of ground-truth papers, while simultaneously assessing their merits and drawbacks based on other reference material.


## 🚀 Pipeline

### Create the environment

```bash
pip install -r requirements.txt
```

### Configuration

All API keys and paths are managed through a centralized configuration system using Pydantic Settings with `.env` file.

> **Note:** This project uses **OpenAI-compatible API format**, supporting any provider: OpenAI, DeepSeek, Azure OpenAI, local LLMs (vLLM, Ollama, etc.)

**1. Copy the example configuration file:**
```bash
cp .env.example .env
```

**2. Edit `.env` and fill in your API keys:**
```bash
# Primary LLM - Used for idea generation (AI-Scientist)
IDEA_GEN_API_KEY=your_api_key_here
IDEA_GEN_BASE_URL=https://api.openai.com/v1
IDEA_GEN_MODEL_NAME=gpt-4o

# Evaluation LLM - Used for MCQ, competition, idea matching, novelty
EVAL_API_KEY=your_api_key_here
EVAL_BASE_URL=https://api.deepseek.com/v1
EVAL_MODEL_NAME=deepseek-chat

# Semantic Scholar API (for paper search)
S2_API_KEY=your_semantic_scholar_api_key_here

# Data Paths (relative to project root)
PAPERS_DATA_PATH=../papers_data
TARGET_PAPER_DATA_PATH=../target_paper_data.json
```

See `.env.example` for all available configuration options including model parameters and intermediate data paths.

### Data preparation

Download the data from <a href="https://huggingface.co/datasets/yanshengqiu/AI_Idea_Bench_2025">[Huggingface]</a> and configure the paths in your `.env` file.

Recommended project structure:
```
Idea_bench_data/
├── code (current repository)
├── papers_data
├── target_paper_data.json
```

### Preparation for SciPDF Parser:
Install [SciPDF Parser](https://github.com/titipata/scipdf_parser) for PDF parsing.
```bash
git clone https://github.com/titipata/scipdf_parser.git
pip install git+https://github.com/titipata/scipdf_parser
python -m spacy download en_core_web_sm
```

### Preparation for Grobid

**Option 1: Docker (Recommended)**
```bash
docker run --rm --init --ulimit core=0 -p 8070:8070 grobid/grobid:0.7.3
```

Wait until you see `Started @XXXXXms` in the logs, then test:
```bash
curl http://localhost:8070/api/isalive  # Should return "true"
```

**Option 2: Local Installation**

Install Java for Grobid:
```bash
wget https://download.oracle.com/java/GA/jdk11/9/GPL/openjdk-11.0.2_linux-x64_bin.tar.gz
tar -zxvf openjdk-11.0.2_linux-x64_bin.tar.gz
```

Configure JAVA_HOME in your `.env` file:
```bash
JAVA_HOME=/path/to/jdk-11.0.2
```

Run Grobid via SciPDF Parser:
```bash
cd scipdf_parser
bash serve_grobid.sh
```

Or install Grobid directly:
```bash
git clone https://github.com/kermitt2/grobid.git
cd grobid
./gradlew clean install
./gradlew run
```

> **Note:** If using a system proxy, add `localhost` to `no_proxy` to avoid connection issues:
> ```bash
> export no_proxy="localhost,127.0.0.1"
> ```

### Generate ideas

```bash
cd ./AI-Scientist
python generate_ideas_fron_papers.py
cd ..
```

### Idea multiple-choice evaluation

```bash
python Make_MCQ.py  # Make mcq questions
python MCQ.py
```

### Idea to idea matching

```bash
python idea_gt_idea.py
```

### Idea to topic matching

```bash
python idea_gt_topic.py
```

### Ideas competition among baselines

```bash
python competition.py
```

### Novelty assessment

```bash
python find_paper_by_kewords.py  # Find current papers and history papers
python extract_hd_cd_paper.py
```
**Attention !!** Here there may be a failure to parse the paper, this is because some papers cannot be downloaded through the script. For this issue, we will manually re-download those papers that cannot be parsed.

```bash
python Novelty.py
```

### Feasibility

```bash
python split_experimental_plan.py  # split experimental plan of generated ideas
python feasibility.py
```

## 🚩 License
This repository is under the Apache-2.0 license. For commercial use, please contact with the authors.


## 📜 Citations
```
@article{qiu2025ai,
  title={AI Idea Bench 2025: AI Research Idea Generation Benchmark},
  author={Qiu, Yansheng and Zhang, Haoquan and Xu, Zhaopan and Li, Ming and Song, Diping and Wang, Zheng and Zhang, Kaipeng},
  journal={arXiv preprint arXiv:2504.14191},
  year={2025}
}
```
## 🔈 Acknowledgements
This repository is based on the following Github repositories. Thanks to the following public repositories:
- [AI-Scientist](https://github.com/SakanaAI/AI-Scientist)
- [CoI-Agent](https://github.com/DAMO-NLP-SG/CoI-Agent)
- [VIRSC](https://github.com/open-sciencelab/Virtual-Scientists)

**Note:** This is a research level repository and might contain issues/bugs. Please contact the authors for any query.
