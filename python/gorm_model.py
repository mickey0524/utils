# coding: utf8
# 把 MySQL 建表语句转换成 gorm 库要求的 model

import re


name_pattern = re.compile(r'`(?P<name>\w+)`')
type_pattern = re.compile(r'` +(?P<type_desc>\w+(\(\d+\))?)')
default_pattern = re.compile(
    r'default (?P<default_value>\w+|[\'"][^\'"]*[\'"])[ ,]')

type_map = {
    'int': 'int32',
    'tinyint': 'int8',
    'smallint': 'int16',
    'mediumint': 'int32',
    'bigint': 'int64',
    'float': 'float64',
    'double': 'float64',
    'char': 'string',
    'varchar': 'string',
    'text': 'string',
    'tinytext': 'string',
    'mediumtext': 'string',
    'longtext': 'string',
    'date': 'time.Time',
    'datetime': 'time.Time',
    'timestamp': 'time.Time',
}


def get_name(line):
    name = re.search(name_pattern, line).group('name')
    return name, ''.join(word.capitalize() for word in name.split('_'))


def convert(create_sql):
    """
    :type create_sql: str
    :rtype: str
    """
    result = []
    for line in create_sql.splitlines():
        line = line.strip(' \t\n')
        if not line:
            continue
        elif 'create table' in line.lower():
            table, model_name = get_name(line)
            result.append('type {0} struct {{\n'.format(model_name))
        elif line.startswith('`'):
            raw_name, go_name = get_name(line)
            result.append('    ' + go_name.ljust(20, ' '))
            type_desc = re.search(type_pattern, line).group('type_desc')
            type_name = type_desc[:type_desc.index(
                '(')] if '(' in type_desc else type_desc
            go_type = type_map[type_name.lower()].ljust(12, ' ')
            # if 'unsigned' in line.lower():
            #     go_type = 'u' + go_type[:-1]
            result.append(
                go_type + '`gorm:"type:{0};column:{1}"`\n'.format(type_desc, raw_name))
        else:
            result.append('}\n\n')
            break
    result.append('func ({0} *{0}) TableName() string {{\n    return "{1}"\n}}\n'.format(model_name,
                                                                                         table))
    print(''.join(result))
    return ''.join(result)


if __name__ == '__main__':
    create_sql = """
        CREATE TABLE `game_reserve` (
        `id`          BIGINT UNSIGNED NOT NULL  AUTO_INCREMENT,
        `game_id`     BIGINT          NOT NULL,
        `device_id`   BIGINT          NOT NULL  DEFAULT 0,
        `user_id`     BIGINT          NOT NULL  DEFAULT 0,
        `app_type`    TINYINT         NOT NULL  DEFAULT 0 COMMENT '0: 头条 1: 段子 2: 抖音 3: 火山 4: 西瓜',
        `create_time` TIMESTAMP       NOT NULL  DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (`id`),
        KEY `idx_game_id` (`game_id`),
        KEY `idx_did_uid_app` (`device_id`, `user_id`, `app_type`)
        ) ENGINE = InnoDB DEFAULT CHARSET = utf8;
    """
    convert(create_sql)
