### 執行方式
* Windows/Linux/macOS 通用
```bash
python -m pytest
```
* --cov src/ 在執行測試時，計算 src/ 有多少比例的程式碼有被「**測試過**」
```bash
pytest -vv --cov src/
```
* 安靜模式
```bash
python -m pytest -q
```
* 只跑名稱含 add 的測試
```bash
python -m pytest -vv -k add
```
* 產出html測試報告
```bash
python -m pytest -vv --html=reports/leetcode.html --self-contained-html
```

<hr>

* 使用 pytest 內建的 Context Switcher 可以指定「範圍內的程式碼應該要拋出何種錯誤」
```python
with pytest.raises(<錯誤型態>):
    # 此處的代碼如果沒有拋出<錯誤型態>，pytest會認為該次測試失敗
```

<hr>

#### TDD (Test Driven Development) 測試驅動開發
TDD 是一種開發方法，確保每個功能都有相關的測試用例，並且在修改現有程式碼時能夠快速發現問題，關注單元測試的設計
針對開發內容寫 Test Cases，先寫 Test Cases 再開發，開發人員按照「紅、綠、重構」的循環進行工作：先編寫會 失敗的測試 (紅)，然後編寫足夠的代碼使其 通過 (綠)，最後對程式碼進行 重構 以保持其清晰度和簡潔性。
TDD 有助於確保每個功能都有相關的測試用例，並且在修改現有代碼時能夠快速發現問題。

#### BDD (Behavior Driven Development) 行為驅動開發
BDD 是一種開發方法，強調軟體的行為和需求。
BDD 通過更自然的語言（如 Gherkin）來描述軟體的行為，幫助各個領域的利益相關者更好地理解需求。
BDD 的測試案例通常以「Given-When-Then」的結構描述：給定某種情境，當某種事件發生時，預期的結果應該是什麼。
BDD 強調團隊合作和共享對需求的理解，以確保所有人對軟體的行為都有一致的理解。
