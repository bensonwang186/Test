from System import systemDefine


class appLocaleData(object):
    cs_CZ = "cs_CZ"
    de_DE = "de_DE"
    en_US = "en_US"
    es_ES = "es_ES"
    fr_FR = "fr_FR"
    hu_HU = "hu_HU"
    it_IT = "it_IT"
    ja_JP = "ja_JP"
    pl = "pl"
    ru = "ru"
    sl = "sl"
    zh_CN = "zh_CN"
    zh_TW = "zh_TW"

    en_US_website_url = "https://www.cyberpowersystems.com/support/"
    en_US_products_url = "https://www.cyberpowersystems.com/products/"
    en_US_contacts_url = "https://www.cyberpowersystems.com/company/contact/"
    en_US_privacy_url = "https://www.cyberpower.com/global/en/policy/privacy"
    en_US_terms_url = "https://www.cyberpower.com/global/en/policy/terms"

    de_DE_website_url = "https://www.cyberpower.com/de/de"
    de_DE_products_url = "https://www.cyberpower.com/de/de"
    de_DE_contacts_url = "https://www.cyberpower.com/de/de/company/worldwide"
    de_DE_privacy_url = "https://www.cyberpowersystems.de/datenschutz.html"
    de_DE_terms_url = "https://www.cyberpowersystems.de/agb.html"

    ja_JP_website_url = "https://www.cyberpower.com/jp/ja"
    ja_JP_products_url = "https://www.cyberpower.com/jp/ja"
    ja_JP_contacts_url = "https://www.cyberpower.com/jp/ja/company/worldwide"
    ja_JP_privacy_url = "https://www.cyberpower.com/jp/ja/policy/privacy"
    ja_JP_terms_url = "https://www.cyberpower.com/jp/ja/policy/terms"

    es_ES_website_url = "https://www.cyberpower.com/eu/es"
    es_ES_products_url = "https://www.cyberpower.com/eu/es"
    es_ES_contacts_url = "https://www.cyberpower.com/eu/es/company/worldwide"
    es_ES_privacy_url = "https://www.cyberpower.com/eu/es/policy/privacy"
    es_ES_terms_url = "https://www.cyberpower.com/eu/es/policy/terms"

    cs_CZ_website_url = "https://www.cyberpower.com/eu/cs"
    cs_CZ_products_url = "https://www.cyberpower.com/eu/cs"
    cs_CZ_contacts_url = "https://www.cyberpower.com/eu/cs/company/worldwide"
    cs_CZ_privacy_url = "https://www.cyberpower.com/eu/cs/policy/privacy"
    cs_CZ_terms_url = "https://www.cyberpower.com/eu/cs/policy/terms"

    pl_website_url = "https://www.cyberpower.com/eu/pl"
    pl_products_url = "https://www.cyberpower.com/eu/pl"
    pl_contacts_url = "https://www.cyberpower.com/eu/pl/company/worldwide"
    pl_privacy_url = "https://www.cyberpower.com/eu/pl/policy/privacy"
    pl_terms_url = "https://www.cyberpower.com/eu/pl/policy/terms"



class appLocaleRecorder(systemDefine.Singleton):
    appLocale = appLocaleData.en_US


class appLocaleRecorderFromDB(systemDefine.Singleton):
    appLocale = appLocaleData.en_US

