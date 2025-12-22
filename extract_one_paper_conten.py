import os
from SementicSearcher import SementicSearcher
from prompt_template.process_one_paper import get_deep_reference_prompt
import fitz

from config import settings


def resolve_paper_path(paper_path: str) -> str:
    """将论文相对路径解析为绝对路径（基于项目根目录）"""
    if os.path.isabs(paper_path):
        return paper_path
    # 移除开头的 ./
    if paper_path.startswith("./"):
        paper_path = paper_path[2:]
    # 基于项目根目录解析
    return str(settings.paths.project_root / paper_path)


def save_first_20_pages(input_pdf_path):
    current_dir = str(settings.paths.dataset_temple_path)
    output_folder = os.path.join(current_dir, 'cutpdf')
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    file_name = os.path.basename(input_pdf_path)
    output_pdf_path = os.path.join(output_folder, file_name)

    doc = fitz.open(input_pdf_path)
    writer = fitz.open()

    if len(doc)>20:
        if os.path.exists(output_pdf_path):
            return output_pdf_path
        for page_num in range(min(20, len(doc))):
            writer.insert_pdf(doc, from_page=page_num, to_page=page_num)

        writer.save(output_pdf_path)
        return output_pdf_path
    else:
        return input_pdf_path


def get_article_idea_experiment_references_info(response):
        entities = extract(response,"entities")
        idea = extract(response,"idea")
        experiment = extract(response,"experiment")
        references = extract(response,"references")
        return idea,experiment,entities,references

def get_content_between_a_b(start_tag, end_tag, text):
    extracted_text = ""
    start_index = text.find(start_tag)
    while start_index != -1:
        end_index = text.find(end_tag, start_index + len(start_tag))
        if end_index != -1:
            extracted_text += text[start_index + len(start_tag) : end_index] + " "
            start_index = text.find(start_tag, end_index + len(end_tag))
        else:
            break

    return extracted_text.strip()


def extract(text, type):
    if text:
        target_str = get_content_between_a_b(f"<{type}>", f"</{type}>", text)
        if target_str:
            return target_str
        else:
            return text
    else:
        return ""

def get_one_paper_conten(model_api, pdf_path, topic):

    sementicsearcher = SementicSearcher()

    # 解析为绝对路径
    pdf_path = resolve_paper_path(pdf_path)
    pdf_path = save_first_20_pages(pdf_path)

    article_dict = sementicsearcher.read_arxiv_from_path(pdf_path)
    if article_dict is None:
        raise RuntimeError(f"Failed to parse PDF: {pdf_path}. Is Grobid running?")
    title, abstract, pub_data = article_dict["title"], article_dict["abstract"], article_dict["pub_date"]
    paper = Result(title,abstract,article_dict,0,pub_data)
    paper_conten = sementicsearcher.read_paper_content_with_ref(article_dict)

    prompt = get_deep_reference_prompt(paper_conten, topic)


    LLM_result = model_api(prompt)

    idea,experiment,entities,references = get_article_idea_experiment_references_info(LLM_result)

    data = {}
    data['idea'] = idea
    data['experiment'] = experiment
    data['entities'] = entities
    data['references'] = references

    return data


class Result:
    def __init__(self,title="",abstract="",article=None,citations_conut = 0,year = None) -> None:
        self.title = title
        self.abstract = abstract
        self.article = article
        self.citations_conut = citations_conut
        self.year = year



    




