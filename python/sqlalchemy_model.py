# coding: utf8
# 把 MySQL 建表语句转换成 sqlalchemy 库要求的 model


import re
from datetime import datetime


name_pattern = re.compile(r'`(?P<name>\w+)`')
type_pattern = re.compile(r'` +(?P<type_desc>\w+(\(\d+\))?)')
default_pattern = re.compile(
    r'default (?P<default_value>\w+|[\'"][^\'"]*[\'"])[ ,]')

type_map = {
    'int': 'Integer',
    'tinyint': 'SmallInteger',
    'smallint': 'SmallInteger',
    'mediumint': 'SmallInteger',
    'bigint': 'BigInteger',
    'float': 'Float',
    'double': 'Float',
    'char': 'String',
    'varchar': 'String',
    'text': 'Text',
    'tinytext': 'String',
    'mediumtext': 'String',
    'longtext': 'String',
    'date': 'Date',
    'datetime': 'DateTime',
    'timestamp': 'DateTime',
}


def get_name(line):
    """
    :type line: str
    """
    name = re.search(name_pattern, line).group('name')
    return name, ''.join(word.capitalize() for word in name.split('_'))


def convert(create_sql):
    """
    :type create_sql: str
    :rtype: str
    """
    result = [
        'import datetime\n\n',
        'from sqlalchemy import Column, Integer, SmallInteger, BigInteger, Float, String, Text, '
        'Date, DateTime\n',
        'from sqlalchemy.ext.declarative import declarative_base\n\n',
        'Base = declarative_base()\n\n\n']
    for line in create_sql.splitlines():
        line = line.strip(' \t\n')
        line = line.lower()
        if not line:
            continue
        elif 'create table' in line:
            name, cls_name = get_name(line)
            result.append('class {cls}(Base):\n'.format(cls=cls_name))
            result.append("    __tablename__ = '{name}'\n".format(name=name))
            day = datetime.now().strftime('%Y-%m-%d')
            result.append(
                "    __model_version__ = '{date}'\n\n".format(date=day))
        elif line.startswith('`'):
            name = re.search(name_pattern, line).group('name')
            type_desc = re.search(type_pattern, line).group('type_desc')
            type_name = type_desc[:type_desc.index(
                '(')] if '(' in type_desc else type_desc
            type_value = type_desc[type_desc.index(
                '('):] if '(' in type_desc else ''
            code_line = '    {name} = Column({type}{type_value})\n'.format(
                name=name, type=type_map[type_name], type_value=type_value)
            if name == 'id':
                code_line = code_line[::-1].replace(')',
                                                    ', primary_key=True)'[::-1], 1)[::-1]
            default_desc = get_default_desc(line)
            if default_desc:
                code_line = code_line[::-
                                      1].replace(')', default_desc[::-1], 1)[::-1]
            result.append(code_line)
        else:
            break
    print(''.join(result))
    return ''.join(result)


def get_default_desc(line):
    """
    :type line: str
    :rtype: str
    """
    default_match = re.search(default_pattern, line)
    if not default_match:
        return ''
    default_value = default_match.group('default_value')
    default_value = default_value.strip('\'"')
    if default_value == 'current_timestamp':
        return ', default=datetime.datetime.now)'
    try:
        default_value = int(default_value)
        return ', default={0})'.format(default_value)
    except ValueError:
        return ", default='{0}')".format(default_value)


if __name__ == '__main__':
    create_sql = '''
        CREATE TABLE `game_v` (
          `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '自增id, 无实际意义',
          `app_type` tinyint(4) NOT NULL DEFAULT '0' COMMENT '大v对应的平台 0: 头条, 1: 段子, 2: 抖音, 3: 火山, 4: 西瓜',
          `user_id` bigint(20) NOT NULL COMMENT '大v用户id',
          `user_name` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '' COMMENT '大v用户name',
          `game_id` bigint(20) NOT NULL COMMENT '游戏大v属于的游戏id',
          `game` varchar(64) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '' COMMENT '游戏名',
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='运营手动找的游戏大v';
    '''
    convert(create_sql)
