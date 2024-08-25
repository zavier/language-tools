import os

from flask import Blueprint, request, current_app, render_template, jsonify
from langchain_community.chat_models import QianfanChatEndpoint
from langchain_core.output_parsers import SimpleJsonOutputParser, StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from app import db
from app.models import Translate, TranslateResource, TranslateAnalysis

bp = Blueprint('chat', __name__, url_prefix='/api')

model = QianfanChatEndpoint(model="ERNIE-Lite-8K-0308")
system_template = """你是一个英语老师，现在需要根据{scenario}场景下出{number}个常用的句子翻译题，要求如下：
        1. 需要你先提供对应的英文和中文，以json数组格式返回，数组中的对象只有两个key, chinese中记录中文，english中记录英文，格式样例为: [{{'chinese':'你好', 'english':'hello'}}]
        2. 如果英语句子的难度级别分为初级、中级、高级，初级表示最低难度，高级最最高难度，你提供的翻译题难度级别为{difficulty}
        3. 注意只返回json，不要返回其他任何多余的信息
        """
prompt_template = ChatPromptTemplate.from_messages(
    [("user", system_template)]
)

output_parser = SimpleJsonOutputParser()

chain = prompt_template | model | output_parser

@bp.route('/generate-sentence', methods=['POST'])
def chat():
    body = request.get_json()

    translate = Translate(scenario=body["scenario"], number=body["number"], difficulty=body["difficulty"])
    db.session.add(translate)
    db.session.commit()

    resp = chain.invoke({"scenario": body["scenario"], "number": body["number"], "difficulty": body["difficulty"]})
    current_app.logger.info('get-sentence resp: %s， type: %s', str(resp), type(resp))

    resources = [TranslateResource(source=x["chinese"], target=x["english"], translate_id=translate.id) for x in resp]
    db.session.add_all(resources)
    db.session.commit()

    return resp


@bp.route('/get-sentence-detail/<int:id>')
def get_sentence_detail(translate_id: int):
    data_list = TranslateResource.query.filter_by(translate_id=translate_id).all()
    return render_template('translate.json', data_list=data_list)


@bp.route('/submit-translation', methods=['POST'])
def submit_translation():
    data: dict[str, str] = request.get_json()

    template = """你是一个资深的英语老师，你帮我分析一下我下面翻译的内容，中文内容是:{chinese}，我翻译成的英文是:{english}
        你帮我分析一下翻译的内容是否有问题，如果有问题帮我说出具体的有问题的点以及如何改进，如果涉及语法等知识可以一并告知我
        最好也可以提供一下你翻译的内容
    """
    prompt = ChatPromptTemplate.from_messages(
        [("user", template)]
    )
    parser = StrOutputParser()
    this_chain = prompt | model | parser

    res = []
    for k, v in data.items():
        if k.startswith('source'):
            index = int(k[len('source') + 1:])

            r = this_chain.invoke({'chinese': v, 'english': data[f'target-{index}']})
            res.append({'chinese': v, 'english': data[f'target-{index}'], 'suggestion': r})

    analysis = [TranslateAnalysis(source=x['chinese'], translate=x['english'], suggestion=x['suggestion'], translate_id=0) for x in res]
    db.session.add_all(analysis)
    db.session.commit()
    return res


@bp.route('/get-translate-result/<int:translate_id>')
def get_translate_result(translate_id: int):
    data_list = TranslateAnalysis.query.filter_by(translate_id=translate_id).all()
    current_app.logger.info('get-translate-result resp: %s', str(data_list))
    return render_template('translate-result.json', res_list=data_list)