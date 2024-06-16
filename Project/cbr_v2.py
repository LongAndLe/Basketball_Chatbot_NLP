import json
import random
from datetime import datetime
import spacy
import numpy as np

print("Chatbot: Hệ thống đang khởi động. Xin chờ 1 lát...")

# Đọc dữ liệu từ file JSON
data = json.loads(open('data.json', encoding='utf-8').read())
cbr_database = data['intents']

# Sử dụng thư viện SpaCy để xử lý ngôn ngữ và có thể chuyển đổi câu thành các vector đa chiều
nlp = spacy.load("en_core_web_sm")
# Tính toán sự tương đồng dựa trên cosin
def calculate_similarity(doc_pattern, doc_question):

    # Calculate cosine similarity between two SpaCy documents
    dot_product = doc_question.vector @ doc_pattern.vector  # Tính tích vô hướng
    norm_question = np.linalg.norm(doc_question.vector)  # Tính độ dài vector
    norm_pattern = np.linalg.norm(doc_pattern.vector)  # Tính độ dài vector

    # Kiểm tra xem độ dài của vector có khác 0 không trước khi thực hiện phép chia
    if norm_question != 0 and norm_pattern != 0:
        cosine_similarity = dot_product / (norm_question * norm_pattern)  # Tính độ tương đồng cos
    else:
        cosine_similarity = 0

    return cosine_similarity


# Tìm kiếm case có độ tương đồng cao nhất với question
def find_most_similar_case(question, database):
    most_similar_case = None
    highest_similarity = 0

    # Duyệt qua các case trong database
    for case in database:
        for pattern in case['patterns']: # Duyệt qua các pattern trong case
            doc_pattern = nlp(pattern) # Xử lý ngôn ngữ cho pattern
            doc_question = nlp(question) # Xử lý ngôn ngữ cho question
            similarity = calculate_similarity(doc_pattern, doc_question) # Tính độ tương đồng giữa pattern và question

            if similarity > highest_similarity:
                most_similar_case = case
                highest_similarity = similarity

    if highest_similarity > 0.8:  # Nếu độ tương đồng lớn hơn 0.9 thì trả về câu trả lời
        return most_similar_case
    else:
        return None # Nếu không thì trả về None để lưu câu hỏi mới vào file newdata.json


# Lưu câu hỏi mới vào file newdata.json
def save_new_intent(question, i):
    new_intent = {
        "tag": "Vấn đề mới " + str(i), # Tạo tag mới cho câu hỏi mới
        "patterns": [question],
        "responses": [""] # Tạo câu trả lời mới cho câu hỏi mới
    }

    new_data = json.loads(open('newdata.json', encoding='utf-8').read())
    new_data['intents'].append(new_intent)  # Thêm case mới vào file newdata.json

    with open('newdata.json', 'w', encoding='utf-8') as outfile: 
        json.dump(new_data, outfile, ensure_ascii=False, indent=4) 


# Hàm thêm dữ liệu được người dùng cung cấp
def add_content(new_pattern,new_response):

    # Lấy ngày tháng năm hiện tại
    ngay_thang_hien_tai = datetime.now()

    # Định dạng xâu ngày tháng năm
    xau_ngay_thang_nam = ngay_thang_hien_tai.strftime("%d/%m/%Y %H:%M:%S")
    new_intent = {
        "tag": "Thông tin được người dùng cung cấp ngày " + xau_ngay_thang_nam, # Tạo tag mới cho câu hỏi mới
        "patterns": [new_pattern], # Thêm câu hỏi người dung nhập
        "responses": [new_response] # Thêm câu trả loời người dùng nhập
    }
    new_content = json.loads(open('user_content.json', encoding='utf-8').read())
    new_content['intents'].append(new_intent)  # Thêm thông tin khách nhập vào mảng chứa thông tin

    with open('user_content.json', 'w', encoding='utf-8') as outfile:
        json.dump(new_content, outfile, ensure_ascii=False, indent=4) # Ghi thông tin mới vào file user_content.json



