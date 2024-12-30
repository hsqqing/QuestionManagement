def generate_tags(content):
    """
    根据题目内容生成自动标签
    :param content: 题目内容
    :return: 标签列表
    """
    tags = []
    try:
        # 根据内容生成标签
        if "error" in content.lower():
            tags.append("easy_to_learn")
        if "frequent" in content.lower():
            tags.append("high_frequency")
        if "advanced" in content.lower():
            tags.append("difficult")

        if not tags:
            tags.append("general")

        return tags

    except Exception as e:
        logging.error(f"Error generating tags: {e}")
        return ["general"]  # 返回默认标签
