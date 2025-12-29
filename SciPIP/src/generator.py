import functools
import json
import os
import threading
import time
import warnings

import click
from loguru import logger
from omegaconf import OmegaConf

from utils.hash import check_env
from utils.header import ConfigReader
from utils.llms_api import APIHelper

warnings.filterwarnings("ignore")


def extract_problem(problem, background):
    start_keyword = "**Research Problem**"
    end_keyword = "**Rationales**"
    start_index = problem.find(start_keyword)
    end_index = problem.find(end_keyword)
    if start_index != -1 and end_index != -1:
        research_problem = problem[start_index:end_index].strip()
    else:
        research_problem = background
    return research_problem


def extract_ideas(idea_str):
    if idea_str is None:
        return ""
    ideas = []
    for i in range(1, 100): # 100 is a magic number
        start_word = f"**Idea {i}"
        end_word = f"**Idea {i+1}"
        start_index = idea_str.find(start_word)
        end_index = idea_str.find(end_word)
        if start_index != -1 and end_index != -1:
            ideas.append(idea_str[start_index:end_index].strip())
            # idea_str = idea_str[start_index+end_index+1:]
        elif start_index != -1:
            ideas.append(idea_str[start_index:].strip())
            break
        else:
            break
    return ideas if ideas else [idea_str]


class IdeaGenerator:
    def __init__(
        self,
        config,
        paper_list: list[dict] = [],
        brainstorm: str = None,
    ) -> None:
        self.api_helper = APIHelper(config)
        self.paper_list = paper_list
        self.brainstorm = brainstorm

    def generate_without_cue_words(self, background: str):
        """Generate ideas without cue words and brainstorm
        """
        problem, message_input = self.api_helper.generate_problem(
            background, self.paper_list
        )
        idea = self.api_helper.generate_idea(problem, self.paper_list)
        idea_filtered = self.api_helper.filter_idea(idea, background)
        return message_input, problem, idea, idea_filtered

    def generate_without_cue_words_bs(self, background: str):
        """Generate ideas without cue words, but brainstorm
        """
        problem, message_input = self.api_helper.generate_problem(
            background, self.paper_list
        )
        idea = self.api_helper.generate_idea(problem, self.paper_list)
        idea_filtered = self.api_helper.integrate_idea(
            background, self.brainstorm, idea
        )
        return message_input, problem, idea, idea_filtered

    def generate_without_cue_words_ins(self, background: str):
        """Generate ideas without cue words and brainstorm, but inspiration
        """
        problem, message_input = self.api_helper.generate_problem(
            background, self.paper_list
        )
        research_problem = extract_problem(problem, background)
        inspirations = []
        for paper in self.paper_list:
            inspiration = self.api_helper.generate_inspiration(research_problem, paper)
            inspirations.append(inspiration)
        idea = self.api_helper.generate_idea_by_inspiration(problem, inspirations)
        idea_filtered = self.api_helper.filter_idea(idea, background)
        return message_input, problem, inspirations, idea, idea_filtered

    def generate_without_cue_words_ins_bs(self, background: str):
        """Generate ideas without cue words, but inspiration and brainstorm
        """
        problem, message_input = self.api_helper.generate_problem(
            background, self.paper_list
        )
        research_problem = extract_problem(problem, background)
        inspirations = []
        for paper in self.paper_list:
            inspiration = self.api_helper.generate_inspiration(research_problem, paper)
            inspirations.append(inspiration)
        idea = self.api_helper.generate_idea_by_inspiration(problem, inspirations)
        idea_filtered = self.api_helper.integrate_idea(
            background, self.brainstorm, idea
        )
        return message_input, problem, inspirations, idea, idea_filtered

    def generate_ins_bs(self, detail_background: str):
        """Generate ideas with inspiration and brainstorm
        """
        inspirations = []

        ## generate inspirations
        processes = []
        def generate_inspiration(paper, i):
            detail_method = paper.get("idea") or ""
            if not isinstance(detail_method, str):
                detail_method = str(detail_method)
            inspiration = self.api_helper.generate_inspiration_with_detail_method(detail_background, detail_method)
            logger.info(f"Generate inspiration for related paper {i} succeed")
            if not(inspiration.startswith("None") or (len(inspiration) < 100 and "None" in inspiration)):
                inspirations.append(inspiration)

        for i, paper in enumerate(self.paper_list):
            p = threading.Thread(target=generate_inspiration, args=(paper, i))
            processes.append(p)
            p.start()
        for p in processes:
            p.join(120)
        
        ## generate ideas through all inspirations
        logger.info("Generate inspirations for all related papers succeed")
        idea = self.api_helper.generate_idea_by_inspiration(detail_background, inspirations)
        initial_ideas = extract_ideas(idea)
        logger.info("Generate ideas from inspirations succeed")
        idea_filtered = self.api_helper.integrate_idea(detail_background, self.brainstorm, idea)
        logger.info("Idea integration succeed")

        ## expand ideas
        ideas_filtered = extract_ideas(idea_filtered)
        final_ideas = ["None"] * len(ideas_filtered)
        def expand_idea(detail_background: str, idea: str, i):
            final_ideas[i] = self.api_helper.expand_idea(detail_background, idea)
            logger.info(f"Expand the {i}th idea succeed")
        processes = []
        for i, idea in enumerate(ideas_filtered):
            p = threading.Thread(target=expand_idea, args=(detail_background, idea, i))
            processes.append(p)
            p.start()
        for p in processes:
            p.join(120)

        ## reture
        return None, None, inspirations, initial_ideas, ideas_filtered, final_ideas

    def generate(
        self,
        background: str,
        mode: str,
        bs_mode: str = None,
        use_cue_words: bool = False,
    ):
        mode_name = None
        if mode == "backtracking":
            mode_name = "Backtrack"
        elif mode == "new_idea":
            mode_name = "Generate new idea"
        if bs_mode == "mode_a":
            logger.info(
                "{} using brainstorm_mode_a without cue words.".format(mode_name)
            )
            (message_input, problem, idea, idea_filtered) = (
                self.generate_without_cue_words(background)
            )
        elif bs_mode == "mode_b" or bs_mode == "mode_c":
            logger.info(
                "{} using brainstorm_{} without cue words.".format(
                    mode_name, bs_mode
                )
            )
            (message_input, problem, idea, idea_filtered) = (
                self.generate_without_cue_words_bs(background)
            )

        idea_modified = self.api_helper.modify_idea(background, idea_filtered)
        median = {
            "problem": problem,
            "initial_idea": idea,
            "filtered_idea": idea_filtered,
        }
        return message_input, idea_modified, median

    def generate_by_inspiration(
        self,
        background: str,
        mode: str,
        bs_mode: str = None,
        use_cue_words: bool = False,
    ):
        mode_name = None
        if mode == "backtracking":
            mode_name = "Backtrack"
        elif mode == "new_idea":
            mode_name = "Generate new idea"
        if bs_mode == "mode_a":
            logger.info(
                "{} using brainstorm_mode_a without cue words.".format(mode_name)
            )
            (message_input, problem, inspirations, idea, idea_filtered) = (
                self.generate_without_cue_words_ins(background)
            )
        elif bs_mode == "mode_b" or bs_mode == "mode_c":
            logger.info(
                "{} using brainstorm_{} without cue words.".format(
                    mode_name, bs_mode
                )
            )
            (message_input, problem, inspirations, idea, idea_filtered) = (
                self.generate_without_cue_words_ins_bs(background)
            )

        idea_modified = self.api_helper.modify_idea(background, idea_filtered)
        median = {
            "problem": problem,
            "inspirations": inspirations,
            "initial_idea": idea,
            "filtered_idea": idea_filtered,
        }
        return message_input, idea_modified, median


