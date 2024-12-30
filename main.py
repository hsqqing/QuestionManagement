from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from classify import classify_question
from tagging import generate_tags
import json
import logging

# 初始化Flask和SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # 使用SQLite数据库
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 日志配置
logging.basicConfig(level=logging.DEBUG)

# 数据库模型定义
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)  # 题目文本
    type = db.Column(db.String(50), nullable=False)  # 题目类型
    subject = db.Column(db.String(50), nullable=False)  # 科目
    difficulty = db.Column(db.String(50), nullable=False)  # 难度
    options = db.Column(db.Text, nullable=False)  # 选项
    answer = db.Column(db.String(10), nullable=False)  # 正确答案
    tags = db.Column(db.String(200), nullable=True)  # 标签
    knowledge_point = db.Column(db.String(100), nullable=True)  # 知识点

    def to_dict(self):
        """将Question对象转换为字典格式返回"""
        return {
            'id': self.id,
            'text': self.text,
            'type': self.type,
            'subject': self.subject,
            'difficulty': self.difficulty,
            'options': eval(self.options),  # 将字符串形式的字典转换为字典
            'answer': self.answer,
            'tags': self.tags.split(',') if self.tags else [],
            'knowledge_point': self.knowledge_point
        }

# 在第一次请求时创建数据库
@app.before_first_request
def create_tables():
    try:
        db.create_all()
        logging.info("Database tables created successfully.")
    except Exception as e:
        logging.error(f"Error creating tables: {e}")
        abort(500)

# 1. 题目录入接口
@app.route('/api/submit_question', methods=['POST'])
def submit_question():
    try:
        data = request.json
        # 检查输入数据是否完整
        if not all(key in data for key in ['text', 'type', 'subject', 'difficulty', 'options', 'answer']):
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields'
            }), 400

        options = str(data['options'])  # 将选项转为字符串存储

        # 添加题目到数据库
        question = Question(
            text=data['text'],
            type=data['type'],
            subject=data['subject'],
            difficulty=data['difficulty'],
            options=options,
            answer=data['answer'],
        )
        db.session.add(question)
        db.session.commit()

        logging.info(f"New question added with ID: {question.id}")

        return jsonify({
            'status': 'success',
            'message': 'Question submitted successfully',
            'question_id': question.id
        }), 201

    except Exception as e:
        logging.error(f"Error submitting question: {e}")
        return jsonify({
            'status': 'error',
            'message': f"Failed to submit question: {str(e)}"
        }), 500

# 2. 题目分类接口
@app.route('/api/classify_question', methods=['POST'])
def classify_question_api():
    try:
        data = request.json
        if 'question_id' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing question_id'
            }), 400
        
        question_id = data['question_id']
        question = Question.query.get_or_404(question_id)

        # 使用BERT模型分类题目
        classification = classify_question(question.text)

        logging.info(f"Classified question ID {question_id}: {classification}")

        return jsonify({
            'status': 'success',
            'classification': classification
        })

    except Exception as e:
        logging.error(f"Error classifying question: {e}")
        return jsonify({
            'status': 'error',
            'message': f"Failed to classify question: {str(e)}"
        }), 500

# 3. 添加标签接口
@app.route('/api/tag_question', methods=['POST'])
def tag_question():
    try:
        data = request.json
        if 'question_id' not in data or 'tags' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Missing question_id or tags'
            }), 400

        question_id = data['question_id']
        tags = data['tags']
        question = Question.query.get_or_404(question_id)

        # 将标签存储为逗号分隔的字符串
        question.tags = ','.join(tags)
        db.session.commit()

        logging.info(f"Tags {tags} added to question ID {question_id}")

        return jsonify({
            'status': 'success',
            'message': 'Tags added successfully',
            'tags': tags
        })

    except Exception as e:
        logging.error(f"Error tagging question: {e}")
        return jsonify({
            'status': 'error',
            'message': f"Failed to add tags: {str(e)}"
        }), 500

# 4. 检索题目接口
@app.route('/api/get_question', methods=['GET'])
def get_question():
    try:
        question_id = request.args.get('question_id', type=int)
        if not question_id:
            return jsonify({
                'status': 'error',
                'message': 'Missing question_id parameter'
            }), 400

        question = Question.query.get_or_404(question_id)

        return jsonify({
            'status': 'success',
            'question': question.to_dict()
        })

    except Exception as e:
        logging.error(f"Error retrieving question: {e}")
        return jsonify({
            'status': 'error',
            'message': f"Failed to retrieve question: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
