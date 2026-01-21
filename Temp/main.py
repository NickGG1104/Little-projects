
# -*- coding: utf-8 -*-
import re
import pandas as pd
import requests
from fb_graphql_scraper.facebook_graphql_scraper import FacebookGraphqlScraper as fb_graphql_scraper

# 移除 Excel 不接受的控制字元（保留 \n \r \t）
_ILLEGAL = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F]")

def clean_excel_text(s):
    if s is None:
        return None
    return _ILLEGAL.sub("", str(s))

# 給 requests 設定預設 timeout（避免卡到天荒地老）
_old_post = requests.post
def _post_with_timeout(*args, **kwargs):
    kwargs.setdefault("timeout", 30)  # 30 秒還沒回就放棄
    return _old_post(*args, **kwargs)
requests.post = _post_with_timeout

if __name__ == "__main__":
    facebook_user_name = "326264037018"
    facebook_user_id = "326264037018"
    days_limit = 4405
    driver_path = "/Users/tucaizhen/Downloads/chromedriver"
    # driver_path = r"C:\Users\user\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"

    print("fb_graphql_scraper =", fb_graphql_scraper)
    fb_spider = fb_graphql_scraper(driver_path=driver_path, open_browser=True)

    try:
        res = fb_spider.get_user_posts(
           fb_username_or_userid=facebook_user_id,
            days_limit=days_limit,
            display_progress=True
        )
    except Exception as e:
        print("抓取失敗：", repr(e))
        res = {}

    rows = []
    for post in res.get("data", []):
        dt = post.get("published_date")
        rows.append({
            "published_date": dt.strftime("%Y-%m-%d %H:%M:%S") if dt is not None else None,
           "context": clean_excel_text(post.get("context"))
       })

    df = pd.DataFrame(rows, columns=["published_date", "context"])

    output_path = facebook_user_name + "_facebook_posts.xlsx"
    df.to_excel(output_path, index=False)
    print(f"已寫入 Excel：{output_path}，共 {len(df)} 筆")
print("✅ Python 檔案成功執行")