@click.group()
@click.pass_context
def main(ctx):
    """
    Training and evaluation
    """
    print("Mode:", ctx.invoked_subcommand)


@main.command()
@click.option(
    "-c",
    "--config-path",
    default="./configs/datasets.yaml",
    type=click.File(),
    required=True,
    help="Dataset configuration file in YAML",
)
@click.option(
    "--ids-path",
    default="/data/yc/AI_Idea_Bench_2025/target_paper_data.json",
    type=click.File(),
    required=True,
    help="Input JSON file; background derived from summary fields",
)
@click.option(
    "--out-path",
    default="./assets/output_idea/",
    type=str,
    required=True,
    help="Dataset configuration file in YAML",
)
@click.option(
    "--out-file",
    default="out-file.json",
    type=str,
    required=True,
    help="Dataset configuration file in YAML",
)
@click.option(
    "-r",
    "--retriever-name",
    default="SNKG",
    type=str,
    required=True,
    help="Retrieve method",
)
@click.option(
    "--brainstorm-mode",
    default="mode_c",
    type=str,
    required=True,
    help="Choose your brainstorm mode (mode_a: no brainstorm, mode_b: brainstorm for idea generation, mode_c: brainstorm for idea generation and retrival)",
)
@click.option(
    "--use-inspiration",
    default=False,
    type=bool,
    required=True,
    help="Use inspiration in generation",
)
@click.option(
    "--expand-intermediate",
    default=False,
    type=bool,
    help="The number of data you want to process",
)
@click.option(
    "--num",
    default=100,
    type=int,
    required=False,
    help="The number of data you want to process",
)
def new_idea(
    config_path,
    ids_path,
    out_path,
    out_file,
    retriever_name,
    brainstorm_mode,
    use_inspiration,
    expand_intermediate,
    num,
    **kwargs,
):
    check_env()
    logger.add(
        "log/generate_{}_{}.log".format(time.time(), retriever_name), level="DEBUG"
    )  # 添加文件输出
    logger.info("Retrieve name: {}".format(retriever_name))
    # Configuration
    config = ConfigReader.load(config_path, **kwargs)
    api_helper = APIHelper(config)
    eval_data = []
    cur_num = 0
    data_num = 0
    batch_size = 1
    bg_ids = set()
    os.makedirs(out_path, exist_ok=True)
    output_file = os.path.join(
        out_path, out_file
    )
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            try:
                eval_data = json.load(f)
                bg_ids = {data["background"] for data in eval_data}
                cur_num = len(eval_data)
            except json.JSONDecodeError:
                eval_data = []
    logger.debug(f"{cur_num} datas have been processed.")
    all_input = json.load(ids_path)
    # 加载预处理好的引用论文数据
    merged_ref_path = "/data/liumengdi/Mindflow/data/merged_processed_target_paper_data.json"
    with open(merged_ref_path, "r", encoding="utf-8") as rf:
        merged_refs = json.load(rf)
    ref_map = {item.get("index"): item for item in merged_refs}
    for line in all_input:
        # 解析每行的JSON数据
        # data = json.loads(line)
        data = line
        ### 1. 获取背景信息
        bg = None
        if "summary" in data.keys():
            summary = data["summary"]
            if isinstance(summary, dict):
                bg = summary.get("revised_topic") or summary.get("topic")
            else:
                bg = summary
        if not bg:
            data_num += 1
            print(f"This data doesn't have background or summary topic...")
            continue
        idx = data.get("index")
        ref_entry = ref_map.get(idx)
        if ref_entry is None:
            data_num += 1
            print(f"No reference entry found for index {idx}, skip.")
            continue
        if bg in bg_ids:
            data_num += 1
            print(f"Skipping already processed data_{data_num}.")
            continue
        
        ## extract entities from background
        entities = api_helper.generate_entity_list(bg)

        ## expand background to a detailed version
        keywords_str = functools.reduce(lambda x, y: f"{x}, {y}", entities)
        expanded_background = api_helper.expand_background(bg, keywords_str)

        ## brainstorm according to the background
        if brainstorm_mode == "mode_b" or brainstorm_mode == "mode_c":
            brainstorm = api_helper.generate_brainstorm(expanded_background)
            seperate_brainstorm = extract_ideas(brainstorm)
            ## expand the brainstorms to a detailed version
            expanded_brainstorms = []
            if expand_intermediate:
                for i, sb in enumerate(seperate_brainstorm):
                    expanded_brainstorms.append(api_helper.expand_idea(expanded_background, sb))
                    logger.info(f"Expand the {i}th brainstorm succeed")
        else:
            brainstorm = None
        
        ## Extract entities from the brainstorm result
        logger.debug("Original entities from background: {}".format(entities))
        if brainstorm_mode == "mode_c":
            entities_bs = api_helper.generate_entity_list(brainstorm, 10)
            logger.debug("Original entities from brainstorm: {}".format(entities_bs))
            entities_all = list(set(entities) | set(entities_bs))
        else:
            entities_bs = None
            entities_all = entities

        ### 2. 读取相关论文（基于预处理引用）
        refs = ref_entry.get("find_cite", {}).get("top_references") or ref_entry.get("top_references", [])
        related_paper = []
        for ref in refs:
            cite_content = ref.get("cite_paper_conten", {}) or {}
            related_paper.append(
                {
                    "title": ref.get("title", ""),
                    "paper_local_path": ref.get("paper_local_path", ""),
                    "idea": cite_content.get("idea", ""),
                    "experiment": cite_content.get("experiment", ""),
                    "entities": cite_content.get("entities", ""),
                    "references": cite_content.get("references", ""),
                }
            )
        logger.info("Find {} related papers from preprocessed references.".format(len(related_paper)))
        entities_rt = []

        ### 3. 生成IDEA
        idea_generator = IdeaGenerator(config, related_paper, brainstorm)
        _, _, inspirations, initial_ideas, idea_filtered, final_ideas = idea_generator.generate_ins_bs(expanded_background)
        expanded_initial_ideas = []
        if expand_intermediate:
            for i, initial_idea in enumerate(initial_ideas):
                expanded_initial_ideas.append(api_helper.expand_idea(expanded_background, initial_idea))
                logger.info(f"Expand the {i}th initial idea succeed")
        eval_data.append(
            {
                "background": bg,
                "expanded_background": expanded_background,
                "entities_bg": entities,
                "brainstorm": brainstorm,
                "seperate_brainstorm": seperate_brainstorm,
                "entities_bs": entities_bs,
                "entities_rt": entities_rt,
                "related_paper": [p["title"] for p in related_paper],
                "inspirations": inspirations,
                "initial_ideas": initial_ideas,
                "filtered_ideas": idea_filtered,
                "expanded_final_ideas": final_ideas,
                "expanded_brainstorms": expanded_brainstorms,
                "expanded_initial_ideas": expanded_initial_ideas,
            }
        )
        cur_num += 1
        if cur_num % batch_size == 0:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(eval_data, f, ensure_ascii=False, indent=4)
        if cur_num >= num:
            break
    logger.info("=== Finish ===")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(eval_data, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
