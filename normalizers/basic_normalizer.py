# from models.base_models import Normalizer
from normalizers import cache


class MohaverekhanBasicNormalizer():

    ###############################################################################
    # باید کاراکتر‌ها را یکسان کنیم تا چندین نشانه یکسان با نگارش متفاوت نداشته باشیم.
    # مثلا فرض کنید در نشانه علیرضا اصلا معلوم نیست از «ی» و یا «ي» استفاده شده‌است.

    translation_characters = (
        (r'0', r'۰', '', 'hazm', 'true'),
        (r'1', r'۱', '', 'hazm', 'true'),
        (r'2', r'۲', '', 'hazm', 'true'),
        (r'3', r'۳', '', 'hazm', 'true'),
        (r'4', r'۴', '', 'hazm', 'true'),
        (r'5', r'۵', '', 'hazm', 'true'),
        (r'6', r'۶', '', 'hazm', 'true'),
        (r'7', r'۷', '', 'hazm', 'true'),
        (r'8', r'۸', '', 'hazm', 'true'),
        (r'9', r'۹', '', 'hazm', 'true'),

        (r'٠', r'۰', '', 'mohaverekhan', 'true'),
        (r'١', r'۱', '', 'mohaverekhan', 'true'),
        (r'٢', r'۲', '', 'mohaverekhan', 'true'),
        (r'٣', r'۳', '', 'mohaverekhan', 'true'),
        (r'٤', r'۴', '', 'mohaverekhan', 'true'),
        (r'٥', r'۵', '', 'mohaverekhan', 'true'),
        (r'٦', r'۶', '', 'mohaverekhan', 'true'),
        (r'٧', r'۷', '', 'mohaverekhan', 'true'),
        (r'٨', r'۸', '', 'mohaverekhan', 'true'),
        (r'٩', r'۹', '', 'mohaverekhan', 'true'),

        (r' ', r' ', 'space character 160 -> 32', 'hazm', 'true'),
        (r'ك', r'ک', '', 'hazm', 'true'),
        (r'ي', r'ی', '', 'hazm', 'true'),
        (r'ئ', r'ی', '', 'hazm', 'true'),
        (r'ؤ', r'و', '', 'hazm', 'true'),
        (r'إ', r'ا', '', 'mohaverekhan', 'true'),
        (r'أ', r'ا', '', 'mohaverekhan', 'true'),
        (r'ة', r'ه', '', 'mohaverekhan', 'true'),
        (r'“', r'"', '', 'hazm', 'true'),
        (r'”', r'"', '', 'hazm', 'true'),
        (r'%', r'٪', '', 'mohaverekhan', 'true'),
        (r'?', r'؟', '', 'mohaverekhan', 'true'),
        # (r'آ', r'ا', '', 'mohaverekhan', 'true'),
        # (r'هٔ', r'ه', '', 'hazm', 'true'),
    )

    translation_characters = {tc[0]: tc[1] for tc in translation_characters}

    def uniform_signs(self, text_content):
        text_content = text_content.translate(text_content.maketrans(self.translation_characters))
        text_content = text_content.strip(' ')
        return text_content

    ###############################################################################
    # یک سری از کاراکتر‌های دیگر باید حذف و یا جایگزین بشن، در این قسمت با رگس آن را انجام می‌دهیم.
    basic_patterns = (
        # extract hashtag content
        (r'_', r' '),
        (r'#(\w+)', r'\1'),
        # حذف فتحه و کسره و غیره

        (r'[\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652]', r'',
         'remove FATHATAN, DAMMATAN, KASRATAN, FATHA, DAMMA, KASRA, SHADDA, SUKUN', 0, 'hazm', 'true'),
        # حذف کشیده
        (r'[ـ\r]', r'', r'remove keshide, \r', 0, 'hazm', 'true'),
        # حذف همزه‌ی مستقل بالای حروف
        (r'ٔ', r'', r'remove  ٔ ', 0, 'mohaverekhan', 'true'),
        # جایگزین کردن سه نقطه با علامت آن
        (r'([^\.]|^)(\.\.\.)([^\.]|$)', r'\1…\3', 'replace 3 dots with …', 0, 'mohaverekhan', 'true'),
        # حذف تکرار علامت سوال و تعجب و نقطه و غیره
        (rf'([{cache.punctuations}])\1+', r'\1', 'remove cache.punctuations repetitions', 0, 'mohaverekhan', 'true'),
        # فارسی سازی نقل قول انگلیسی با فارسی
        # (r'"([^\n"]+)"', r'«\1»', 'replace quotation with gyoome', 0, 'hazm', 'true'),
        # حذف اینتر‌های زائد
        (r'\n+', r'\n', 'remove extra newlines', 0, 'mohaverekhan', 'true'),
        # حذف فاصله‌های زائد
        (r' +', r' ', 'remove extra spaces', 0, 'hazm', 'true'),
    )

    basic_patterns = [(p[0], p[1]) for p in basic_patterns]

    basic_patterns = cache.compile_patterns(basic_patterns)

    def do_basic_patterns(self, text_content):


        for pattern, replacement in self.basic_patterns:
            text_content = pattern.sub(replacement, text_content)
            # self.logger.info(f'> After {pattern} -> {replacement} : \n{text_content}')
        text_content = text_content.strip(' ')
        return text_content

    ###############################################################################
    # تابع شروع کننده این نرمالایزر
    def normalize(self, text_content):
        import re
        # self.logger.info(f'>>> mohaverekhan-basic-normalizer : \n{text_content}')
        dummy_thing = 'UNnDeRlInEe'
        max_cnt = 0

        text_content = text_content.strip(' ')

        text_content = self.uniform_signs(text_content)
        # self.logger.info(f'>> uniform_signs : \n{text_content}')

        text_content = self.do_basic_patterns(text_content)
        # self.logger.info(f'>> do_basic_patterns : \n{text_content}')

        text_content = text_content.strip(' ')
        # return clean.clean_text(text_content)
        return text_content
