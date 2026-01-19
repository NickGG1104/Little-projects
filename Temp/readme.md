### 結論
* 這個套件作者很屌，逆向工程找到API跟token直接抓PO文。
* 只要修該原始套件(facebook_graphql_scraper.py)，在每次requests後隨機等待5~15秒再做下次請求，模擬正常人的請求速度避免被鎖IP。
* 重點在這個：time.sleep(random.uniform(5, 15))。
* 雖然會跑超級慢但至少不會被鎖，不過我只改未登入模式。
* 有使用登入模式的話要改 get_user_posts 裡面的 scroll 迴圈，pause(0.7) -> pause(random.uniform(5, 15))。
#### Step 1. 在 cmd 輸入 pip show pkg_name 找到套件存放路徑
```cmd
pip show facebook_graphql_scraper
```
* 通常會在這 "C:\Users\AppData\Local\Programs\Python\Python313\Lib\site-packages\fb_graphql_scraper"

#### Step 2. 打開 facebook_graphql_scraper.py import random 套件
```python
import random
```

#### Step 3. 將 requests_flow 函式覆蓋存檔
```python
def requests_flow(self, doc_id:str, fb_username_or_userid:str, days_limit:int, profile_feed:list, display_progress=True):
    """
    Fetch more posts from a user's Facebook profile using the requests module.

    Flow:
        1. Get the document ID of the target Facebook profile.
        2. Use the requests module to fetch data from the profile.
        3. Continuously fetch data by checking for new posts until the specified days limit is reached.

    Args:
        doc_id (str): The document ID of the target Facebook account.
        fb_username_or_userid (str): The Facebook username or user ID of the target account.
        days_limit (int): The number of days for which to fetch posts (limits the time range of retrieved posts).
        profile_feed (list): A list containing the posts retrieved from the target profile.

    Helper Functions:
        1. get_before_time:
            Retrieves Facebook posts from a specified time period before the current date.

        2. get_payload:
            Prepares the payload for the next round of requests to the server.

        3. get_next_page_status:
            Checks whether the target Facebook user has more posts available for retrieval.

        4. compare_timestamp:
            Verifies whether a retrieved post falls within the specified time period for collection.
    """

    url = "https://www.facebook.com/api/graphql/"
    before_time = get_before_time()
    loop_limit = 5000
    is_first_time = True
    # Extract data
    for i in range(loop_limit):
        if is_first_time:
            payload_in = get_payload(
                doc_id_in=doc_id, 
                id_in=fb_username_or_userid, 
                before_time=before_time
            )
            is_first_time = False
            
        # if not the first tiime send request, use function 'get_next_payload' for extracting end cursor to scrape next round
        elif not is_first_time:
            next_cursor = get_next_cursor(body_content_in=body_content)
            payload_in = get_next_payload(
                doc_id_in=doc_id, 
                id_in=fb_username_or_userid, 
                before_time=before_time, # input before_time
                cursor_in=next_cursor
            )

        print(f'正在執行第 {i + 1} 次請求...')
        response = requests.post(
            url=url, 
            data=payload_in,
        )
        body = response.content
        decoded_body = body.decode("utf-8")
        body_content = decoded_body.split("\n")
        self.requests_parser.parse_body(body_content=body_content)

        # Check progress
        next_page_status = get_next_page_status(body_content=body_content)
        
        before_time = str(self.requests_parser.creation_list[-1])
        if not next_page_status:
            print("There are no more posts.")
            break
        
        # date_object = int(datetime.strptime(before_time, "%Y-%m-%d"))
        if compare_timestamp(timestamp=int(before_time), days_limit=days_limit, display_progress=display_progress):
            print(f"The scraper has successfully retrieved posts from the past {str(days_limit)} days.")
            break

        time.sleep(random.uniform(5, 15))

    res_out = self.requests_parser.collect_posts()
    new_reactions = self.process_reactions(res_in=res_out)
    # create result
    final_res = self.format_data(
        res_in=res_out, 
        fb_username_or_userid=fb_username_or_userid, 
        new_reactions=new_reactions
    )
    return {
        "fb_username_or_userid": fb_username_or_userid,
        "profile": profile_feed,
        "data": final_res,
    }
```
