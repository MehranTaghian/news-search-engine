import logging
import random
import re
import time

repetition_pattern = re.compile(r"([^A-Za-z])\1{1,}")
# debug_pattern = re.compile(r'[0-9۰۱۲۳۴۵۶۷۸۹]')
# debug_pattern = re.compile(r'^گرون$|^میدون$|^خونه$|^نون$|^ارزون$|^اون$|^قلیون$')
# debug_pattern = re.compile(r'هایمان')
debug_pattern = re.compile(r'^(.)\1{5}$')

logger = None
normalizers = {}
validators = {}
taggers = {}
token_set = set()
repetition_word_set = set()
compile_patterns = lambda patterns: [(re.compile(pattern), repl) for pattern, repl in patterns]
typographies = r'&*@‱\\/•^†‡⹋°〃=※×#÷%‰¶§‴~_\|‖¦٪'
punctuations = r'\.:!،؛?؟»\]\)\}«\[\(\{\'\…¡¿'
num_punctuations = r':!،؛?؟»\]\)\}«\[\(\{\'\…¡¿'
hashtag = r'#'
numbers = r'۰۱۲۳۴۵۶۷۸۹'
persians = 'اآب‌پتثجچحخدذرزژسشصضطظعغفقکگلمنوهی'
has_persian_character_pattern = re.compile(rf"([{persians}{numbers}])")
link = r'((https?|ftp):\/\/)?(?<!@)([wW]{3}\.)?(([a-zA-Z۰-۹0-9-]+)(\.([a-zA-Z۰-۹0-9]){2,})+([-\w@:%_\+\/~#?&=]+)?)'
emojies = r'\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F4CC\U0001F4CD'
email = r'[a-zA-Z۰-۹0-9\._\+-]+@([a-zA-Z۰-۹0-9-]+\.)+[A-Za-z]{2,}'
id = r'@[a-zA-Z_]+'
num = r'[+-]?[\d۰-۹]+'
numf = r'[+-]?[\d۰-۹,]+[\.٫,]{1}[\d۰-۹]+'
tag = r'\#([\S]+)'
nj = '‌'
# tag_set_token_tags = dict()
all_token_tags = dict()
import path
import os
from utils import load_file

if os.path.isfile(path.mohaverekhan_parsed_dir):
    # tag_set_token_tags = load_obj(path.mohaverekhan_parsed_fir)
    all_token_tags = load_file(path.mohaverekhan_parsed_dir)
    # print(all_token_tags)
else:
    # file = read_bijan_files(path.bijan_files_dir)
    # (file, path.mohaverekhan_parsed_dir)
    # # tag_set_token_tags = file
    # all_token_tags = file
    print("FILE DOES NOT EXIST")

# for t in tag_set_token_tags

is_number_pattern = re.compile(rf"^({num})|(numf)$")


###############################################################################
# باید بررسی کنیم نشانه‌های مورد نظر در مجموعه داده موجود وجود دارد یا نه
# ممکنه نشانه مورد نظر، یک نشانه بی‌نهایت باشد و یک نشانه بی‌نهایت برای ما معتبر هست.
def is_token_valid(token_content):
    # اگر نشانه عدد بود، آن را قبول و برای بهبود سرعت آن را در کش ذخیره می‌کنیم.
    if is_number_pattern.fullmatch(token_content):
        # logger.info(f'> Number found and added : {token_content}')
        # tag_set_token_tags['mohaverekhan-tag-set'][token_content] = {'U': 1}
        all_token_tags[token_content] = {'U': 1}
        return True

    # برچسب آر به معنای معتبر بودن نشانه نیست و اگر نشانه فقط برچسب آر داشت آن را معتبر نمی‌خوانیم.
    if token_content in all_token_tags and list(all_token_tags[token_content].keys()) != ['R']:
        return True

    return False
