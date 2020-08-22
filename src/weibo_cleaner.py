## Code in this cell is essentially copy & pasted from Hadoop: PrepareWeiboCorpus.ipynb . 
import re, emoji
atMention_pattern  = re.compile(r'@([\u4e00-\u9fa5a-zA-Z0-9_-]{1,30})')
emoticons_pattern  = re.compile(r'\[([0-9a-zA-Z\u4e00-\u9fa5]+)\]')
topic_pattern      = re.compile(r'#([^#]+)#')
url_pattern        = re.compile(r'{LK}([a-zA-Z0-9]{5,10})')
emoji_pattern      = emoji.get_emoji_regexp()
whitespace_pattern = re.compile(r'\s+')
rtMention_pattern  = re.compile(r'^\s*@([\u4e00-\u9fa5a-zA-Z0-9_-]{1,30})\s*[:：]\s*')
markers_pattern    = re.compile(r' \{[A-Z]{2}\} ')

def mask(content):
    '''This function replaces many tokens with special tokens.'''
    # "@李名扬: 哈喽❤️~你来看看{LK}3JKS2L 这个里面有没有 @郭德纲 说的那个#宝藏#^_^。我觉得  还可以！"
    #rt_at_user     = ''.join(rtMention_pattern.findall(content))
    masked_content = rtMention_pattern.sub('', content)
    # "哈喽❤️~你来看看{LK}3JKS2L 这个里面有没有 @郭德纲 说的那个#宝藏#^_^。我觉得  还可以！"
    masked_content = whitespace_pattern.sub(' {SP} ', masked_content) # Reserve natural whitespaces
    # "哈喽❤️~你来看看{LK}3JKS2L {SP} 这个里面有没有 {SP} @郭德纲 {SP} 说的那个#宝藏#^_^。我觉得 {SP} 还可以！"
    #links          = url_pattern.findall(masked_content)
    masked_content = url_pattern.sub(' {LK} ', masked_content)
    # "哈喽❤️~你来看看 {LK}  {SP} 这个里面有没有 {SP} @郭德纲 {SP} 说的那个#宝藏#^_^。我觉得 {SP} 还可以！"
    #usernames      = atMention_pattern.findall(masked_content)
    masked_content = atMention_pattern.sub(' {AT} ', masked_content)
    # "哈喽❤️~你来看看 {LK}  {SP} 这个里面有没有 {SP}  {AT}  {SP} 说的那个#宝藏#^_^。我觉得 {SP} 还可以！"
    masked_content = emoji_pattern.sub(r' \1 ', masked_content)
    # "哈喽 ❤️ ~你来看看 {LK}  {SP} 这个里面有没有 {SP}  {AT}  {SP} 说的那个#宝藏#^_^。我觉得 {SP} 还可以！"
    #topics         = topic_pattern.findall(masked_content)
    masked_content = topic_pattern.sub(' {TP} ', masked_content)
    # "哈喽 ❤️ ~你来看看 {LK}  {SP} 这个里面有没有 {SP}  {AT}  {SP} 说的那个 {TP} ^_^。我觉得 {SP} 还可以！"
    #emoticons      = emoticons_pattern.findall(masked_content)
    masked_content = emoticons_pattern.sub(' {ET} ', masked_content)
    # "[微笑]", etc.

    return masked_content

assert mask( "@李名扬: 哈喽❤~你来看看{LK}3JKS2L 这个里面有没有 @郭德纲 说的那个#宝藏#^_^。我觉得  还可以！")=="哈喽 ❤ ~你来看看 {LK}  {SP} 这个里面有没有 {SP}  {AT}  {SP} 说的那个 {TP} ^_^。我觉得 {SP} 还可以！"
