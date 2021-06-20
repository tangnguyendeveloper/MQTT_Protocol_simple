# ĐỒ ÁN CUỐI KỲ NHÓM 3 --- LỚP NT106.L21.MMCL

## DANH SÁCH THÀNH VIÊN

| MSSV          | Họ Và Tên           | Nhiệm vụ         |
| ------------- | ------------------- | ---------------- |
| 19522181      | NGUYỄN TÂN TẠNG     | Code Broker      |
| 19521675      | ĐỖ HOÀNG MAI KHANH  | Code MQTTClient  |
| 19522470      | NGUYỄN LÊ ANH TUẤN  | Code Client      |

## CÀI ĐẶT MÔI TRƯỜNG

- Python 3.8.5 hoặc mới hơn
- Cài đặt các thư viện
  1.  pip install asyncio 
  2. Ubuntu
    -  sudo apt-get install build-essential pypy-dev 
    -  pip install pycryptodome 
    -  pypy -m Cryptodome.SelfTest 
    -  [Installation documentation link](https://pycryptodome.readthedocs.io/en/latest/src/installation.html)
  3. Windows
    -  Download Build Tools for Visual Studio 2019. In the installer, select the C++ build tools, the Windows 10 SDK, and the latest version of MSVC v142 x64/x86 build tools.
    -  pip install pycryptodome --no-binary :all: 
    -  python -m Cryptodome.SelfTest (Có thể bỏ qua)
    -  [Installation documentation link](https://pycryptodome.readthedocs.io/en/latest/src/installation.html)
  4. Cài đặt Kivy và môi trường ảo
    -  [Installing Kivy](https://kivy.org/doc/stable/gettingstarted/installation.html)
    -  [Youtube - Installing Kivy on Windows](https://www.youtube.com/watch?v=dLgquj0c5_U)



## CẤU TRÚC GÓI TIN

| Type (1 byte)    | length fist (2 byte) | length second (2 byte) |  n bytes      | m byte       |
| ---------------- | -------------------- | ---------------------- | ------------- | ------------ |
| SEND_KEY         | length public key    | 0                      | public key    | N/A          |
| CONNECT          | length name          | length public key      | name          | public key   |
| RECONNECT        | length name          | 0                      | name          | N/A          |
| PUBLISH          | length topic         | length data            | topic         | data         |
| SECURITY_PUBLISH | length topic         | length data            | topic encrypt | data encrypt |
| SUBSCRIBE        | length name          | length list topic      | name          | list topic   |
