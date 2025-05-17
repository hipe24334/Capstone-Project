# Mô tả:
Cài đặt Website trao đổi tin nhắn và dữ liệu số đa phương tiện có bảo mật thông qua các room chat.
- Người dùng khi đăng ký tài khoản thành công, sẽ được cung cấp dịch vụ tạo một cặp khóa gồm Public Key
và Private Key trên máy người.
- Người dùng mang tính tương đối với 2 vai trò người gửi và người nhận, tuy thuộc vào tính huống và hoàn
cảnh.
- Người gửi và người nhận tham gia Chatroom và xác minh nhau thông qua việc trao đổi Publickey.
- Người dùng tham gia vào các phòng chat có thể nhắn tin cho nhau và cũng có thể đính kèm tệp dữ liệu số
đa phương tiện được mã hóa và khi người gửi và nhận tải vể hay tải lên đều cần xác thức bằng Private
Key.
- Hai bên có thể trao đổi thông qua tin nhắn và có thể đính kèm tệp dữ liệu số đa phương tiện. Trong đó
người gửi sẽ thực hiện gửi file dữ liệu, file sẽ được mã hóa sử dụng AES và tạo chữ ký sử dụng RSA và SHA.
Người nhận sẽ nhận file và thực hiện giải mã sử dụng AES, giải mã chữ ký bằng RSA và xác nhận nguồn gốc
với SHA. Nếu xác nhận chữ ký 4 chính xác, thì việc gửi file mã hóa đã đúng và hoàn thành.
- Chatroom giữa 2 người sẽ có thời hạn lưu trữ là 07 ngày kể từ ngày tạo, và sẽ được tự động xóa sau khi
hết thời hạn.
# YÊU CẦU
## Yêu cầu chức năng:
- Xác thực: Tài khoản của người dùng phải hợp lệ trên hệ thống để sử dụng dịch vụ.
- Tạo khóa: Người dùng tạo cặp khóa công khai và bí mật trên máy người dùng từ dịch vụ do chương trình
cung cấp
- Lưu trữ: Dữ liệu trao đổi được lưu tạm thời chúng trong vòng 7 ngày.
- Gửi tin nhắn: Khả năng gửi văn bản, hình ảnh, video, tệp âm thanh và tệp đính kèm khác.
- Tải lên và Tải xuống: Cho phép người dùng tải lên các tệp đính kèm từ thiết bị của họ.
- Mã hóa Tệp: Mã hóa tệp đính kèm để đảm bảo an toàn và bảo mật dữ liệu.
- Thông báo: Hiển thị thông báo cho người dùng theo các kết quả thực hiện các sự kiện.
## Các thành phần chính:
- Quản lý Phiên: Đảm bảo việc quản lý phiên an toàn để ngăn chặn truy cập trái phép.
- Tương thích di động: Hỗ trợ nhiều nền tảng và thiết bị, bao gồm cả ứng dụng di động
- Tìm kiếm hiệu quả: Cung cấp khả năng tìm kiếm nhanh chóng và sát nhất với từ khóa.
- Backup và Phục hồi: Hệ thống sao lưu thường xuyên để bảo vệ dữ liệu khỏi mất mát.
- Quản lý lưu lượng người dùng: Kiểm soát và quản lý lưu lượng giúp website có thể vận hành tốt khi có số
lượng người dùng cùng lúc quá cao.
- Tích hợp Mạng xã hội: Cho phép chia sẻ nhanh từ nền tảng khác và tích hợp các dịch vụ mạng xã hội.
- Hiệu suất: Sử dụng dịch vụ lưu trữ của bên thứ 3 để tối ưu khả năng lưu trữ mà vẫn đảm bảo an toàn.
- Khả năng sử dụng: Có hướng dẫn sử dụng rõ ràng, đáng tin cậy, giao diện thân thiện với người dùng.
## Môi trường:
- Ngôn ngữ: Python, html, css, javascript
- Máy chủ: localhost Kali linux
- Database framework: Flask, Flask-Session, fakerFlask-SQLAlchemy
- Tool nhắn tin: flask_socketio, gevent, gevent-websocket
- Thư viện hỗ trợ: Pillow 9.5, Crypto
## Link Demo:
- https://www.youtube.com/watch?v=i6U7zzCyaV4&ab_channel=Skipper