# Tạo mảng chứa lệnh cung cấp thông tin
lenh_cung_cap = ["tôi muốn cung cấp thông tin cho bạn", "tôi muốn cung cấp thông tin", "tôi muốn dạy cho bạn", "cung cấp thông tin cho hệ thống", "tôi muốn cung cấp thông tin cho hệ thống", "tôi muốn cung cấp câu hỏi và câu trả lời cho vấn đề mới", "tôi muốn cung cấp thông tin và câu hỏi cho tình huống mới"]


# Hàm kiểm tra khách hỏi hay cung cấp thông tin
def check_input(question):
    for lenh in lenh_cung_cap: # Duyệt các lệnh trong mảng
        if question.lower() == lenh:
            return True
    return False



i = 1

# Hàm tìm câu trả lời câu hỏi
def cbr_respond(question, database):
    global i
    similar_case = find_most_similar_case(question, database)

    if similar_case:
        return similar_case['responses'][0]
    else:
        save_new_intent(question, i)
        i += 1
        return "Tôi không thể tìm thấy câu trả lời cho câu hỏi của bạn và đã lưu câu hỏi này lại để có thể cải thiện các câu trả lời trong tương lai"

# Chào mở đầu
print('Chatbot: Xin chào! Tôi có thể cùng bạn trao đổi thông tin về môn bóng rổ.')
print('Mỗi lần bạn muốn cung cấp thông tin cho tôi hãy nhập "Tôi muốn cung cấp thông tin" hoặc nếu bạn muốn hỏi tôi gì đó hãy nhập câu hỏi!')
print('Nếu bạn muốn kết thúc trao đổi nhớ nhập lệnh "Stop"')



# Các câu in ra sau khi trả lời
ask_list = ['Bạn còn câu hỏi nào nữa không???', ':D Tiếp tục cho tôi câu hỏi nào!', 'Bạn muốn hỏi thêm về những vấn đề khác của bóng rổ chứ, tôi sẽ giúp bạn!', 'Hãy tiếp tục đưa ra câu hỏi nếu bạn còn điều gì thắc mắc, nếu bạn muốn dừng lại hãy gõ stop']
wait_list = ['Xin đợi tôi 1 lát!', 'Tôi đang suy nghĩ! Xin hãy đợi :() ', 'Xin hãy đợi!Câu trả lời sẽ có nhanh thôi!', 'Please wait...']



# Main loop
while True:
    print('Bạn: ', end='')
    question = input("") # Nhập câu hỏi
    if question.lower() == 'stop':# Nhập stop để dừng chương trình
        print('Chatbot: Hẹn gặp lại bạn sớm nhất có thể! Tôi sẽ nhớ bạn!')
        break

    # Kiểm tra người dùng đang muốn hỏi hay đang muốn cung cấp thông tin.
    elif check_input(question):
        print("Chatbot: Xin mời nhập câu hỏi hoặc tình huống bạn muốn cung cấp thông tin")
        new_pattern = input("")
        print("Chatbot: Xin mời nhập câu trả lời cho câu hỏi hoặc tình huống này")
        new_response = input("")
        add_content(new_pattern,new_response)
        print("Chatbot: Xin cảm ơn bạn đã cung cấp thêm thông tin giúp hệ thống cải thiện tốt hơn! Chúng tôi đã lưu lại thông tin")
        print("mà bạn cung cấp để chờ xét duyệt thêm vào hệ thống. Hãy tiếp tục đưa ra câu hỏi hoặc cung cấp thông tin cho tôi")
        continue

    print('Chatbot: '+ random.choice(wait_list))
    response = cbr_respond(question, cbr_database)

    # In từng đoạn có độ dài 150 ký tự trên một dòng
    
    print('Chatbot: '+ response)
    print('Chatbot: '+ random.choice(ask_list))
